
![](https://img.shields.io/badge/python-3.x-blue?logo=python&labelColor=lightblue&logoColor=blue)
![](https://img.shields.io/badge/RPC-blueviolet)
# simple_rpc
一个简易的RPC框架python实现，支持多线程(线程池管理)，服务端注册函数，更方便简洁

# 特点
1. 服务端注册函数，采用`RpcServer.register_function`装饰器进行注册，简洁方便；
2. 服务端采用多线程设计，可进行线程池配置；
3. 客户端与服务端直接数据传输，进行了数据长度校验，可防止粘包问题；
4. 客户端连接到服务端后，会自动打印服务端可调用的函数，采用的是长连接，可多次调用不同函数；

# RPC服务配置
## 服务端配置
- 在服务端进行注册函数 \
**rpc_server.py**
```python
from rpc.server import RpcServer


@RpcServer.register_function
def add(a: int, b: int, c: int = 10) -> int:
    return a + b + c


@RpcServer.register_function(name='add1')
def add1(a: int, b: int, c: int = 10) -> int:
    return a + b + c
```
- 服务端端口配置
    - **`port`**:端口
    - **`max_workers`**:线程池最大线程数
```python
if __name__ == '__main__':
    with RpcServer(port=15000, max_workers=4) as server:
        server.serve_forever()
```

## 客户端配置
**rpc_client.py**
- **`host`**:远程服务端ip地址
- **`port`**:端口
```python
import time
from rpc.client import RpcClient

if __name__ == '__main__':
    with RpcClient(host='localhost', port=15000) as client:
        for i in range(100):
            res = client.add(1, 14)
            print(res)
            time.sleep(3)
```

# 启动RPC服务

- 启动服务端
```python
python rpc_server.py
```
![rpc server start](https://cdn.jsdelivr.net/gh/nfyn/image_host/rpc_server_start.png)

- 启动客户端端
```python
python rpc_client.py
```
![rpc client start](https://cdn.jsdelivr.net/gh/nfyn/image_host/rpc_client_start.png)
