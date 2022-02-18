# coding: utf-8

from rpc.server import RpcServer
import subprocess
import platform


@RpcServer.register_function
def add(a: int, b: int, c: int = 10) -> int:
    return a + b + c


@RpcServer.register_function
def add1(a: int, b: int, c: int = 10) -> int:
    return a + b + c


@RpcServer.register_function(name='command')
def command(cmd: str) -> str:
    """
    远程执行终端命令，并返回执行结果信息
    :param cmd: 命令字符串
    :return: 命令执行结果信息
    """
    proc = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # 优先返回错误信息
    sysstr = platform.system()
    if proc.stderr:
        if sysstr == "Windows":
            import chardet
            encoding = chardet.detect(proc.stderr).get('encoding', 'utf-8')
        else:
            encoding = 'utf-8'
        return proc.stderr.decode(encoding)

    if proc.stdout:
        if sysstr == "Windows":
            import chardet
            encoding = chardet.detect(proc.stdout).get('encoding', 'utf-8')
        else:
            encoding = 'utf-8'
        return proc.stdout.decode(encoding)


if __name__ == '__main__':
    with RpcServer(port=15000, max_workers=4) as server:
        server.serve_forever()
