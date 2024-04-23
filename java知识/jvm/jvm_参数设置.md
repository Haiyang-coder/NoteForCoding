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
>默认是15,最大也是15,年轻代经历过这个次数的GC进入了老年代

### 6.XX:PretenureSizeThreshold
>大对象直接进去老年代

### 7.-XX:+UseParNewGC
>采用ParNew的垃圾回收器

### 8.XX:CMSInitiatingOccupancyFaction
>老年代的空间占用达到多少的时候进行fullGC

### 9.-XX:+UseCMSCompactAtFullCollection”，默认就打开了
>在FULLGC之后他意思是在Full GC之后要再次进行“Stop the World”，停止工作线程，然后进行碎片整理，就是把存活对象挪到一起，空出来大片连续内存空间，避免内存碎片

### 10.-XX:CMSFullGCsBeforeCompaction
>这个意思是执行多少次Full GC之后再执行一次内存碎片整理的工作，默认是0，意思就是每次Full GC之后都会进行一次内存整理