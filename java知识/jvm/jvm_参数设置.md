[TOC]
# JVM参数设置
- **Xms**: java堆内存大小
- **Xmx**: java堆内存最大大小
- **Xmn**: java堆内存中新生代大小(剩下的就是老年代大小了)
- **XX:PermSize**: 永久代大小
- **XX:MaxPermSize**: 永久代最大大小
- **Xss**: 每个线程内存的大小

下面详细介绍:
## 参数补充
### 1. Xms和Xmx
>java内存刚开始的大小和允许扩张的最大的大小

### 2.Xmn
>新生代内存大小,扣除掉新生代就是老年代的内存大小了

### 3.XX:PermSize和XX:MaxPermSize
>在jdk1.8版本以后换用了metaspaceSize了,限定了永久代的大小和允许的最大的大小

### 4.Xss
>限定了每个线程的栈内存大小