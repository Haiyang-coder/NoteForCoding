# 后台线程做什么

- 刷新内存池中的数据，保证缓冲池中的数据是最新的数据
- 将脏页落盘

# iothread

- read thread:将数据页从磁盘加载到缓存页中
- write thread：将脏页落盘 buffer pool
- log thread：将log buffer落盘
- insert thread：将写缓冲区的内存刷新到磁盘change buffer 

# purge thread

在十五提交后，undo日志就没用了，这个线程就用来回收undo页