[TOC]
# 字节码执行引擎
功能就是,输入字节码文件,对字节码文件进行解析并处理,最后执行输出的结果.

## 栈帧
![](https://raw.githubusercontent.com/Haiyang-coder/ImageRepository/main/单独发.png)
### 1.局部变量表
>用来存储方法参数和内部定义的局部变量的存储空间,以slot为单位,一个slot存放32位以内的数据类型
>对于实例方法,slot第0位是this,然后从1到n放的参数列表和局部变量,static就不会有this

![](https://raw.githubusercontent.com/Haiyang-coder/ImageRepository/main/sasfpng)

**slot是复用的,以节省栈帧的空间**
这个功能有可能会会影响垃圾回收机制,因为你slot插槽的对象还在,垃圾回收机制会认为你还有用,所以不会进行垃圾回收,除非栈帧退出或者另一个变量顶替了插槽,所以有时候对象用完及时置为null有可能会提升效率.

### 2.操作数栈
操作数栈操作的数据都是从slot插槽中获取的.算完之后会返回在赋值给插槽(如果插槽有的话)