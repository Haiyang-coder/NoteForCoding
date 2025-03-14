// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#include "muduo/base/AsyncLogging.h"
#include "muduo/base/LogFile.h"
#include "muduo/base/Timestamp.h"

#include <stdio.h>

using namespace muduo;

AsyncLogging::AsyncLogging(const string &basename,
                           off_t rollSize,
                           int flushInterval)
    : flushInterval_(flushInterval),
      running_(false),
      basename_(basename),
      rollSize_(rollSize),
      thread_(std::bind(&AsyncLogging::threadFunc, this), "Logging"),
      latch_(1),
      mutex_(),
      cond_(mutex_),
      currentBuffer_(new Buffer),
      nextBuffer_(new Buffer),
      buffers_()
{
  currentBuffer_->bzero();
  nextBuffer_->bzero();
  buffers_.reserve(16);
}

void AsyncLogging::append(const char *logline, int len)
{
  // 这就是前台所有的线程调用的入口函数
  muduo::MutexLockGuard lock(mutex_);
  // 加一个锁，同一时间只允许一个线程将日志写入内存缓冲区
  if (currentBuffer_->avail() > len)
  {
    // 当前的缓冲区可以容纳，直接写入当前的缓冲区中
    currentBuffer_->append(logline, len);
  }
  else
  {
    // 缓冲区不够用了，将这个缓冲区放到已经填满的缓冲区队列中
    buffers_.push_back(std::move(currentBuffer_));

    // 将备用缓冲区编程当前缓冲区使用
    // 只涉及到指针的拷贝，还是很快的
    // 如果备用缓冲区没有，新建一个在移动指针
    if (nextBuffer_)
    {

      currentBuffer_ = std::move(nextBuffer_);
    }
    else
    {
      currentBuffer_.reset(new Buffer); // Rarely happens
    }
    currentBuffer_->append(logline, len);
    // 代码运行到这里，意味着有一个缓冲区已经满了，所以唤醒刷盘线程进行落盘操作
    cond_.notify();
  }
}

void AsyncLogging::threadFunc()
{
  assert(running_ == true);
  latch_.countDown();
  LogFile output(basename_, rollSize_, false);
  // 这是两个临时的落盘缓存
  BufferPtr newBuffer1(new Buffer);
  BufferPtr newBuffer2(new Buffer);
  newBuffer1->bzero();
  newBuffer2->bzero();
  // 存储着落盘缓存块的容器
  BufferVector buffersToWrite;
  buffersToWrite.reserve(16);
  while (running_)
  {
    assert(newBuffer1 && newBuffer1->length() == 0);
    assert(newBuffer2 && newBuffer2->length() == 0);
    assert(buffersToWrite.empty());

    {
      muduo::MutexLockGuard lock(mutex_);
      // 倒计时结束也会刷盘，如果容器是空的继续等待
      if (buffers_.empty()) // unusual usage!
      {
        cond_.waitForSeconds(flushInterval_);
      }
      // 把当前的缓存一块放上
      buffers_.push_back(std::move(currentBuffer_));
      currentBuffer_ = std::move(newBuffer1);
      buffersToWrite.swap(buffers_);
      if (!nextBuffer_)
      {
        nextBuffer_ = std::move(newBuffer2);
      }
    }

    assert(!buffersToWrite.empty());

    if (buffersToWrite.size() > 25)
    {
      // 这里是判断前端死循环拼命写日志导致了日志堆积/
      // 也就是前端拼命申请缓冲区放入直到有25块
      // 100m的日志来不及处理
      char buf[256];
      snprintf(buf, sizeof buf, "Dropped log messages at %s, %zd larger buffers\n",
               Timestamp::now().toFormattedString().c_str(),
               buffersToWrite.size() - 2);
      fputs(buf, stderr);
      output.append(buf, static_cast<int>(strlen(buf)));
      // 出了前两块日志，其他的日志全部丢掉
      buffersToWrite.erase(buffersToWrite.begin() + 2, buffersToWrite.end());
    }

    for (const auto &buffer : buffersToWrite)
    {
      // FIXME: use unbuffered stdio FILE ? or use ::writev ?
      output.append(buffer->data(), buffer->length());
    }

    if (buffersToWrite.size() > 2)
    {
      // drop non-bzero-ed buffers, avoid trashing
      // 都已经写完了，我们仅仅保留两块给newbuffer1和newbuffer2
      buffersToWrite.resize(2);
    }

    if (!newBuffer1)
    {
      assert(!buffersToWrite.empty());
      newBuffer1 = std::move(buffersToWrite.back());
      buffersToWrite.pop_back();
      newBuffer1->reset();
    }

    if (!newBuffer2)
    {
      assert(!buffersToWrite.empty());
      newBuffer2 = std::move(buffersToWrite.back());
      buffersToWrite.pop_back();
      newBuffer2->reset();
    }

    // 这里缓冲区申请都是用智能指针来管理的
    // clear之后会自动销毁
    buffersToWrite.clear();
    output.flush();
  }
  output.flush();
}
