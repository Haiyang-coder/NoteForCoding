[TOC]
# class文件格式
 ![](https://raw.githubusercontent.com/Haiyang-coder/ImageRepository/main/class.png)
 
 上图表示了class文件的总结构
## 1.class 常量池
如图所示:
- `constant_pool_count` 表示了常量池中的数量,用两个字节表示
- `constant_pool[constant_pool_count - 1]`表示了所有的常量池的的数据,
- 数据类型是`cp_info`,结构如下,第一个字节是表示常量种类
  ```java
  cp_info{
    u1 tag;
    u1 info[]
  }
  ```

### 要如何阅读常量池呢?
1. 先看tag,找到种类,如果是07,则种类是`CONSTANT_Class`
 ![](https://raw.githubusercontent.com/Haiyang-coder/ImageRepository/main/常量区种类.png)
2. 找到`CONSTANT_Class`结构,可以看到,一个字节也是种类,另外两个字节是索引
![](https://raw.githubusercontent.com/Haiyang-coder/ImageRepository/main/SHUJU.png)
3. 上图是给的索引,索引就是在常量池中的哪里,如图的反编译文件是1的索引就直接指向了2
![](https://raw.githubusercontent.com/Haiyang-coder/ImageRepository/main/changliangchi.png)
4. 2就不是索引了,是直接的值,可见2出的类型不同,是UTF8类型,1是CLASS类型,和3一样都是索引

其他方法也和常量池一样,先看属性结构,然后看占了多少字节,将对应的字节转换成对应的结构