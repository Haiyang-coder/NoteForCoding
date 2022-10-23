[TOC]
# JVM参数设置


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

### 5.XX:MaxTenuringThreshold
>默认是15

### 6.XX:PretenureSizeThreshold
>大对象直接进去老年代