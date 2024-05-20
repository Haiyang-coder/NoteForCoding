// Copyright 2010, Shuo Chen.  All rights reserved.
// http://code.google.com/p/muduo/
//
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.

// Author: Shuo Chen (chenshuo at chenshuo dot com)
//
// This is a public header file, it must only include public header files.

#ifndef MUDUO_NET_EVENTLOOPTHREAD_H
#define MUDUO_NET_EVENTLOOPTHREAD_H

#include "muduo/base/Condition.h"
#include "muduo/base/Mutex.h"
#include "muduo/base/Thread.h"

namespace muduo
{
  namespace net
  {

    class EventLoop;

    class EventLoopThread : noncopyable
    {
      // muduo是一个io线程一个loop
      // 所以可以有多个io线程
      // 多个io线程可以用io线程池来管理
      // 这个类用来封装io线程
      // 功能：
      // 1.创建也给线程
      // 在该线程中创建一个loop对象，并让该对象处于loop状态
    public:
      typedef std::function<void(EventLoop *)> ThreadInitCallback;

      EventLoopThread(const ThreadInitCallback &cb = ThreadInitCallback(),
                      const string &name = string());
      ~EventLoopThread();
      // 启动线程，该线程就是io线程，在这个线程中创建一个eventloop对象
      EventLoop *startLoop();

    private:
      // 线程函数
      void threadFunc();

      // 指向一个eventloop对象
      EventLoop *loop_ GUARDED_BY(mutex_);
      // 是否退出
      bool exiting_;
      // 基于对象的编程思想，包含也给thread类
      Thread thread_;
      // 和条件变量配合使用
      MutexLock mutex_;
      Condition cond_ GUARDED_BY(mutex_);
      // 回调函数，没有也可以，会有一个空的
      // 如果回调函数不是空的，在loop循环之前被调用
      // 相当于进行初始化，初始化完了之后在进行循环
      ThreadInitCallback callback_;
    };

  } // namespace net
} // namespace muduo

#endif // MUDUO_NET_EVENTLOOPTHREAD_H
