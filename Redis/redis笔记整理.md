# redis笔记整理

## redis的数据结构

### redis的查询为什么那么快呢

你要了解为什么块，你就得知道瓶颈会出现在哪里：网络io，cpu计算（key，value的查找计算），磁盘or内存寻址

1. 为了实现从键到值的快速访问，Redis 使用了一个哈希表来保存所有键值对。哈希表的最大好处很明显，就是让我们可以用 O(1) 的时间复杂度来快速查找到键值对——我们只需要计算键的哈希值，就可以知道它所对应的哈希桶位置，然后就可以访问相应的 entry 元素
2. 他用的是内存的存储，查找自然比磁盘的io快得多
3. 用的网络模型是io多路复用，处理网络io的能力特别的块

### 哈希表的冲突问题和 rehash 可能带来的操作阻塞，你怎么解决呢？

1. 采用拉链法来化解hash冲突：Redis 解决哈希冲突的方式，就是链式哈希。链式哈希也很容易理解，就是指**同一个哈希桶中的多个元素用一个链表来保存，它们之间依次用指针连接。**

2. 当链表的长度太长的时候进行rehash：也就是增加现有的哈希桶数量，让逐渐增多的 entry 元素能在更多的桶之间分散保存，减少单个桶中的元素数量，从而减少单个桶中的冲突。

**rehash的具体做法：**

Redis 默认使用了两个全局哈希表：哈希表 1 和哈希表 2。一开始，当你刚插入数据时，默认使用哈希表 1，此时的哈希表 2 并没有被分配空间。随着数据逐步增多，Redis 开始执行 rehash，这个过程分为三步：

1. 给哈希表 2 分配更大的空间，例如是当前哈希表 1 大小的两倍；
2. 把哈希表 1 中的数据重新映射并拷贝到哈希表 2 中；
3. 释放哈希表 1 的空间。

### rehash涉及大量的数据拷贝，会造成 Redis 线程阻塞，如何解决？

为了避免这个问题，Redis 采用了**渐进式 rehash**：

简单来说就是在第二步拷贝数据时，Redis 仍然正常处理客户端请求，每处理一个请求时，从哈希表 1 中的第一个索引位置开始，顺带着将这个索引位置上的所有 entries 拷贝到哈希表 2 中；等处理下一个请求时，再顺带拷贝哈希表 1 中的下一个索引位置的 entries。这样就巧妙地把一次性大量拷贝的开销，分摊到了多次处理请求的过程中，避免了耗时操作，保证了数据的快速访问。

### 集合有哪些底层数据结构

集合类型的底层数据结构主要有 5 种：整数数组、双向链表、哈希表、压缩列表和跳表。压缩列表和跳表我们平时接触得可能不多，但它们也是 Redis 重要的数据结构，所以我来重点解释一下。

**压缩表：**

压缩列表实际上类似于一个数组，数组中的每一个元素都对应保存一个数据。和数组不同的是，压缩列表在表头有三个字段 zlbytes、zltail 和 zllen，分别表示列表长度、列表尾的偏移量和列表中的 entry 个数；压缩列表在表尾还有一个 zlend，表示列表结束。在压缩列表中，如果我们要查找定位第一个元素和最后一个元素，可以通过表头三个字段的长度直接定位，复杂度是 O(1)。而查找其他元素时，就没有这么高效了，只能逐个查找，此时的复杂度就是 O(N) 了。

**跳表**

有序链表只能逐一查找元素，导致操作起来非常缓慢，于是就出现了跳表。具体来说，跳表在链表的基础上，增加了多级索引，通过索引位置的几个跳转，实现数据的快速定位。

### 每个集合支持的数据结构有哪些

首先：每个集合都支持两个的数据结构。其次，除了set其他都支持压缩列表。set单独支持一个整数数组，其他的根据集合的性质和数据结构的性质灵活推论。

### redis不同操作的复杂程度

1. 单元素操作是基础；
2. 范围操作非常耗时；
3. 统计操作通常高效；
4. 例外情况只有几个。

第一，**单元素操作，是指每一种集合类型对单个数据实现的增删改查操作**。例如，Hash 类型的 HGET、HSET 和 HDEL，Set 类型的 SADD、SREM、SRANDMEMBER 等。这些操作的复杂度由集合采用的数据结构决定，例如，HGET、HSET 和 HDEL 是对哈希表做操作，所以它们的复杂度都是 O(1)；

Set 类型用哈希表作为底层数据结构时，它的 SADD、SREM、SRANDMEMBER 复杂度也是 O(1)。这里，有个地方你需要注意一下，集合类型支持同时对多个元素进行增删改查，例如 Hash 类型的 HMGET 和 HMSET，Set 类型的 SADD 也支持同时增加多个元素。此时，这些操作的复杂度，就是由单个元素操作复杂度和元素个数决定的。例如，HMSET 增加 M 个元素时，复杂度就从 O(1) 变成 O(M) 了。

第二，**范围操作，是指集合类型中的遍历操作，可以返回集合中的所有数据**，比如 Hash 类型的 HGETALL 和 Set 类型的 SMEMBERS，或者返回一个范围内的部分数据，比如 List 类型的 LRANGE 和 ZSet 类型的 ZRANGE。**这类操作的复杂度一般是 O(N)，比较耗时，我们应该尽量避免**。

不过，Redis 从 2.8 版本开始提供了 SCAN 系列操作（包括 HSCAN，SSCAN 和 ZSCAN），这类操作实现了渐进式遍历，每次只返回有限数量的数据。这样一来，相比于 HGETALL、SMEMBERS 这类操作来说，就避免了一次性返回所有元素而导致的 Redis 阻塞。

第三，统计操作，是指**集合类型对集合中所有元素个数的记录**，例如 LLEN 和 SCARD。这类操作复杂度只有 O(1)，这是因为当集合类型采用压缩列表、双向链表、整数数组这些数据结构时，这些结构中专门记录了元素的个数统计，因此可以高效地完成相关操作。

第四，例外情况，是指某些数据结构的特殊记录，例如**压缩列表和双向链表都会记录表头和表尾的偏移量**。这样一来，对于 List 类型的 LPOP、RPOP、LPUSH、RPUSH 这四个操作来说，它们是在列表的头尾增删元素，这就可以通过偏移量直接定位，所以它们的复杂度也只有 O(1)，可以实现快速操作。



## redis的单线程模式

### 为什么说redis是单线程的？

Redis 是单线程，主要是==Redis 的网络 IO 和键值对读写是由一个线程来完成的==，这也是 Redis 对外提供键值存储服务的主要流程。但 Redis 的其他功能，比如持久化、异步删除、集群数据同步等，其实是由额外的线程执行的。

### 采用多线程有什么问题

1. 当有多个线程要修改这个共享资源时，为了保证共享资源的正确性，就需要有额外的机制进行保证，而这个额外的机制，就会带来额外的开销。这就是==多线程编程模式面临的共享资源的并发访问控制问题。==

2. 而且，采用多线程开发一般会引入同步原语来保护共享资源的并发访问，这也会降低系统代码的易调试性和可维护性。为了避免这些问题，Redis 直接采用了单线程模式。

所以从性能，难度，可维护性来说，单线程较好

### 为什么redis单线程那么快

1. 一方面，Redis 的大部分操作在==内存==上完成

2. 再加上它采用了==高效的数据结构==，例如哈希表和跳表，这是它实现高性能的一个重要原因。

3. ，就是 Redis 采用了==多路复用机制==，使其在网络 IO 操作中能并发处理大量的客户端请求，实现高吞吐率。（这个io多路复用机制是重中之重，所以要单独重点学习）



## redis的数据持久化之AOF日志

### AOF日志是如何实现的？

我们比较熟悉的是数据库的写前日志（Write Ahead Log, WAL），也就是说，在实际写数据前，先把修改的数据记到日志文件中，以便故障时进行恢复。不过，AOF 日志正好相反，它是写后日志，“写后”的意思是 Redis 是先执行命令，==把数据写入内存，然后才记录日志==。

### AOF为什么用写后记录的方式

1. 而 AOF 里记录的是 ==Redis 收到的每一条命令==，这些命令是以文本形式保存的。为了避免额外的检查开销，Redis 在向 AOF 里面记录日志的时候，并不会先去对这些命令进行语法检查。所以，如果先记日志再执行命令的话，日志中就有可能记录了错误的命令，Redis 在使用日志恢复数据时，就可能会出错。只有命令能执行成功，才会被记录到日志中，否则，系统就会直接向客户端报错。所以，Redis 使用写后日志这一方式的一大好处是，可以避免出现记录错误命令的情况。
2. 它是在命令执行后才记录日志，所以**不会阻塞当前的写操作**。

### AOF写日志的io操作卡顿？

对于这个问题，AOF 机制给我们提供了三个选择，也就是 AOF 配置项 appendfsync 的三个可选值。

- Always，同步写回：每个写命令执行完，立马同步地将日志写回磁盘；
- Everysec，每秒写回：每个写命令执行完，只是先把日志写到 AOF 文件的内存缓冲区，每隔一秒把缓冲区中的内容写入磁盘；
- No，操作系统控制的写回：每个写命令执行完，只是先把日志写到 AOF 文件的内存缓冲区，由操作系统决定何时将缓冲区内容写回磁盘。

针对避免主线程阻塞和减少数据丢失问题，==这三种写回策略都无法做到两全其美==。

### AOF文件太大了怎么办？

==重写机制==具有“多变一”功能。所谓的“多变一”，也就是说，旧日志文件中的多条命令，在重写后的新日志中变成了一条命令。就是会根据具体的操作来缩减合并命令，从而减少了命令的条数。

### AOF重写过程是怎么样的？

重写过程是由后台子进程 bgrewriteaof 来完成的，我把重写的过程总结为==一个拷贝，两处日志==。AOF重写日志是给日志瘦身，别搞混了

**一个拷贝：**

就是指，每次执行重写时，主线程 fork 出后台的 bgrewriteaof 子进程。然后，bgrewriteaof 子进程就可以在不影响主线程的情况下，逐一把拷贝的数据写成操作，记入重写日志。（这里你复习一下fork命令），他会将主进程资源复制（除了线程资源，而且也不是真正的物理复制，而是在修改进程资源的时候才会分配空间，否则会只读主进程的数据）

**两处日志**

第一处日志就是指正在使用的 主进程的AOF 日志，Redis 会把这个操作写到它的缓冲区。这样一来，即使宕机了，这个 AOF 日志的操作仍然是齐全的，可以用于恢复。而第二处日志，就是指新的 AOF 重写日志。这个操作也会被写到重写日志的缓冲区。这样，重写日志也不会丢失最新的操作。等到拷贝数据的所有操作记录重写完成后，重写日志记录的这些最新操作也会写入新的 AOF 文件，以保证数据库最新状态的记录。此时，我们就可以用新的 AOF 文件替代旧文件了。



## redis内存持久化之RDB



### RDB给哪些数据做了快照：

Redis 的数据都在内存中，为了提供所有数据的可靠性保证，它执行的是全量快照，也就是说，把内存中的所有数据都记录到磁盘中，这就类似于给 100 个人拍合影，把每一个人都拍进照片里。这样做的好处是，一次性记录了所有数据，一个都不少。

### RDP快照会不会阻塞主线程

Redis 提供了两个命令来生成 RDB 文件，分别是 save 和 bgsave。

- save：在主线程中执行，会导致阻塞；
- bgsave：创建一个子进程，专门用于写入 RDB 文件，避免了主线程的阻塞，这也是 Redis RDB 文件生成的默认配置。

好了，这个时候，我们就可以通过 bgsave 命令来执行全量快照，这既提供了数据的可靠性保证，也避免了对 Redis 的性能影响。

### 如果采用不会阻塞主线程的方式来生成RDB，快照时还能修改数据码

我们要知道bgsave虽然不会阻塞主线程，但是此时你==只能进行读操作，不能写操作==，为了快照而暂停写操作，肯定是不能接受的。所以这个时候，Redis 就会借助操作系统提供的写时复制技术（Copy-On-Write, COW），在执行快照的同时，正常处理写操作。





## redis主从数据同步

### 主从模式下的交流模式

实际上，Redis 提供了主从库模式，以保证数据副本的一致，主从库之间采用的是读写分离的方式。

- 读操作：主库、从库都可以接收；
- 写操作：首先到主库执行，然后，主库将写操作同步给从库。

### 为什么要采取读写分离的模式呢

如果客户端对同一个数据（例如 k1）前后修改了三次，每一次的修改请求都发送到不同的实例上，在不同的实例上执行，那么，这个数据在这三个实例上的副本就不一致了（分别是 v1、v2 和 v3）。在读取这个数据的时候，就可能读取到旧的值。

如果我们非要保持这个数据在三个实例上一致，就要涉及到加锁、实例间协商是否完成修改等一系列操作，但这会带来巨额的开销，当然是不太能接受的。

### 主从模式，主库承担了太多同步任务怎么办？

一次全量复制中，对于主库来说，需要完成两个耗时的操作：生成 RDB 文件和传输 RDB 文件。我们可以**通过“主 – 从 – 从”模式将主库生成 RDB 和传输 RDB 的压力，以级联的方式分散到从库上。**

简单来说，我们在部署主从集群的时候，可以手动选择一个从库（比如选择内存资源配置较高的从库），用于级联其他的从库。然后，我们可以再选择一些从库（例如三分之一的从库），在这些从库上执行如下命令，让它们和刚才所选的从库，建立起主从关系。

### 如果主从库的网络连接断开了怎么办？

主从库会采用增量复制的方式继续同步。听名字大概就可以猜到它和全量复制的不同：全量复制是同步所有数据，而增量复制只会把主从库网络断连期间主库收到的命令，同步给从库。



## 哨兵机制

### 哨兵机制是干嘛的？

哨兵其实就是一个运行在特殊模式下的 Redis 进程，主从库实例运行的同时，它也在运行。哨兵主要负责的就是三个任务：==监控、选主（选择主库）和通知==。

监控是指哨兵进程在运行时，周期性地给所有的主从库发送 PING 命令，检测它们是否仍然在线运行。如果从库没有在规定时间内响应哨兵的 PING 命令，哨兵就会把它标记为“下线状态”；同样，如果主库也没有在规定时间内响应哨兵的 PING 命令，哨兵就会判定主库下线，然后开始自动切换主库的流程。

这个流程首先是执行哨兵的第二个任务，选主。主库挂了以后，哨兵就需要从很多个从库里，按照一定的规则选择一个从库实例，把它作为新的主库。这一步完成后，现在的集群里就有了新主库。

然后，哨兵会执行最后一个任务：通知。在执行通知任务时，哨兵会把新主库的连接信息发给其他从库，让它们执行 replicaof 命令，和新主库建立连接，并进行数据复制。同时，哨兵会把新主库的连接信息通知给客户端，让它们把请求操作发到新主库上。

### 哨兵在完成监控，选择主库，通知的过程中需要做什么决策

- 在监控任务中，哨兵需要判断主库是否处于下线状态；
- 在选主任务中，哨兵也要决定选择哪个从库实例作为主库。

通常会采用多实例组成的集群模式进行部署，这也被称为==哨兵集群==。当有 N 个哨兵实例时，最好要有 N/2 + 1 个实例判断主库为“主观下线”，才能最终判定主库为“客观下线”。

以分别按照三个规则依次进行三轮打分，这三个规则分别是==从库优先级、从库复制进度以及从库 ID 号==。只要在某一轮中，有从库得分最高，那么它就是主库了，选主过程到此结束。如果没有出现得分最高的从库，那么就继续进行下一轮。

### 哨兵对其他哨兵和主从的状态都是怎么知道的

- 基于 pub/sub 机制的哨兵集群组成过程；（了解集群中其他哨兵的存在）
- 基于 INFO 命令的从库列表，这可以帮助哨兵和从库建立连接；（连接主从的redis关系）
- 基于哨兵自身的 pub/sub 功能，这实现了客户端和哨兵之间的事件通知。


Redis 的发布订阅模式是通过 Redis 的服务器内部实现的。下面是大致的工作流程：

1. **订阅者订阅频道**：
   - 当一个客户端使用 `SUBSCRIBE` 命令订阅一个频道时，Redis 服务器会将该客户端添加到频道的订阅者列表中。
2. **发布者发布消息**：
   - 当一个客户端使用 `PUBLISH` 命令发布消息到某个频道时，Redis 服务器会将该消息发送给所有订阅了该频道的客户端。
3. **消息传递**：
   - Redis 服务器会维护每个频道的订阅者列表，并在接收到发布者发布消息后，遍历该频道的订阅者列表，将消息发送给所有订阅者。
4. **无阻塞**：
   - 发布者发布消息后不会等待订阅者的确认，而是直接发布消息，订阅者可以在任何时间接收到消息。这使得发布者和订阅者之间是无阻塞的，可以独立地进行消息的发布和订阅。
5. **取消订阅**：
   - 当一个客户端使用 `UNSUBSCRIBE` 命令取消对某个频道的订阅时，Redis 服务器会将该客户端从频道的订阅者列表中移除。

Redis 的发布订阅模式是在服务器内部通过订阅者列表来实现的，每个频道都有一个对应的订阅者列表，服务器负责维护这些列表并在接收到消息时将消息发送给所有订阅了该频道的客户端。这种设计使得发布者和订阅者之间是解耦的，可以实现高效的消息传递。

### 哨兵选举leader哨兵的要求

希望由自己来执行主从切换，并让所有其他哨兵进行投票，任何一个想成为 Leader 的哨兵，要满足两个条件：第一，拿到半数以上的赞成票；第二，拿到的票数同时还需要大于等于哨兵配置文件中的 quorum 值。





## redis的切片集群

### redis在持久化大数据会遇到什么问题，如何解决

在使用 RDB 进行持久化时，Redis 会 fork 子进程来完成，fork 操作的用时和 Redis 的数据量是正相关的，而 fork 在执行时会阻塞主线程。数据量越大，fork 操作造成的主线程阻塞的时间越长。因为fork要把主线程的页表拷贝给子进程，所以越大拷贝时间越长，fork卡顿的时间就越长。

切片集群，也叫分片集群，就是指启动多个 Redis 实例组成一个集群，然后按照一定的规则，把收到的数据划分成多份，每一份用一个实例来保存。

### redis切片集群需要解决：如何划分槽，如何找到槽（这里着重学习一下哈希槽）

- 数据切片后，在多个实例之间如何分布？
- 客户端怎么确定想要访问的数据在哪个实例上？

Redis Cluster 方案采用哈希槽（Hash Slot，接下来我会直接称之为 Slot），来处理数据和实例之间的映射关系。在 Redis Cluster 方案中，一个切片集群共有 16384 个哈希槽，这些哈希槽类似于数据分区，每个键值对都会根据它的 key，被映射到一个哈希槽中。

**具体的映射过程：**

- 使用 cluster create 命令创建集群，此时，Redis 会自动把这些槽平均分布在集群实例上。例如，如果集群中有 N 个实例，那么，每个实例上的槽个数为 16384/N 个。
- Redis 实例会把自己的哈希槽信息发给和它相连接的其它实例，来完成哈希槽分配信息的扩散。当实例之间相互连接后，每个实例就有所有哈希槽的映射关系了。

- 客户端为什么可以在访问任何一个实例时，都能获得所有的哈希槽信息呢。
- 首先根据键值对的 key，得到 0~16383 范围内的模数，每个模数代表一个相应编号的哈希槽，根据哈希槽访问具体的实例

### redis切片集群需要解决：新增或者删除节点，或者需要做一次负载均衡怎么办

Redis Cluster 方案提供了一种**重定向机制**，所谓的“重定向”，就是指，客户端给一个实例发送数据读写操作时，这个实例上并没有相应的数据，客户端要再给一个新实例发送操作命令。客户端把一个键值对的操作请求发给一个实例时，如果这个实例上并没有这个键值对映射的哈希槽，那么，这个实例就会给客户端返回下面的 MOVED 命令响应结果，这个结果中就包含了新实例的访问地址。

> ```java
> GET hello:key
> (error) MOVED 13320 172.16.19.5:6379
> ```

### 如何做到负载均衡——一致性哈希算法

一致性哈希（Consistent Hashing）算法。这是一种常用于分布式系统中的哈希算法，它可以在节点动态增减时尽量减少数据的重新分布，同时保持负载均衡。

在 Redis 中，一致性哈希算法被用于实现集群中的数据分片和节点的选择。基本思想是将整个哈希值空间划分成一个环（hash ring），每个节点在环上有一个对应的位置。将数据的哈希值映射到环上，并选择最接近该哈希值的节点作为数据的存储节点。

这种哈希环码的具体实现包括：

1. **节点的选择**：每个节点在环上有一个对应的位置，通常使用节点的 IP 地址或名称的哈希值作为其在环上的位置。对于一个给定的键，找到离该键哈希值最近的节点，并将数据存储到该节点上。
2. **数据分片**：将数据的哈希值映射到环上，然后根据环上节点的位置将数据分配给相应的节点。当节点数量发生变化时（如节点增减），只需要重新分配环上的部分数据，而不需要对所有数据进行重新分片。
3. **虚拟节点**：为了解决节点不均匀的问题，可以引入虚拟节点。即每个物理节点在环上对应多个虚拟节点，这样可以使得数据在环上分布更加均匀，避免某个节点负载过重。

Redis 中的一致性哈希算法使得数据的分片和节点的选择具有高效性和可扩展性，同时保证了负载均衡和数据分布的一致性。



