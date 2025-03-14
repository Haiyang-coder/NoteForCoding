# 为什么要区分二进制文件和文本文件？

 

1. **数据处理方式**：
   - 文本文件是以字符为单位的，通常包含可打印字符（如字母、数字、符号等），以及一些控制字符（如回车、换行等）。文本文件的内容通常是人类可读的。
   - 二进制文件是以字节为单位的，可以包含任意数据，包括非文本数据（如图像、音频、视频等），它们可能包含不可打印字符或二进制数据。
2. **换行符差异**：
   - 文本文件中的换行通常由回车字符（`\r`）和换行字符（`\n`）组成。这种换行方式在不同操作系统上有所不同，例如在Windows上通常使用CRLF (`\r\n`)，而在Unix/Linux上使用LF (`\n`)。
   - 二进制文件没有这种特殊的换行约定，可以包含各种换行符。
3. **文本处理**：
   - 读取文本文件时，文本模式通常会自动进行换行字符的转换，以适应当前操作系统的约定。
   - 读取二进制文件时，不会进行这种自动转换，因此它们保留了原始的字节数据。
4. **文件尾部空格**：
   - 文本文件通常不包含文件尾部的空格或空白字符。
   - 二进制文件可以包含文件尾部的任意字节。

由于这些差异，对于文件的正确读取和写入，应该明确区分文本文件和二进制文件。如果你试图用文本模式打开二进制文件，或者尝试用二进制模式打开文本文件，可能会导致文件内容的损坏或不正确的结果。

因此，文件打开模式的正确选择很重要，以确保文件的处理方式与文件的内容和格式相匹配。例如，当你处理文本文件时，通常应该使用文本模式来确保换行字符的处理是正确的。而在处理二进制文件时，应该使用二进制模式，以防止对文件内容进行不必要的修改。

# 关于线程函数

在多线程的时候有一个有意思的bug，在同一个函数里面调用线程结束函数，会导致这个函数不能直接析构占用的堆栈，也就是说在这个函数里面申请的变量空间也不能自动调用析构，造成了内存泄漏，所以，要把线程要做的事情单独写一个函数，在这个函数外面在调用线程的结束方法。注意我这里讲的主要是系统的api函数，如`_beginthread()`,但是在`std::thread`中没有这种的问题。我们常用的`exit(0)`也有这种问题，你调用之后会结束当前的线程，导致不会触发有些变量的构造函数，导致内存泄漏。

# 析构函数和虚析构函数的区别

析构函数和虚析构函数有一些重要的区别。下面是它们之间的主要区别：

1. **析构函数：**
   - 析构函数是用于释放对象占用的资源和执行清理操作的特殊函数。
   - 它的名称是在类名前加上波浪号 `~`，如 `~ClassName()`。
   - 没有参数，也不能被继承，因此不能被重载。
   - 在派生类对象被销毁时，只会调用派生类的析构函数，而不会调用基类的析构函数（除非基类的析构函数是虚的）。
2. **虚析构函数：**
   - 虚析构函数是一个被声明为虚函数的析构函数。
   - 使用关键字 `virtual` 声明，如 `virtual ~ClassName()`。
   - 允许在继承层次结构中正确调用派生类对象的析构函数，即使通过基类指针或引用来操作这些对象。
   - 当通过基类指针或引用删除派生类对象时，应使用虚析构函数，以确保调用正确的析构函数。否则，可能导致派生类对象的资源没有正确释放。

使用虚析构函数的主要情况是当你有一个基类指针指向一个派生类对象，并且你希望在删除这个指针时正确调用派生类的析构函数。如果基类的析构函数是虚的，那么通过基类指针或引用删除对象时，将调用正确的析构函数，确保释放派生类的资源。

# 关于多线程同步互斥的的几种方式

## 1. 加锁,

**代码规范问题：**

这个是最先想到的是吧，但是有一个很致命的问题，一个临界变量你加锁使用没问题。过了一段时间，有人维护你的代码，他不知道这个变量需要加锁使用，他会直接用，就出了大问题了。这依赖开发人员的规范，很头疼。而且枷锁的不规范，粒度很大的话，就会影响效率。

**解锁策略问题：**

如果有很多线程，lock多了，在解锁的时候先解锁哪一个？会导致一些线程永远得不到执行。

当然你可以自由竞争，但是有些关键线程也会延时，性能会抖动（任务一会卡，一会不卡）

## 2. IOCP



## 3. 互斥体

无视平台，是由应用程序来控制的



## 3. 临界区

有内核来控制的，保护的是代码段

## 4.原子操作

保护的是操作，但是谁先谁后，我不管

# 关于动态绑定的讨论

经常见编程中说的动态绑定，什么叫动态绑定:

> 指的是在运行时确定对象与方法（或函数）之间的关联关系，而不是在编译时确定。这意味着在程序执行的过程中，系统会根据实际的对象类型来确定调用哪个方法，而不是根据代码中的声明或类型信息。

那c++的动态绑定是如何实现的呢？

> **虚函数：** 在基类中声明的虚函数是在派生类中可以被重写的函数。通过使用关键字 `virtual`，你可以告诉编译器这个函数是虚函数。
>
> **虚表：** 每个包含虚函数的类都有一个虚表，这是一个指向虚函数地址的指针数组。当一个类包含虚函数时，编译器会在对象的内存布局中插入一个指向虚表的指针（通常在对象的开头）。
>
> **动态绑定过程：** 当通过基类指针或引用调用虚函数时，实际执行的是派生类中的重写版本，而不是基类中的原始版本。这是因为在运行时，系统会根据对象的实际类型找到正确的虚表，并调用相应的虚函数。

可以看出，每次调用函数都会查一下虚函数表，所以是动态绑定，如果在编译时就确定，那就确定了就是静态绑定。动态绑定在牺牲部分性能的代价下，提高了程序的灵活性和可扩展性。





# bool

c++在linux中bool类型是原子操作，所以跨线程不需要锁住bool类型