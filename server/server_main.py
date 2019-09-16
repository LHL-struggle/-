import socket
import json
import threading
import server_hs

def client_chat(sock_conn, client_addr):
    try:
        while True:
                msg_len_data = sock_conn.recv(15)
                print(msg_len_data.decode())
                if not msg_len_data:
                    break

                msg_len = int(msg_len_data.decode().rstrip())
                recv_size = 0
                msg_content_data = b""
                while recv_size < msg_len:
                    tmp_data = sock_conn.recv(msg_len - recv_size)
                    if not tmp_data:
                        break
                    msg_content_data += tmp_data
                    recv_size += len(tmp_data)
                else:
                    print(msg_content_data.decode())
                    # 发送给其他所有在线的客户端
                    for sock_tmp, tmp_addr in client_socks:
                        if sock_tmp is not sock_conn:
                            try:
                                sock_tmp.send(msg_len_data)
                                sock_tmp.send(msg_content_data)
                            except:
                                client_socks.remove((sock_tmp, tmp_addr))
                                sock_tmp.close()
                    continue
                break
    finally:
            sock_conn.close()
            client_socks.remove((sock_conn, client_addr))



# 注册
def regist(sock_conn,req):
    rsp = {"op": 2, "error_code": 0}  # 0表注册成功
    # 校验用户名是否存在，校验通过返回0，校验失败返回非零（格式错误返回1，用户名已存在返回2）
    # 用户名校验通过
    if server_hs.check_user_name(req["args"]["uname"]) == 0:
        if not server_hs.user_reg(req["args"]["uname"], req["args"]["passwd"], req["args"]["phone"], req["args"]["email"]):
            rsp["error_code"] = 1  # 1表注册失败
    # 用户名格式错误
    elif server_hs.check_user_name(req["args"]["uname"]) == 1:
        rsp["error_code"] = 3
    # 用户名已存在
    elif server_hs.check_user_name(req["args"]["uname"]) == 2:
        rsp["error_code"] = 2

    # 将校验字典转化为字符串，并转为二进制
    rsp = json.dumps(rsp).encode()
    # 求取校验字典的大小，左对齐，宽度15，不足以空白补齐，在转换为二进制
    data_len = "{:<15}".format(len(rsp)).encode()
    print(rsp)
    # 发送数据大小
    sock_conn.send(data_len)
    # 发送数据
    sock_conn.send(rsp)
    # 关闭套接字
    sock_conn.close()

def main(client_socket, client_addr):
    # 接收客户端的消息
    data_len = client_socket.recv(15)
    print(data_len.decode())
    # 将接收的消息装换为字符型出去右边的空白符并将他装换为int型
    # 数据大小
    data_size = int(data_len.decode().rstrip())
    # 接收的数据大小
    recv_size = 0
    # 接收的数据内容
    recv_content = b''
    # 如果接收的数据小于文件大小，便一直接收
    while recv_size < data_size:
        recv_data = client_socket.recv(data_size-recv_size)
        if not recv_data:
            break
        # 已接收的数据大小
        recv_size += len(recv_data)
        # 已接收的数据内容
        recv_content += recv_data
    # 将接收的数据转换为字符型，在转为字典型
    recv_content = json.loads(recv_content.decode())
    print(recv_content, "数据")

    if recv_content["op"] == 1:
        print("op: 1")
        # 登录校验
        rsp = {"op": 1, "error_code": 0}  # 表示登录成功
        ''' check_uname_pwd(user_name, password)
            返回值：校验通过返回0，校验失败返回1
        '''
        if server_hs.check_uname_pwd(recv_content["args"]["uname"], recv_content["args"]["passwd"]):
            # 登录失败
            print('登录失败')
            rsp["error_code"] = 1
        rsp_1 = rsp
        # 将字典转换为字符串在转换为二进制
        rsp = json.dumps(rsp).encode()

        # 求取发送数据的大小，左对齐，宽度15，不足以空白补齐，在转换为二进制
        data_len = "{:<15}".format(len(rsp)).encode()
        # 发送数据大小
        client_socket.send(data_len)
        # 发送数据
        client_socket.send(rsp)


        # 如果登录校验成功，则向客户端发送文件
        if not rsp_1["error_code"]:
            client_chat(client_socket, client_addr)

    elif recv_content["op"] == 2:
        # 注册
        regist(client_socket, recv_content)




# 创建套接字
server_socket = socket.socket()
# 从IP_address.json文件里获取IP 和 port
IP_Port = tuple(eval(json.load(open("IP_address.json", encoding="utf-8"))["server_IP"]))
# 绑定地址与端口号
server_socket.bind(IP_Port)
# 监听套接字
server_socket.listen(5)
client_socks = []

while 1:
    # 等待连接
    client_socket, client_addr = server_socket.accept()
    print(client_addr, "连接")
    client_socks.append((client_socket, client_addr))
    # 每一个客户端便创建一个线程
    # target关联的函数，args以元组的形式传参，
    threading.Thread(target=main, args=(client_socket, client_addr)).start()




