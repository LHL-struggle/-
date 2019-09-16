from socket import *
import socket
import hashlib
import os
import time
import json
import re
def md5(file_path):
    m = hashlib.md5()
    with open(file_path, "rb") as f:
        while True:
            data = f.read(1024)
            if len(data) == 0:
                break
            m.update(data)
    return m.hexdigest().upper()       # 大写

def passwd_md5(passwd):
    m = hashlib.md5()
    m.update(passwd)
    return m.hexdigest().upper()       # 大写

# 本地校验用户名/密码
def check(uname):
    '''
        函数功能：校验用户名是否合法
        函数参数：
        user_name 待校验的用户名
        返回值：校验通过返回0，校验失败返回1
        '''
    # [a-zA-Z0-9_]{6, 15}
    if not re.match("^[a-zA-Z0-9_]{6,15}$", uname):
        return 1
    else:
        return 0


def check_phone(phone):
    '''
    函数功能：校验手机号格式是否合法
    函数参数：
    phone 待校验的手机号
    返回值：校验通过返回0，校验错误返回1
    '''
    if re.match("^1\d{10}$", phone):
        return 0
    return 1


# 注册
def register_user(req):
    # 创建套接字
    client_socket = socket.socket()
    # 读取连接配置
    Conn_IP_address = tuple(eval(json.load(open('ClientConnIp.json', encoding='utf-8'))["Conn_IP_address"]))
    # 连接服务器
    client_socket.connect(Conn_IP_address)

    # 注册新用户
    req["args"]["passwd"] = passwd_md5(req["args"]["passwd"].encode())  # 密码的MD5值
    print(req)
    # 将字典转换为字符串在转为二进制
    req = json.dumps(req).encode()              # 文件内容
    # 求取文件大小，再将大小转换为字符型，宽度为15，不足用空格填充，最后转换为字节型
    len_req = str(len(req)).ljust(15).encode()
    # 发送注册文件大小
    client_socket.send(len_req)
    # 发送注册文件内容
    client_socket.send(req)
    # {"op": 2,"error_code": 0  # 0表示注册成功，1表示注册失败}
    # 将接收的消息转换为字符型，且删除右边的的空白符合
    data_2 = client_socket.recv(15).decode().rstrip()

    if len(data_2) > 0:
        # 所要接收数据的大小
        len_data_2 = int(data_2)
        len_recv_2 = 0
        req_recv_2 = ''
        while len_recv_2 < len_data_2:
        # 当接收的数据小于数据大小就一直接收
            r_recv_2 = client_socket.recv(len_data_2 - len_recv_2).decode()
            if len(r_recv_2) == 0:
                break
            len_recv_2 += len(r_recv_2)  # 已接收的数据大小
            req_recv_2 += r_recv_2       # 已接收的数据
        # 将接收到的数据转换为字典
        req_recv_2 = dict(eval(req_recv_2))
        client_socket.close()
        print(req_recv_2)
        # error_code0表注册成功，1表注册失败 2用户名已存在，3格式错误
        return req_recv_2["error_code"]
    else:
        client_socket.close()