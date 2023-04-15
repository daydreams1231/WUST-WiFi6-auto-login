import os

def getWifiName():
    str = os.popen('netsh wlan show interfaces').read()
    index = str.find("SSID")
    if index != -1 :
        return str[index:].split(':')[1].replace('\n','').replace('    BSSID','').replace(' ','')
    else :
        return False

def filterJSON(string):
    return string[42:-1]
