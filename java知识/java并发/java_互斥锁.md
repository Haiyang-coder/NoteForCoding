[TOC]
# 用互斥锁解决原子性问题
因为原子性的问题产生的原因是因为线程中断引起的,但是我们不能禁止线程的中断而且在多核的现在,高位地址和地位地址的写入可能在不同的cpu上进行,就算禁止了一个cpu的线程中断也不能达到原子性.但是保证了<font color=red>对共享变量同一时刻只有一个线程在修改</font>,那么我们就能实现原子性.

## 1.java提供的锁的技术synchronized
>synchronized加锁和解锁的对象是可以自己指定的,如果不指定也会有默认值
- <font color=red>当修饰静态方法的时候,锁定的是class对象</font>
- <font color=red>修饰非静态方法的时候,锁定的对象就是this</font>
  
## 2.锁和受保护资源的关系
>结论<font color=red>一把锁可以保护多个资源,但是多把锁不能保护一个资源</font>:原因也靠理解,多把锁,保护一个的话,不同锁之间不能保证了可见性.
## 3.如何做到一把锁保护多个资源

### (1)保护没有关联性的多个资源
- 用不同的锁来保护不同的资源,比如存款取款是一个资源,修改查看头像是一个资源,你可以用两个不同的锁各自锁住不同的资源
- 你也可以用一个锁来保护,就是直接全部用互斥锁来锁住,这样四种操作变成了只能异步操作,效率很低.
  
### (2)保护有关联性的多个资源
只要我们的**锁能覆盖所有受保护资源**就可以了,锁如果不指定参数那么默认就是this或者.class,这里有多个有关联的资源,所以要做到全覆盖,就要用到范围更大的.class,因为this是不只有一个.
这里给个代码
```java
class Account {
  private int balance;
  // 转账
  void transfer(Account target, int amt){
    synchronized(Account.class) {
      if (this.balance > amt) {
        this.balance -= amt;
        target.balance += amt;
      }
    }
  } 
}
```
确实解决了锁的覆盖的问题了,但是新的问题随之而来<font color=red>锁将所有的操作都变成了串行</font>就是每个用户执行转账操作都得排队,因为`.class`只有一个啊,这里<font color=red>锁的粒度太大了要缩小锁的范围</font>

针对这个问题继续简化代码
```java
class Account {
  private int balance;
  // 转账
  void transfer(Account target, int amt){
    // 锁定转出账户
    synchronized(this) {              
      // 锁定转入账户
      synchronized(target) {           
        if (this.balance > amt) {
          this.balance -= amt;
          target.balance += amt;
        }
      }
    }
  } 
}

```
这样的代码实现了只会锁定参加转账的双方,Atranfer(B),先锁定了A账号,在等待B账号,等到B账号资源后进行转账.但是依然造成了问题,就是下面的死锁问题(看专题)