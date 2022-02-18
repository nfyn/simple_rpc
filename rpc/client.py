# coding: utf-8
import json
import socket
from struct import pack, unpack


class RpcClient:

    def __init__(self, host, port):
        self.host, self.port = host, port
        # 创建套接字
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 连接服务端
        self._socket.connect((self.host, self.port))
        print("tcp://{0}:{1}\n可用函数：\n{2}".format(self.host, self.port, '\n'.join(self.functions)))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._socket.close()

    @property
    def functions(self):
        """
        获取服务器可用函数列表
        :return: 服务端可用函数列表
        """
        response = self.list_functions()
        return json.loads(response).get('result', [])

    def __getattr__(self, function):
        """
        动态添加服务端函数到客户端实例上
        :param function: 函数名称
        :return: 函数
        """
        def _func(*args, **kwargs):
            # 客户端请求参数
            params = {'method_name': function, 'method_args': args, 'method_kwargs': kwargs}
            buffer = json.dumps(params).encode('utf-8')
            # 客户端发送请求信息包长度
            self._socket.sendall(pack('i', len(buffer)))
            # 客户端发送请求
            self._socket.sendall(buffer)
            # 解析服务端返回信息
            response_msg = self._socket.recv(4)
            response = None
            if response_msg:
                # 获取服务端响应包长度
                length = unpack('i', response_msg)[0]
                # 获取服务端响应包
                data = []
                while length > 0:
                    tmp = self._socket.recv(length)
                    data.append(tmp)
                    length = length - len(tmp)
                response = b''.join(data).decode('utf-8')
            return response

        setattr(self, function, _func)
        return _func


if __name__ == '__main__':
    with RpcClient('localhost', 15000) as client:
        res = client.add(1, 14)
        print(res)
        res = client.command("pwd")
        print(res)
