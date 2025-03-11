from adb_shell.adb_device import AdbDeviceTcp
import time
from adb_shell.auth.sign_pythonrsa import PythonRSASigner

class PermissionScript:
    def __init__(self,ip, port,adbkey, text ):
        self.ip = ip
        self.port = port
        self.text = text
        self.adbkey = adbkey
        
    def time_c(self):
        return time.ctime().replace(":",".").replace(" ", "-")

    def adb_connection(self):

        with open(self.adbkey) as f:
            priv = f.read()

        with open(self.adbkey + ".pub") as f:
            pub = f.read()

        signer = PythonRSASigner(pub, priv)

        self.device = AdbDeviceTcp(self.ip, self.port, default_transport_timeout_s=9.0)
        self.device.connect(rsa_keys=[signer], auth_timeout_s=0.1)

    def pm_diff(self):
        self.adb_connection()

        #Generate adbkey before
        response = self.device.shell("pm list permissions")
        response_list = response.splitlines()


        with open("std_pm") as std:
            std_list = std.read().splitlines()

        duff_pm = set(response_list) - set(std_list)

        with open(self.time_c() + ".log", "w") as file1:
            file1.write(str(duff_pm))
            
        print(f"{duff_pm}")


if __name__ == "__main__":
    pm_script = PermissionScript("192.168.122.35","5555","./adbkey","std_pm")
    pm_script.pm_diff()





