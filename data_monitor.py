#iptables文件：iptables.txt   已注销账户：destory.txt  正常使用账户：using_account.txt  可用空闲账号：availavle_account
#所有文件均存放在/home/ss文件夹下
import os
import time
import re
import random
import fileinput

#初始化账户字典，每个端口对应4个数据，开始时间、当前时间、使用时间、使用流量、开始使用标志位(0未使用，1已使用)
account = {}
for i in range(10):
    account['838{0}'.format(i)]=['','',0,0,0]
    account['839{0}'.format(i)]=['','',0,0,0]

#注销账户（修改ss文件密码）并且将已销账户信息导入destroy.txt文件
def DestroyAccount(account,port):
    #修改config.json文件中对应所注销账户的端口密码
    file_ss_config = fileinput.input(r'/etc/shadowsocks/config.json', backup='.bak', inplace=1)
    for line in file_ss_config:
        if port in line:
            password = line.split('"')[-2]
            # print(password)
            # print(len(password))
            new_password = str(random.randint(904239875, 10000000000)) + chr(random.randint(97, 122))  # 随机生成11位数的密码
            # print(new_password)
            # print(len(new_password))
            a = line.replace(password, new_password)
            # print(line)
            print(a, end='')
        else:
            print(line, end='')
    file_ss_config.close()

    #重新启动ss服务
    os.system(r'ssserver -c /etc/shadowsocks/config.json -d stop')   #后台停止
    os.system(r'ssserver -c /etc/shadowsocks/config.json -d start')  # 后台启动

    file_destroy = open(r'/home/ss/destroy.txt', 'a')  #将过期用户备份到文件
    file_destroy.write(port+':'+str(account[port]))
    file_destroy.write('\n')
    file_destroy.close()
    account[port] = ['', '', 0, 0, 0]   #初始化端口

    os.system(r'iptables -Z INPUT {0}'.format(int(port[-1])+1))     #重置输入端口流量
    os.system(r'iptables -Z OUTPUT {0}'.format(int(port[-1])+1))    #重置输出端口流量





while True:                            #定时刷新读取数据，半小时刷新一次
    for i in range(10):
        account['838{0}'.format(i)][3] = 0  #每次更新数据时将流量数据项清零
        account['839{0}'.format(i)][3] = 0

    availavle_account = open(r'/home/ss/availavle_account.txt','w')  #先将空闲账号文件available_account.txt清空
    availavle_account.close()
    availavle_account = open(r'/home/ss/availavle_account.txt','a')  #然后打开文件，添加空闲账号列表

    NormalAccount = open(r'/home/ss/using_account.txt','w')
    NormalAccount.close()
    NormalAccount = open(r'/home/ss/using_account.txt','a')
    second_write_flag = 0

    os.system(r'iptables -nvL -x > /home/ss/iptables.txt')
    file = open(r'/home/ss/iptables.txt')                                #打开iptables.txt文件
    for line in file:
        if 'Chain OUTPUT' in line:
            second_write_flag = 1     #遍历上半部分端口时不进行写入
        port = line.split(':')[-1][:-1]     #找到每行的端口号，并且去除回车符
        if len(port) == 4:                  #找出端口为4位数的行，即找出十个开放端口
            number = re.compile(r'\d+')     #找到每一行的数字
            data = number.findall(line)[1]  #取每行的第二个数字
            #print(data)
            data = int(data)
            account[port][3] = account[port][3] + data              #读取流量使用信息
            if (account[port][4] == 0) and (account[port][3] >= 10000000):  #当端口流量大于10M时，标志账户开始使用，需要记录开始使用时间
                account[port][4] = 1
                account[port][0] = time.strftime("%Y-%m-%d %H:%M:%S")

            if account[port][4] == 1:                                 #正在使用的账户，需要进行日期更新，当前日期和使用时间
                account[port][1] = time.strftime("%Y-%m-%d %H:%M:%S")
                time_value = time.mktime(time.strptime(account[port][1], "%Y-%m-%d %H:%M:%S")) - time.mktime(time.strptime(account[port][0], "%Y-%m-%d %H:%M:%S"))
                account[port][2] = time_value
                if account[port][2] >= 2592000 or account[port][3] >= 53000000000:  #达到30天或者达到50G，停止服务，注销账户
                    DestroyAccount(account,port)        #停止账户的使用，并且将信息导入destroy.txt文件
            if account[port][4] == 0 and second_write_flag == 1:
                availavle_account.write(port)
                availavle_account.write('\n')
            elif account[port][4] == 1 and second_write_flag == 1:
                NormalAccount.write(port+':'+str(account[port]))
                NormalAccount.write('\n')

    availavle_account.close()
    NormalAccount.close()
    file.close()
    time.sleep(900)  #15分钟执行一次
    #time.sleep(600)


