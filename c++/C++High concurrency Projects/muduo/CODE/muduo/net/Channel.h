// Copyright 2010, Shuo Chen.  All rights reserved.
// http://code.google.com/p/muduo/
//
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.

// Author: Shuo Chen (chenshuo at chenshuo dot com)
//
// This is an internal header file, you should not include this.

#ifndef MUDUO_NET_CHANNEL_H
#define MUDUO_NET_CHANNEL_H

#include "muduo/base/noncopyable.h"
#include "muduo/base/Timestamp.h"

#include <functional>
#include <memory>

namespace muduo
{
  namespace net
  {

    class EventLoop;
    // 这个类是不拥有文件描述符的（意思是对这个文件描述符没有管理权限）
    // 文件描述符在socket类里面放着
    // an eventfd, a timerfd, or a signalfd

    ///
    /// A selectable I/O channel.
    ///
    /// This class doesn't own the file descriptor.
    /// The file descriptor could be a socket,
    /// an eventfd, a timerfd, or a signalfd
    class Channel : noncopyable
    {
    public:
      // 事件的回调处理
      typedef std::function<void()> EventCallback;
      // 读事件的回调处理（需要多传递一个事件戳）
      typedef std::function<void(Timestamp)> ReadEventCallback;

      // 一个channel只能由一个eventloop负责
      Channel(EventLoop *loop, int fd);
      ~Channel();

      // 这个函数来决定来调用哪一些回调函数
      void handleEvent(Timestamp receiveTime);
      // 下面都是一些回调函数的注册，读写等回调函数
      void setReadCallback(ReadEventCallback cb)
      {
        readCallback_ = std::move(cb);
      }
      void setWriteCallback(EventCallback cb)
      {
        writeCallback_ = std::move(cb);
      }
      void setCloseCallback(EventCallback cb)
      {
        closeCallback_ = std::move(cb);
      }
      void setErrorCallback(EventCallback cb)
      {
        errorCallback_ = std::move(cb);
      }

      /// Tie this channel to the owner object managed by shared_ptr,
      /// prevent the owner object being destroyed in handleEvent.
      void tie(const std::shared_ptr<void> &);

      // 这个fd就是channel所对应的文件描述符
      int fd() const { return fd_; }
      // 文件描述符注册的事件（读 写  错误）
      int events() const { return events_; }
      // 实际给你返回了什么事件（你关注了好几个，可能实际返回了其中的一个或者几个）
      void set_revents(int revt) { revents_ = revt; } // used by pollers
      // int revents() const { return revents_; }
      bool isNoneEvent() const { return events_ == kNoneEvent; }

      // 对事件的控制，关注或者不关注一些事件，用下面的方法
      // 注意这个update事件，就相当于你更新了你的关注的事件
      void enableReading()
      {
        events_ |= kReadEvent;
        update();
      }
      void disableReading()
      {
        events_ &= ~kReadEvent;
        update();
      }
      void enableWriting()
      {
        events_ |= kWriteEvent;
        update();
      }
      void disableWriting()
      {
        events_ &= ~kWriteEvent;
        update();
      }
      void disableAll()
      {
        events_ = kNoneEvent;
        update();
      }
      bool isWriting() const { return events_ & kWriteEvent; }
      bool isReading() const { return events_ & kReadEvent; }

      // for Poller
      int index() { return index_; }
      void set_index(int idx) { index_ = idx; }

      // for debug
      string reventsToString() const;
      string eventsToString() const;

      void doNotLogHup() { logHup_ = false; }

      EventLoop *ownerLoop() { return loop_; }
      void remove();

    private:
      static string eventsToString(int fd, int ev);

      void update();
      void handleEventWithGuard(Timestamp receiveTime);

      // 事件常量，在.cc文件中已经定义了
      static const int kNoneEvent;
      static const int kReadEvent;
      static const int kWriteEvent;

      // 所属的eventloop，一个channel只能给一个eventloop
      EventLoop *loop_;
      const int fd_;
      // 关注的事件
      int events_;
      // poll/epoll返回事件
      int revents_; // it's the received event types of epoll or poll
      // 在poll的事件数组中的序号（poll函数会提供一个数据，告诉你你在数据中的位置，你从这个位置中拿你的事件）
      // 一直看的都是epoll，poll都块给忘完了
      int index_; // used by Poller. epoll有不同的涵义
      bool logHup_;

      std::weak_ptr<void> tie_;
      bool tied_;
      // 是否处在事件的处理中
      bool eventHandling_;
      // 添加到事件循环中了没有
      bool addedToLoop_;
      ReadEventCallback readCallback_;
      EventCallback writeCallback_;
      EventCallback closeCallback_;
      EventCallback errorCallback_;
    };

  } // namespace net
} // namespace muduo

#endif // MUDUO_NET_CHANNEL_H
