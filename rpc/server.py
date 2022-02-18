# coding: utf-8

import json
import socket
from functools import partial
from inspect import signature
import logging
from struct import pack, unpack
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(filename)s line:%(lineno)d] %(levelname)s: %(message)s')


class RpcServer:
    _funcs = {}
    instance = None

    def __init__(self, port, host='0.0.0.0', max_workers=None):
        self.host, self.port = host, port
        # 创建套接字
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 解决程序端口占用问题
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 绑定本地ip地址
        self._socket.bind((self.host, self.port))
        # 将套接字变为监听套接字，最大连接数量设置为100
        self._socket.listen(100)
        # 创建线程池，设置线程数量
        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        logging.info('RPC Server Start, listen {0} ...'.format(self.port))

    def serve_forever(self):
        while True:
            # 等待设备连接(通过ip地址和端口建立tcp连接)
            conn_socket, conn_address = self._socket.accept()

            # 线程池处理客户端请求
            t = self._thread_pool.submit(self._handle_request, conn_socket)
            t.done()

    def _handle_request(self, conn_socket):
        try:
            while True:
                # 获取客户端请求信息
                conn_address = conn_socket.getpeername()
                request_msg = conn_socket.recv(4)
                if request_msg:
                    # 获取请求包长度
                    length = unpack('i', request_msg)[0]
                    data = []
                    while length > 0:
                        tmp = conn_socket.recv(length)
                        data.append(tmp)
                        length = length - len(tmp)
                    data = b''.join(data).decode('utf-8')
                    param_dict = json.loads(data)
                    param_dict['ip'] = '{0}:{1}'.format(conn_address[0], conn_address[1])
                    logging.info('{0}'.format(param_dict))
                    data = self._call_method(**param_dict)
                    # 服务端发送响应信息包长度
                    conn_socket.sendall(pack('i', len(data)))
                    # 响应客户端请求信息
                    conn_socket.sendall(data)
                else:
                    logging.info('客户端 {0}:{1} 断开连接...'.format(conn_address[0], conn_address[1]))
                    # 关闭套接字
                    conn_socket.close()
                    break
        except ConnectionResetError:
            logging.info('客户端 {0}:{1} 强制中断连接...'.format(conn_address[0], conn_address[1]))
            # 关闭套接字
            conn_socket.close()

    def _call_method(self, **kwargs):
        method_name = kwargs.pop('method_name')
        method_args = kwargs.pop('method_args')
        method_kwargs = kwargs.pop('method_kwargs')
        res = None
        err_msg = None

        # 先从实例方法里查找，若没有，从_funcs里查找，若_funcs里没有此方法，返回None
        func = getattr(self, method_name, self._funcs.get(method_name, None))
        if func is not None:
            res = func(*method_args, **method_kwargs)
        else:
            err_msg = 'method {0} is not supported'.format(method_name)

        data = {}
        if res:
            data.update({'result': res})
        if err_msg:
            data.update({'error message': err_msg})
        return json.dumps(data).encode('utf-8')

    @classmethod
    def register_function(cls, function=None, name=None):
        # decorator factory
        if function is None:
            return partial(cls.register_function, name=name)

        if name is None:
            name = function.__name__
        cls._funcs[name] = function

    def list_functions(self):
        func_lst = []
        for name, function in self._funcs.items():
            func_lst.append('{0}{1}{2}'.format(name, signature(function), function.__doc__ or '\n'))
        return func_lst

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._thread_pool.shutdown()
        self._socket.close()


if __name__ == '__main__':
    with RpcServer(port=15000) as server:
        server.serve_forever()
