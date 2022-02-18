# coding: utf-8

import time
from rpc.client import RpcClient

if __name__ == '__main__':
    with RpcClient(host='localhost', port=15000) as client:
        for i in range(100):
            res = client.add(1, 14)
            print(res)
            time.sleep(3)
