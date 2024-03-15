// Copyright 2010, Shuo Chen.  All rights reserved.
// http://code.google.com/p/muduo/
//
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.

// Author: Shuo Chen (chenshuo at chenshuo dot com)

#include "muduo/net/poller/PollPoller.h"

#include "muduo/base/Logging.h"
#include "muduo/base/Types.h"
#include "muduo/net/Channel.h"

#include <assert.h>
#include <errno.h>
#include <poll.h>

using namespace muduo;
using namespace muduo::net;

PollPoller::PollPoller(EventLoop *loop)
    : Poller(loop)
{
}

PollPoller::~PollPoller() = default;

Timestamp PollPoller::poll(int timeoutMs, ChannelList *activeChannels)
{
  // XXX pollfds_ shouldn't change
  // 其实就是对已经注册的通道进行poll。返回可以用的通道数
  // 你把他看成epoll_wait
  // 这个是Poller的特点，触发了事件需要你从头到尾遍历一遍
  int numEvents = ::poll(&*pollfds_.begin(), pollfds_.size(), timeoutMs);
  int savedErrno = errno;
  Timestamp now(Timestamp::now());
  if (numEvents > 0)
  {
    // 这里发现有事件可以用
    // 马上来取出这些事件激活管道
    LOG_TRACE << numEvents << " events happened";
    fillActiveChannels(numEvents, activeChannels);
  }
  else if (numEvents == 0)
  {
    LOG_TRACE << " nothing happened";
  }
  else
  {
    if (savedErrno != EINTR)
    {
      errno = savedErrno;
      LOG_SYSERR << "PollPoller::poll()";
    }
  }
  return now;
}

void PollPoller::fillActiveChannels(int numEvents,
                                    ChannelList *activeChannels) const
{
  for (PollFdList::const_iterator pfd = pollfds_.begin();
       pfd != pollfds_.end() && numEvents > 0; ++pfd)
  {
    if (pfd->revents > 0)
    {
      // 有返回的事件
      --numEvents;
      ChannelMap::const_iterator ch = channels_.find(pfd->fd);
      assert(ch != channels_.end());
      Channel *channel = ch->second;
      assert(channel->fd() == pfd->fd);
      // 将返回来的事件填进管道去
      channel->set_revents(pfd->revents);
      // pfd->revents = 0;
      // 将管道放入管道列表
      activeChannels->push_back(channel);
    }
  }
}

void PollPoller::updateChannel(Channel *channel)
{
  // 用来注册或者更新通道
  // 这里就会把你关注的事件放到channelMap里面去
  // 每次都会看一下是否是跨线程调用
  Poller::assertInLoopThread();
  LOG_TRACE << "fd = " << channel->fd() << " events = " << channel->events();
  if (channel->index() < 0)
  {
    // 这是一个新的通道
    // 将这个新的通道，放到通道队列的最后面去
    //  a new one, add to pollfds_
    assert(channels_.find(channel->fd()) == channels_.end());
    struct pollfd pfd;
    pfd.fd = channel->fd();
    pfd.events = static_cast<short>(channel->events());
    pfd.revents = 0;
    pollfds_.push_back(pfd);
    int idx = static_cast<int>(pollfds_.size()) - 1;
    // 新的通道，给channel分配的index是通道List最后一个
    channel->set_index(idx);
    // 我们关注的map列表也给添加上
    // 这里你注意，channels_是父类有的，是我们关注的
    // pollfds_放的东西是Poller监听的，实际的fd
    channels_[pfd.fd] = channel;
  }
  else
  {
    // update existing one
    assert(channels_.find(channel->fd()) != channels_.end());
    assert(channels_[channel->fd()] == channel);
    int idx = channel->index();
    assert(0 <= idx && idx < static_cast<int>(pollfds_.size()));
    // 这里的pollfd是找出来的，上面是新创建的
    struct pollfd &pfd = pollfds_[idx];
    assert(pfd.fd == channel->fd() || pfd.fd == -channel->fd() - 1);
    pfd.fd = channel->fd();
    pfd.events = static_cast<short>(channel->events());
    pfd.revents = 0;
    if (channel->isNoneEvent())
    {
      // 不关注事件，不将channel移除，而是将文件描述符设置成-1
      // channel的文件描述符没有变，变的是Poller监听的文件描述符
      //  ignore this pollfd
      // 必定是负数，-1是为了避免0
      pfd.fd = -channel->fd() - 1;
    }
  }
}

void PollPoller::removeChannel(Channel *channel)
{
  // 删除指定的channel
  Poller::assertInLoopThread();
  LOG_TRACE << "fd = " << channel->fd();
  assert(channels_.find(channel->fd()) != channels_.end());
  assert(channels_[channel->fd()] == channel);
  // 看到没必须没有关注的事件了，你才能移除这个通道
  assert(channel->isNoneEvent());
  int idx = channel->index();
  assert(0 <= idx && idx < static_cast<int>(pollfds_.size()));
  const struct pollfd &pfd = pollfds_[idx];
  (void)pfd;
  assert(pfd.fd == -channel->fd() - 1 && pfd.events == channel->events());
  size_t n = channels_.erase(channel->fd());
  assert(n == 1);
  (void)n;
  // 这里还分移除最后一个和非组后一个，算法优化
  if (implicit_cast<size_t>(idx) == pollfds_.size() - 1)
  {
    pollfds_.pop_back();
  }
  else
  {
    // 将最后一个元素和移除的元素交换，然后在popback
    // 注意要修改channel的序号属性
    int channelAtEnd = pollfds_.back().fd;
    iter_swap(pollfds_.begin() + idx, pollfds_.end() - 1);
    // 这里注意有可能和你交换的哪一个的fd是不关注事件的fd
    if (channelAtEnd < 0)
    {
      // 获得真实的fd
      channelAtEnd = -channelAtEnd - 1;
    }
    // 原本序号时最后一个，现在不是最后一个了
    channels_[channelAtEnd]->set_index(idx);
    pollfds_.pop_back();
  }
}
