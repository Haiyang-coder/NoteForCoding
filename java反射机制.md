# java反射机制
[1. java的状态](#1java的状态)
[2. Class类](#2class类)
[3. java的加载方式](#3java的加载方式)
[4. java反射爆破](#4反射爆破)

##  1.java的状态
![状态](https://raw.githubusercontent.com/Haiyang-coder/ImageRepository/main/D17D91B8-3D7A-408E-96A9-7ED3A2AD435D.jpeg)
java的的三种运行状态
> 1.编译阶段
> 2.加载阶段(此时会在堆中形成一个唯一的数据结构,包含了类的所有的信息)
> 3.运行状态,获取完类的对象,开始操作
> 4.类的字节码的二进制文件储存在方法区
## 2.Class类
**还记得有一个getclass()方法吗**
> 方法代表着就是某个类在加载后在堆中的对象

**Class类的基本介绍**
>1. Class类也是类,继承于Object
>2. Class类不是new出来的而是系统创建的
>3. 类的Class对象,在内存中只会存在一份,因为类只加载一次
>4. 每个类的实例都会记得自己是由哪个Class实例生成的
>5. 通过Class对象可以得到一个类的完整的结构，可以通过一系列的API获取结构中的信息。如构造方法，成员变量等等
>6. Class的对象是放在堆中的
>7. 类的字节码数据放在方法区



![d](https://raw.githubusercontent.com/Haiyang-coder/ImageRepository/main/d.png)

## 3.java的加载方式
 1. 静态加载
   >如果你用new来创建对象,那么就是动态加载.没有这个类,直接报错
 2. 动态加载
   >如果用ClassForName，那就是动态加载，只有运行时没有这个类才会报错，这就是用到了反射机制

## 4.反射爆破
> 通过java的类的方法,可以直接修改Class对象中的各种变量和方法,无论是私有还是公开的
1. 反射爆破属性
2. 反射爆破方法
3. 反射爆破对象
