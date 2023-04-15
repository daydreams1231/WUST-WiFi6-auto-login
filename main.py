import hashlib
import hmac
import json
import os
import socket
import sys
import time

import requests
from win10toast import ToastNotifier

from EncodeSources.Base64 import *
from EncodeSources.modules import *
from EncodeSources.Xencode import *

Debug = False

#User profile
username = ''
password = ''

account_name = socket.gethostname()

#检测wifi是否连接
while os.popen('netsh wlan show interfaces').read().find('已连接') == -1:
    print('Waiting for a certain connection...\n')
    time.sleep(0.5)
print('Ready to check...\n')

#检测WiFi可用性
while True:
    try:
        requests.get("http://59.68.177.183/srun_portal_pc?ac_id=7&theme=pro")
    except Exception as err:
        print('[Internal] Connection error : cannot access Internet.\n')
        time.sleep(0.5)
        continue
    break

#检测是否为目标wifi
if getWifiName() != 'WUST-WiFi6' :
    print('A wrong connection was detected, exiting...')
    sys.exit()
else :
    print(f'Welcome : {account_name} - Ready to login...\n')

#连接wifi : WUST-WiFi6 后进行后续操作
call_time = int(time.time()) * 1000 # int 格式
ip = socket.gethostbyname(account_name) # str 格式

#初始化Toast module
toast = ToastNotifier() 
callback = 'jQuery112402537284455192399_' + str(call_time)
header = {
    "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "close",
    "Cookie": "lang=zh-CN",
    "Host": "59.68.177.183",
    "Pragma": "no-cache",
    "Referer": "http://59.68.177.183/srun_portal_pc?ac_id=7&theme=pro",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

time.sleep(0.2)
#此步骤上传callback,后续用于请求认证,这步其实也能得到ip
requests.get('http://59.68.177.183/cgi-bin/rad_user_info', params = {
    'callback': callback,
    '_': call_time
},headers = header)

time.sleep(0.2)
#此步骤模拟点击登录后的操作，我们只需要此步返回的challenge值
response_2 = requests.get('http://59.68.177.183/cgi-bin/get_challenge', params = {
    'callback': callback,
    'username': username,
    'ip': ip,
    '_': call_time
},headers = header).text

challenge = json.loads(filterJSON(response_2))['challenge']

Debug == True and print(f'[Debug] Token ok : {challenge}\n')

#准备认证所需要的参数 i
#准备参数
info = json.dumps({
    "username" : username,
    "password" : password,
    "ip" : ip,
    "acid" : "7",
    "enc_ver" : "srun_bx1"
})
i = base64(xencode(info, challenge))

value = challenge + username
value += challenge + hmac.new(challenge.encode(), password.encode(), hashlib.md5).hexdigest()
value += challenge + '7'
value += challenge + ip
value += challenge + '200'
value += challenge + '1'
value += challenge + '{SRBX1}'+ i

#认证操作
time.sleep(0.2)
response_3 = requests.get('http://59.68.177.183/cgi-bin/srun_portal',params = {
    'callback': callback,
    'action': 'login',
    'username': username,
    'password': '{MD5}' + hmac.new(challenge.encode(), password.encode(), hashlib.md5).hexdigest(),
    'os': '鸡你太美OS v11.45.14',
    'name': 'Linux',
    'double_stack': '0',
    'chksum': hashlib.sha1(value.encode()).hexdigest(),
    'info': '{SRBX1}' + i,
    'ac_id': '7',
    'ip': ip,
    'n': '200',
    'type': '1',
    '_': call_time + 1
},headers = header).text
stats = filterJSON(response_3)
Debug == True and print(f'[Debug] Authentication ok : {stats}\n')


#判断返回值中是否有ServerFlag
if response_3.find('ServerFlag') != -1:
    #有
    if json.loads(stats)['ServerFlag'] == 0 :
        print("Wifi login : ok\n")
        #获取流量等信息
        time.sleep(0.2)
        res_json = json.loads(filterJSON(requests.get('http://59.68.177.183/cgi-bin/rad_user_info', params= {
            'callback' : callback,
            '_'  : time
        }).text))
        toast.show_toast(title="已成功自动登录WUST-WiFi6", msg="当前IP : " + ip + ' , 已用流量 : ' + str(int(res_json['sum_bytes']) / 1000000000 )[0:6] + ' GB', duration=6)
else :
    #无
    print("发生错误 ! \n")
    toast.show_toast(title="Failed to login !", msg="Please check error messages !", duration=6)
