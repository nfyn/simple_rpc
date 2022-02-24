# simple_rpc
一个简易的RPC框架python实现，支持多线程(线程池管理)，服务端注册函数更方便

# RPC服务配置
## 服务端配置
- 在服务端进行注册函数
rpc_server.py
```python
from rpc.server import RpcServer


@RpcServer.register_function
def add(a: int, b: int, c: int = 10) -> int:
    return a + b + c


@RpcServer.register_function
def add1(a: int, b: int, c: int = 10) -> int:
    return a + b + c
```

# 启动RPC服务

- 启动服务端
```python
python rpc_server.py
```

- 启动客户端端
```python
python rpc_client.py
```
