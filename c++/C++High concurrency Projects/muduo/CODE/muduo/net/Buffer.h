// Copyright 2010, Shuo Chen.  All rights reserved.
// http://code.google.com/p/muduo/
//
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.

// Author: Shuo Chen (chenshuo at chenshuo dot com)
//
// This is a public header file, it must only include public header files.

#ifndef MUDUO_NET_BUFFER_H
#define MUDUO_NET_BUFFER_H

#include "muduo/base/copyable.h"
#include "muduo/base/StringPiece.h"
#include "muduo/base/Types.h"

#include "muduo/net/Endian.h"

#include <algorithm>
#include <vector>

#include <assert.h>
#include <string.h>
// #include <unistd.h>  // ssize_t

namespace muduo
{
  namespace net
  {

    /// A buffer class modeled after org.jboss.netty.buffer.ChannelBuffer
    ///
    /// @code
    /// +-------------------+------------------+------------------+
    /// | prependable bytes |  readable bytes  |  writable bytes  |
    /// |                   |     (CONTENT)    |                  |
    /// +-------------------+------------------+------------------+
    /// |                   |                  |                  |
    /// 0      <=      readerIndex   <=   writerIndex    <=     size
    /// @endcode
    class Buffer : public muduo::copyable
    {
    public:
      static const size_t kCheapPrepend = 8;
      static const size_t kInitialSize = 1024;

      explicit Buffer(size_t initialSize = kInitialSize)
          : buffer_(kCheapPrepend + initialSize),
            readerIndex_(kCheapPrepend),
            writerIndex_(kCheapPrepend)
      {
        assert(readableBytes() == 0);
        assert(writableBytes() == initialSize);
        assert(prependableBytes() == kCheapPrepend);
      }

      // implicit copy-ctor, move-ctor, dtor and assignment are fine
      // NOTE: implicit move-ctor is added in g++ 4.6

      // 交换Buffer
      void swap(Buffer &rhs)
      {
        buffer_.swap(rhs.buffer_);
        std::swap(readerIndex_, rhs.readerIndex_);
        std::swap(writerIndex_, rhs.writerIndex_);
      }
      // 可读的字节数
      size_t readableBytes() const
      {
        return writerIndex_ - readerIndex_;
      }
      // 可以写入和字节数
      size_t writableBytes() const
      {
        return buffer_.size() - writerIndex_;
      }
      // 预备的字节数
      size_t prependableBytes() const
      {
        return readerIndex_;
      }
      // 返回可读的指针
      const char *peek() const
      {
        return begin() + readerIndex_;
      }
      // 查找crlf
      // CRLF 是回车符（Carriage Return）和换行符（Line Feed）的组合，通常表示为 "\r\n"。它是一种在文本文件中表示换行的标准约定。在这个序列中，"\r" 表示回车，将光标移动到行首，而 "\n" 表示换行，将光标移动到下一行的行首。
      const char *findCRLF() const
      {
        // FIXME: replace with memmem()?
        const char *crlf = std::search(peek(), beginWrite(), kCRLF, kCRLF + 2);
        return crlf == beginWrite() ? NULL : crlf;
      }
      // 从指定的位置查找crlf
      const char *findCRLF(const char *start) const
      {
        assert(peek() <= start);
        assert(start <= beginWrite());
        // FIXME: replace with memmem()?
        const char *crlf = std::search(start, beginWrite(), kCRLF, kCRLF + 2);
        return crlf == beginWrite() ? NULL : crlf;
      }
      //"EOL" 是 "End of Line" 的缩写，指的是一行的结束。它通常用于描述文件或文本数据中的行尾。
      // 在不同的操作系统和文件系统中，EOL 可以由不同的符号或组合来表示：
      // CRLF（\r\n）： 在 Windows  操作系统中，每行的结束通常由回车和换行两个字符组成，即"\r\n"。
      // LF（\n）： 在 Unix/Linux 操作系统中，每行的结束通常由换行符一个字符组成，即 "\n"。
      // CR（\r）： 在老的 Macintosh 系统中，每行的结束通常由回车符一个字符组成，即 "\r"。
      const char *findEOL() const
      {
        const void *eol = memchr(peek(), '\n', readableBytes());
        return static_cast<const char *>(eol);
      }

      const char *findEOL(const char *start) const
      {
        assert(peek() <= start);
        assert(start <= beginWrite());
        const void *eol = memchr(start, '\n', beginWrite() - start);
        return static_cast<const char *>(eol);
      }

      // retrieve returns void, to prevent
      // string str(retrieve(readableBytes()), readableBytes());
      // the evaluation of two functions are unspecified
      // 取回数据len个数据
      void retrieve(size_t len)
      {
        assert(len <= readableBytes());
        if (len < readableBytes())
        {
          readerIndex_ += len;
        }
        else
        {
          retrieveAll();
        }
      }
      // 调整可读直到某一个位置
      void retrieveUntil(const char *end)
      {
        assert(peek() <= end);
        assert(end <= beginWrite());
        retrieve(end - peek());
      }

      void retrieveInt64()
      {
        retrieve(sizeof(int64_t));
      }

      void retrieveInt32()
      {
        retrieve(sizeof(int32_t));
      }

      void retrieveInt16()
      {
        retrieve(sizeof(int16_t));
      }

      void retrieveInt8()
      {
        retrieve(sizeof(int8_t));
      }

      void retrieveAll()
      {
        readerIndex_ = kCheapPrepend;
        writerIndex_ = kCheapPrepend;
      }

      string retrieveAllAsString()
      {
        return retrieveAsString(readableBytes());
      }
      // 取回返回字符串
      string retrieveAsString(size_t len)
      {
        assert(len <= readableBytes());
        string result(peek(), len);
        retrieve(len);
        return result;
      }
      // 转换成StringPiece
      StringPiece toStringPiece() const
      {
        return StringPiece(peek(), static_cast<int>(readableBytes()));
      }
      // 添加数据
      void append(const StringPiece &str)
      {
        append(str.data(), str.size());
      }
      // 添加数据
      void append(const char * /*restrict*/ data, size_t len)
      {
        ensureWritableBytes(len);
        std::copy(data, data + len, beginWrite());
        hasWritten(len);
      }
      // 添加数据
      void append(const void * /*restrict*/ data, size_t len)
      {
        append(static_cast<const char *>(data), len);
      }
      // 确保可写空间》=len，不行就扩充
      void ensureWritableBytes(size_t len)
      {
        if (writableBytes() < len)
        {
          makeSpace(len);
        }
        assert(writableBytes() >= len);
      }
      // 可写的位置
      char *beginWrite()
      {
        return begin() + writerIndex_;
      }

      const char *beginWrite() const
      {
        return begin() + writerIndex_;
      }
      // 调整可写位置
      void hasWritten(size_t len)
      {
        assert(len <= writableBytes());
        writerIndex_ += len;
      }
      // 减少可写位置
      void unwrite(size_t len)
      {
        assert(len <= readableBytes());
        writerIndex_ -= len;
      }

      ///
      /// Append int64_t using network endian
      ///
      void appendInt64(int64_t x)
      {
        int64_t be64 = sockets::hostToNetwork64(x);
        append(&be64, sizeof be64);
      }

      ///
      /// Append int32_t using network endian
      ///
      void appendInt32(int32_t x)
      {
        int32_t be32 = sockets::hostToNetwork32(x);
        append(&be32, sizeof be32);
      }

      void appendInt16(int16_t x)
      {
        int16_t be16 = sockets::hostToNetwork16(x);
        append(&be16, sizeof be16);
      }

      void appendInt8(int8_t x)
      {
        append(&x, sizeof x);
      }

      ///
      /// Read int64_t from network endian
      ///
      /// Require: buf->readableBytes() >= sizeof(int32_t)
      // 读一个64位整数
      int64_t readInt64()
      {
        int64_t result = peekInt64();
        retrieveInt64();
        return result;
      }

      ///
      /// Read int32_t from network endian
      ///
      /// Require: buf->readableBytes() >= sizeof(int32_t)
      int32_t readInt32()
      {
        int32_t result = peekInt32();
        retrieveInt32();
        return result;
      }

      int16_t readInt16()
      {
        int16_t result = peekInt16();
        retrieveInt16();
        return result;
      }

      int8_t readInt8()
      {
        int8_t result = peekInt8();
        retrieveInt8();
        return result;
      }

      ///
      /// Peek int64_t from network endian
      ///
      /// Require: buf->readableBytes() >= sizeof(int64_t)
      int64_t peekInt64() const
      {
        assert(readableBytes() >= sizeof(int64_t));
        int64_t be64 = 0;
        ::memcpy(&be64, peek(), sizeof be64);
        return sockets::networkToHost64(be64);
      }

      ///
      /// Peek int32_t from network endian
      ///
      /// Require: buf->readableBytes() >= sizeof(int32_t)
      int32_t peekInt32() const
      {
        assert(readableBytes() >= sizeof(int32_t));
        int32_t be32 = 0;
        ::memcpy(&be32, peek(), sizeof be32);
        return sockets::networkToHost32(be32);
      }

      int16_t peekInt16() const
      {
        assert(readableBytes() >= sizeof(int16_t));
        int16_t be16 = 0;
        ::memcpy(&be16, peek(), sizeof be16);
        return sockets::networkToHost16(be16);
      }

      int8_t peekInt8() const
      {
        assert(readableBytes() >= sizeof(int8_t));
        int8_t x = *peek();
        return x;
      }

      ///
      /// Prepend int64_t using network endian
      ///
      void prependInt64(int64_t x)
      {
        int64_t be64 = sockets::hostToNetwork64(x);
        prepend(&be64, sizeof be64);
      }

      ///
      /// Prepend int32_t using network endian
      ///
      void prependInt32(int32_t x)
      {
        int32_t be32 = sockets::hostToNetwork32(x);
        prepend(&be32, sizeof be32);
      }

      void prependInt16(int16_t x)
      {
        int16_t be16 = sockets::hostToNetwork16(x);
        prepend(&be16, sizeof be16);
      }

      void prependInt8(int8_t x)
      {
        prepend(&x, sizeof x);
      }

      void prepend(const void * /*restrict*/ data, size_t len)
      {
        assert(len <= prependableBytes());
        readerIndex_ -= len;
        const char *d = static_cast<const char *>(data);
        std::copy(d, d + len, begin() + readerIndex_);
      }

      void shrink(size_t reserve)
      {
        // FIXME: use vector::shrink_to_fit() in C++ 11 if possible.
        Buffer other;
        other.ensureWritableBytes(readableBytes() + reserve);
        other.append(toStringPiece());
        swap(other);
      }

      size_t internalCapacity() const
      {
        return buffer_.capacity();
      }

      /// Read data directly into buffer.
      ///
      /// It may implement with readv(2)
      /// @return result of read(2), @c errno is saved
      ssize_t readFd(int fd, int *savedErrno);

    private:
      char *begin()
      {
        return &*buffer_.begin();
      }

      const char *begin() const
      {
        return &*buffer_.begin();
      }
      // 扩充空间
      void makeSpace(size_t len)
      {
        if (writableBytes() + prependableBytes() < len + kCheapPrepend)
        {
          // FIXME: move readable data
          buffer_.resize(writerIndex_ + len);
        }
        else
        {
          // move readable data to the front, make space inside buffer
          assert(kCheapPrepend < readerIndex_);
          size_t readable = readableBytes();
          std::copy(begin() + readerIndex_,
                    begin() + writerIndex_,
                    begin() + kCheapPrepend);
          readerIndex_ = kCheapPrepend;
          writerIndex_ = readerIndex_ + readable;
          assert(readable == readableBytes());
        }
      }

    private:
      // 缓冲区空间
      std::vector<char> buffer_;
      // 读位置
      size_t readerIndex_;
      // 写位置
      size_t writerIndex_;

      static const char kCRLF[];
    };

  } // namespace net
} // namespace muduo

#endif // MUDUO_NET_BUFFER_H
