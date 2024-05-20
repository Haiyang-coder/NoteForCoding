// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#ifndef MUDUO_BASE_ASYNCLOGGING_H
#define MUDUO_BASE_ASYNCLOGGING_H

#include "muduo/base/BlockingQueue.h"
#include "muduo/base/BoundedBlockingQueue.h"
#include "muduo/base/CountDownLatch.h"
#include "muduo/base/Mutex.h"
#include "muduo/base/Thread.h"
#include "muduo/base/LogStream.h"

#include <atomic>
#include <vector>

namespace muduo
{

  class AsyncLogging : noncopyable
  {
  public:
    AsyncLogging(const string &basename,
                 off_t rollSize,
                 int flushInterval = 3);

    ~AsyncLogging()
    {
      if (running_)
      {
        stop();
      }
    }

    void append(const char *logline, int len);

    void start()
    {
      running_ = true;
      thread_.start();
      latch_.wait();
    }

    void stop() NO_THREAD_SAFETY_ANALYSIS
    {
      running_ = false;
      cond_.notify();
      thread_.join();
    }

  private:
    void threadFunc();

    typedef muduo::detail::FixedBuffer<muduo::detail::kLargeBuffer> Buffer;
    typedef std::vector<std::unique_ptr<Buffer>> BufferVector;
    typedef BufferVector::value_type BufferPtr;

    // 刷新时间，如果时间到了，不管你写没写满都会把你刷新到缓冲区中去
    const int flushInterval_;
    std::atomic<bool> running_;
    const string basename_;
    // 日志文件的滚动大小
    const off_t rollSize_;
    muduo::Thread thread_;
    // 用于等待线程启动
    muduo::CountDownLatch latch_;
    muduo::MutexLock mutex_;
    muduo::Condition cond_ GUARDED_BY(mutex_);
    // 当前缓冲区
    BufferPtr currentBuffer_ GUARDED_BY(mutex_);
    // 预备缓冲区
    BufferPtr nextBuffer_ GUARDED_BY(mutex_);
    // 待写入文件，已经写满的缓冲区
    BufferVector buffers_ GUARDED_BY(mutex_);
  };

} // namespace muduo

#endif // MUDUO_BASE_ASYNCLOGGING_H
