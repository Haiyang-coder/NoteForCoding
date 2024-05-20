// Copyright 2010, Shuo Chen.  All rights reserved.
// http://code.google.com/p/muduo/
//
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.

// Author: Shuo Chen (chenshuo at chenshuo dot com)

#include "muduo/net/EventLoopThread.h"

#include "muduo/net/EventLoop.h"

using namespace muduo;
using namespace muduo::net;

EventLoopThread::EventLoopThread(const ThreadInitCallback &cb,
                                 const string &name)
    : loop_(NULL),
      exiting_(false),
      thread_(std::bind(&EventLoopThread::threadFunc, this), name),
      mutex_(),
      cond_(mutex_),
      callback_(cb)
{
}

EventLoopThread::~EventLoopThread()
{
  exiting_ = true;
  if (loop_ != NULL) // not 100% race-free, eg. threadFunc could be running callback_.
  {
    // still a tiny chance to call destructed object, if threadFunc exits just now.
    // but when EventLoopThread destructs, usually programming is exiting anyway.
    loop_->quit();
    // 等待线程结束
    thread_.join();
  }
}

// 调用这个方法之后会返回一个loop指针让你操作loop
// 但是注意这个loop指针指向的对象并不在主线程中，所以算是跨线程使用loop了
EventLoop *EventLoopThread::startLoop()
{
  assert(!thread_.started());
  // 启动io线程
  thread_.start();

  // 这里注意，从现在开始就是多线程的状态了
  EventLoop *loop = NULL;
  {
    // 这里的条件变量在等待loop指针不为空
    // loop指针是在thread_线程中创建的
    // 这就是使用条件变量的原因
    MutexLockGuard lock(mutex_);
    while (loop_ == NULL)
    {
      cond_.wait();
    }
    loop = loop_;
  }

  return loop;
}

// 这是子线程，他和主线程公共操作的变量就是loop，所以涉及到loop的地方全部都加上了锁
void EventLoopThread::threadFunc()
{
  EventLoop loop;

  if (callback_)
  {
    // 这个回调函数就是给loop初始化用的，你不想传默认loop默认初始化
    callback_(&loop);
  }

  {
    MutexLockGuard lock(mutex_);
    // loop指针指向了一个栈上的对象
    // threadfunc退出的时候，指针就失效了
    loop_ = &loop;
    // 通知loop有值了
    cond_.notify();
  }

  // 一直在loop循环
  loop.loop();
  // assert(exiting_);
  MutexLockGuard lock(mutex_);
  loop_ = NULL;
}
