# tkinter 是 Python 的标准 GUI 库,GUI表示图形化界面
import tkinter as tk
# messagebox是tkinter中的消息框、对话框
import tkinter.messagebox
# 导入通信模块和线程模块
import socket
import threading
import json
from client_hs import register_user, passwd_md5
import client_hs
import re

# 注册函数
def zhuce():
    def usr_reg():
        # 得到输入的信息
        name = new_name.get()
        pwd = new_pwd.get()
        phone = usr_phone.get()
        email = usr_email.get()

        # 校验
        if not re.match("^[a-zA-Z0-9_]{6,15}$", name):
            tk.messagebox.showerror("用户名格式错误")
        else:
            zhuce_infor = {"op": 2, "args": {"uname": name, "passwd": pwd, "phone": phone, "email": email}}
            # 注册函数
            data = client_hs.register_user(zhuce_infor)
            # 0表注册成功，1表注册失败 2用户名已存在
            if data == 1:
                tk.messagebox.showerror("注册失败")
            if data == 2:
                tk.messagebox.showerror("用户名已存在")
            if data == 3:
                tk.messagebox.showerror("用户名格式错误")
            else:
                tk.messagebox.showinfo('注册成功')
                # 注册成功关闭注册框
                window_sign_up.destroy()

    # 新建注册界面
    window_sign_up = tk.Toplevel(denWnd)
    window_sign_up.geometry('400x300')
    window_sign_up.title('注册')

    # 用户名变量及标签、输入框
    new_name = tk.StringVar()
    tk.Label(window_sign_up, text='用户名：').place(x=10, y=10)
    tk.Entry(window_sign_up, textvariable=new_name).place(x=150, y=10)

    # 密码变量及标签、输入框
    new_pwd = tk.StringVar()
    tk.Label(window_sign_up, text='请输入密码：').place(x=10, y=50)
    tk.Entry(window_sign_up, textvariable=new_pwd, show='*').place(x=150, y=50)

    # 手机号输入框
    usr_phone = tk.StringVar()
    tk.Label(window_sign_up, text='手机号:').place(x=10, y=90)
    tk.Entry(window_sign_up, textvariable=usr_phone).place(x=150, y=90)

    # 邮箱输入框
    usr_email = tk.StringVar()
    tk.Label(window_sign_up, text='邮箱:').place(x=10, y=130)
    tk.Entry(window_sign_up, textvariable=usr_email).place(x=150, y=130)

    # 确认注册按钮及位置
    bt_confirm_sign_up = tk.Button(window_sign_up, text='确认注册', command=usr_reg).place(x=150, y=170)


def denlujm(sock):
    def on_send_msg():
        nick_name = "衔与彼寄"
        # 得到发送文本框的内容
        chat_msg = chat_msg_box.get(1.0, "end")
        # if chat_msg == "\n":
        #     return
        chat_data = nick_name + ":" + chat_msg
        chat_data = chat_data.encode()
        data_len = "{:<15}".format(len(chat_data)).encode()
        try:
            sock.send(data_len)
            sock.send(chat_data)
        except:
            # sock.close()
            tk.messagebox.showerror("温馨提示", "发送消息失败，请检查网络连接！")
        else:
            chat_msg_box.delete(1.0, "end")
            chat_record_box.configure(state=tk.NORMAL)
            chat_record_box.insert("end", chat_data.decode() + "\n")
            chat_record_box.configure(state=tk.DISABLED)

    def recv_chat_msg(sock):
        # 将sock设置为全局变量
        # global sock
        while True:
            try:
                while True:
                    msg_len_data = sock.recv(15)
                    if not msg_len_data:
                        break
                    msg_len = int(msg_len_data.decode().rstrip())
                    recv_size = 0
                    msg_content_data = b""
                    while recv_size < msg_len:
                        tmp_data = sock.recv(msg_len - recv_size)
                        if not tmp_data:
                            break
                        msg_content_data += tmp_data
                        recv_size += len(tmp_data)
                    else:
                        # chat_record_box聊天显示文本框
                        # state=tk.NORMAL 正常状态
                        chat_record_box.configure(state=tk.NORMAL)
                        # 在文本框中插入数据
                        print(msg_content_data.decode())
                        chat_record_box.insert("end", msg_content_data.decode() + "\n")
                        # 将按钮设置为，不可使用状态
                        chat_record_box.configure(state=tk.DISABLED)
                        continue
                    break
            finally:
                sock.close()
                sock = socket.socket()
                sock.connect(Conn_IP_address)

    # 创建聊天界面
    mainWnd = tk.Tk()
    # 更改窗口名称
    mainWnd.title("P1901班专属聊天室")
    # 显示聊天的文本框
    chat_record_box = tk.Text(mainWnd)
    # 将按钮设置为灰色状态，不可使用状态
    chat_record_box.configure(state=tk.DISABLED)
    # 设置文本框的外边框
    chat_record_box.pack(padx=10, pady=10)
    # 发送的文本框
    chat_msg_box = tk.Text(mainWnd)
    # 设置发送文本框的长度和高度
    chat_msg_box.configure(width=65, height=5)
    # 设置文本框的外边框
    chat_msg_box.pack(side=tk.LEFT, padx=10, pady=10)
    # Tkinter 按钮组件用于在 Python 应用程序中添加按钮，按钮上可以放上文本或图像，按钮可用于监听用户行为，
    # 能够与一个 Python 函数关联，当按钮被按下时，自动调用该函数。
    # 创建一个发送按钮，并与发送函数on_send_msg关联起来，当按下按键变调动函数发送数据
    send_msg_btn = tk.Button(mainWnd, text="发 送", command=on_send_msg)
    # 将按钮放于右边，内长15，内宽15，外边框长10，宽10
    send_msg_btn.pack(side=tk.RIGHT, padx=10, pady=10, ipadx=15, ipady=15)
    # 创建接收信息线程并启动，
    threading.Thread(target=recv_chat_msg, args=(sock,)).start()
    mainWnd.mainloop()



def denglu():
    # 得到输入的信息
    name = usr_name.get()
    pwd = usr_pwd.get()
    req = {"op": 1, "args": {"uname": name, "passwd": pwd}}

    # 创建客户端套接字
    client_socket = socket.socket()
    # 读取连接配置
    Conn_IP_address = tuple(eval(json.load(open('ClientConnIp.json', encoding='utf-8'))["Conn_IP_address"]))
    # 连接服务器
    client_socket.connect(Conn_IP_address)
    # 登陆信息
    req_uname = req["args"]["uname"]
    req_md5 = passwd_md5(req["args"]["passwd"].encode())  # 密码的MD5值
    req = {"op": 1, "args": {"uname": req_uname, "passwd": req_md5}}
    # 将字典转换为字符串在转为二进制
    req = json.dumps(req).encode()  # 文件内容
    # 求取文件大小，再将大小转换为字符型，宽度为15，不足用空格填充，最后转换为字节型
    len_req = str(len(req)).ljust(15).encode()
    # 发送登录文件大小
    client_socket.send(len_req)
    # 发送登陆文件内容
    client_socket.send(req)
    # 将接收的消息转换为字符型，且删除右边的的空白符合
    data_2 = client_socket.recv(15).decode().rstrip()
    if len(data_2) > 0:
        # 所要接收数据的大小
        len_data_2 = int(data_2)
        len_recv_2 = 0
        req_recv_2 = ''
        # 当接收的数据小于数据大小就一直接收
        while len_recv_2 < len_data_2:
            r_recv_2 = client_socket.recv(len_data_2 - len_recv_2).decode()
            if len(r_recv_2) == 0:
                break
            len_recv_2 += len(r_recv_2)  # 已接收的数据大小
            req_recv_2 += r_recv_2  # 已接收的数据
        # 将接收到的数据转换为字典
        req_recv_2 = dict(eval(req_recv_2))
        print(req_recv_2)
        # {"op": 1,"error_code": 0  # 0表示登录成功，1表示登录失败}
        # client_socket.close()
        data = req_recv_2["error_code"]

        if not data:
            # 聊天界面
            denlujm(client_socket)
        else:
            tk.messagebox.showerror(message='用户或密码不正确')


Conn_IP_address = tuple(eval(json.load(open('ClientConnIp.json', encoding='utf-8'))["Conn_IP_address"]))

# 注册界面
denWnd = tk.Tk()
# 界面名称
denWnd.title("聊天注册登陆界面")
# 登陆界面的宽高
denWnd.geometry('400x300')

# 标签
tk.Label(denWnd, text='用户名:').place(x=100, y=40)
tk.Label(denWnd, text='密码:').place(x=100, y=80)


# 用户名输入框
usr_name = tk.StringVar()
entry_usr_name = tk.Entry(denWnd, textvariable=usr_name)
entry_usr_name.place(x=160, y=40)

# 密码输入框
usr_pwd = tk.StringVar()
entry_usr_pwd = tk.Entry(denWnd, textvariable=usr_pwd)
entry_usr_pwd.place(x=160, y=80)

# 注册按钮
zhuce_b = tk.Button(denWnd, text="注册", command=zhuce)
zhuce_b.place(x=160, y=200)

# 登陆按钮
denglu_b = tk.Button(denWnd, text="登陆", command=denglu)
denglu_b.place(x=230, y=200)
denWnd.mainloop()
