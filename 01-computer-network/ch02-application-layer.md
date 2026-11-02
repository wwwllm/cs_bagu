# 计算机网络第二章：应用层核心八股（P2P 之前）

> 进度状态：正在进行单题模拟面试拷打中（当前停留在 DNS 核心概念）。

---

## 知识框架（P2P 协议之前）

```
应用层
├── 1. 应用层体系与进程通信
│   ├── C/S 架构 vs P2P 架构
│   ├── 套接字（Socket）：应用层与传输层的门脸接口（IP + 端口）
│   └── 传输层提供的服务维度：可靠性、吞吐量保证、定时要求、安全性
├── 2. DNS（域名系统）—— 应用层服务于应用层/网络基础设施
│   ├── 体系结构：根 DNS -> 顶级域 (TLD) -> 权威 DNS + 本地 DNS (LDNS)
│   ├── 解析流程：递归查询 vs 迭代查询
│   ├── 协议选型：默认 UDP 53，何时切换 TCP（区域传送 AXFR / 报文超过 512 字节 / EDNS0 截断）
│   └── DNS 记录类型：A、AAAA、CNAME、NS、MX
└── 3. Web 与 HTTP 协议
    ├── HTTP 版本演进：
    │   ├── HTTP/1.0：短连接（非持续连接），每次资源请求经历 TCP 三次握手
    │   ├── HTTP/1.1：默认长连接（持续连接），引入流水线（Pipeline，但仍有队头阻塞），Host 请求头，分块传输
    │   └── HTTP/2.0：二进制分帧、多路复用（彻底解决 HTTP 队头阻塞，但 TCP 队头阻塞仍存）、头部压缩（HPACK）、服务端推送
    ├── 状态管理：Cookie 与 Session 的机制及安全（HttpOnly, Secure, SameSite）
    ├── 缓存机制与条件 GET：
    │   ├── 强缓存：Cache-Control (max-age, no-cache, no-store), Expires
    │   ├── 协商缓存（条件 GET）：Last-Modified / If-Modified-Since vs ETag / If-None-Match
    │   └── 缓存命中与状态码：200 (from memory/disk cache), 304 Not Modified
    └── 高频状态码辨析：
        ├── 2xx：200 OK, 204 No Content, 206 Partial Content
        ├── 3xx：301 永久重定向（缓存且利于 SEO） vs 302 临时重定向 vs 304 缓存未修改
        ├── 4xx：400 Bad Request, 401 Unauthorized（未认证）, 403 Forbidden（无权限）, 404 Not Found
        └── 5xx：500 Internal Error, 502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout
```

---

## 高频面试题跟踪

### Q1. DNS 解析流程与查询模式（待答）
- 本地、根、顶级、权威四级职责。
- 完整未命中缓存解析路径。
- 递归与迭代本质区别与互联网标准设计考量（为什么根不采用递归？保护根服务器计算与连接资源）。

### Q2. DNS 为什么基于 UDP，何时用 TCP？（待答）
- 性能考量：UDP 无握手、开销小、查询响应快。
- 切换场景：响应报文 > 512 字节（TC 标志位置 1 触发客户端重发 TCP 查询）；主从 DNS 区域传送（Zone Transfer）需可靠性保证。

### Q3. HTTP/1.0 vs HTTP/1.1 与队头阻塞（待答）
- 非持续连接（2 RTT + 传输时间） vs 持续连接（Keep-Alive）。
- 管线化（Pipeline）只能保证请求并行发出，但响应必须按顺序返回，队首响应慢依然导致队头阻塞。

### Q4. 条件 GET 与缓存机制（待答）
- 304 Not Modified 交互过程。
- 为什么需要 ETag：秒级以内频繁修改、文件修改时间变但内容没变、分布式集群各节点时间戳不一致。

### Q5. 核心状态码深度辨析（待答）
- 301 vs 302。
- 401 vs 403。
