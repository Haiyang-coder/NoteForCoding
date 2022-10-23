[TOC]
# jvm 垃圾回收
jvm垃圾回收:强应用不会回收,弱引用和软引用可能会被回收,看一下[java_引用类型](https://github.com/Haiyang-coder/NoteForJava/blob/main/java%E7%9F%A5%E8%AF%86/java_%E5%BC%95%E7%94%A8%E7%B1%BB%E5%9E%8B.md)

## 1.新生代垃圾回收算法---复制算法
>1. 将新生代分成两个区,新建的对象先放在同一个区里面,等到对象快放满了
>2. 对象快满了扫描,标记出不能回收的区域
>3. 将标记的不可回收的区域整体搬迁到另一个空白区域,清空之前的区域

- **优点**
可以有效的避免了内存碎片
- **缺点**
每次只能使用一般的年轻代

## 2.新生代垃圾回收算法---优化复制算法
<font color=red>1个Eden区，2个Survivor区</font>，其中Eden区占80%内存空间，每一块Survivor区各占10%内存空间，比如说Eden区有800MB内存，每一块Survivor区就100MB内

>1. 先放到Eden区里面,快满了在扫描,将存活的对象放到Survivor里面
>2. 又满了之后再次进行扫描,将存货的和Survivor区(也参加了扫描)一块放到另一个Survivor区里面