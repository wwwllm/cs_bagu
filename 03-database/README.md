# 数据库（MySQL / Redis 核心八股与底层机制）

## 规划专题
- 01-mysql-innodb.md：B+ 树索引结构、聚簇索引 vs 二级索引、最左前缀原则
- 02-transactions-mvcc.md：事务 ACID 特性、四种隔离级别、Undo Log 与 ReadView 原理
- 03-locking-concurrency.md：行锁、间隙锁（Gap Lock）、Next-Key Lock 与死锁排查
- 04-redis-fundamentals.md：底层数据结构（SDS、跳表、压缩列表）、持久化机制（RDB/AOF）、缓存雪崩/击穿/穿透
