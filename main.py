from adb_shell.adb_device import AdbDeviceTcp
import time
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

def time_c():
    return time.ctime().replace(":",".").replace(" ", "-")

#Generate adbkey before
adbkey = "./adbkey"

with open(adbkey) as f:
    priv = f.read()

with open(adbkey + ".pub") as f:
    pub = f.read()

signer = PythonRSASigner(pub, priv)

device = AdbDeviceTcp("192.168.122.35", "5555", default_transport_timeout_s=9.0)
device.connect(rsa_keys=[signer], auth_timeout_s=0.1)

response = device.shell("pm list permissions")
response_list = response.splitlines()


with open("std_pm") as std:
    std_list = std.read().splitlines()

duff_pm = set(response_list) - set(std_list)

with open(time_c() + ".txt", "w") as file1:
    file1.write(str(duff_pm))
    
print(f"{duff_pm}")



