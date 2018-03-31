import os

for i in range(20):         #先删除所有端口
    os.system(r'iptables -D INPUT 1 && iptables -D OUTPUT 1')
for i in range(10):         #添加8380-8389十个端口
    os.system(r'iptables -A INPUT -p tcp --dport 838{0} -j ACCEPT && iptables -A OUTPUT -p tcp --sport 838{1} -j ACCEPT'.format(i,i))
    os.system(r'iptables -A INPUT -p tcp --dport 839{0} -j ACCEPT && iptables -A OUTPUT -p tcp --sport 839{1} -j ACCEPT'.format(i, i))