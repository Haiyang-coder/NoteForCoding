## Socket 编程

<img src="./page/image-20240527100722807.png" alt="image-20240527100722807" style="zoom: 67%;" />

### listen 时候参数 backlog 的意义？

```c
int listen (int socketfd, int backlog)
    
```

- 参数一 socketfd 为 socketfd 文件描述符
- 参数二 backlog，这参数在历史版本有一定的变化**现在通常认为 backlog 是 accept 队列。** **但是上限值是内核参数 somaxconn 的大小，也就说 accpet 队列长度 = min(backlog, somaxconn)。**

Linux内核中会维护两个队列：

- 半连接队列（SYN 队列）：接收到一个 SYN 建立连接请求，处于 SYN_RCVD 状态；
- 全连接队列（Accpet 队列）：已完成 TCP 三次握手过程，处于 ESTABLISHED 状态；

<img src="./page/image-20240527100943088.png" alt="image-20240527100943088" style="zoom:67%;" />

###  accept 发生在三次握手的哪一步

<img src="./page/image-20240527101045603.png" alt="image-20240527101045603" style="zoom:67%;" />

从上面的描述过程，我们可以得知**客户端 connect 成功返回是在第二次握手，服务端 accept 成功返回是在三次握手成功之后。**

### 客户端调用 close 了，连接是断开的流程是什么？

<img src="./page/image-20240527101150890.png" alt="image-20240527101150890" style="zoom:67%;" />

###  没有 accept，能建立 TCP 连接吗？

答案：**可以的**。

accpet 系统调用并不参与 TCP 三次握手过程，它只是负责从 TCP 全连接队列取出一个已经建立连接的 socket，用户层通过 accpet 系统调用拿到了已经建立连接的 socket，就可以对该 socket 进行读写操作了。



### 没有 listen，能建立 TCP 连接吗？

答案：**可以的**。

客户端是可以自己连自己的形成连接（**TCP自连接**），也可以两个客户端同时向对方发出请求建立连接（**TCP同时打开**），这两个情况都有个共同点，就是**没有服务端参与，也就是没有 listen，就能 TCP 建立连接。**