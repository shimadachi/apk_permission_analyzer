import os
import time
from datetime import datetime
from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
import libvirt


class MalwareAnalyzer:
    def __init__(self, ip, port, adbkey_path, apk_dir, snapshot_name):
        self.ip = ip
        self.port = port
        self.adbkey_path = adbkey_path
        self.apk_dir = apk_dir
        self.snapshot_name = snapshot_name
        self.device = None

    def formatted_time(self):
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def adb_connect(self):
        with open(self.adbkey_path) as f:
            priv = f.read()
        with open(self.adbkey_path + ".pub") as f:
            pub = f.read()
        signer = PythonRSASigner(pub, priv)
        self.device = AdbDeviceTcp(self.ip, self.port)
        self.device.connect(rsa_keys=[signer])

    def install_apk(self, apk_path):
        self.device.push(apk_path, "/data/local/tmp/temp.apk")
        self.device.shell("pm install /data/local/tmp/temp.apk")

    def grant_all_permissions(self, package_name):
        permissions = self.device.shell(f"dumpsys package {package_name} | grep permission:")
        for line in permissions.splitlines():
            if "granted=false" in line:
                perm = line.split(" ")[-1]
                self.device.shell(f"pm grant {package_name} {perm}")

    def get_granted_permissions(self, package_name):
        response = self.device.shell(f"dumpsys package {package_name}")
        lines = response.splitlines()
        granted = [line.strip() for line in lines if "granted=true" in line]
        return granted

    def get_package_name(self, apk_path):
        return self.device.shell(f"pm dump /data/local/tmp/temp.apk | grep packageName").split("=")[-1].strip()

    def reset_snapshot(self):
        conn = libvirt.open("qemu://system")
        dom = conn.lookupByName("blissos-guest")
        snapshot = dom.snapshotLookupByName(self.snapshot_name)
        dom.revertToSnapshot(snapshot)
        conn.close()

    def analyze_apks(self):
        apk_files = [f for f in os.listdir(self.apk_dir) if f.endswith(".apk")]

        for apk in apk_files:
            apk_path = os.path.join(self.apk_dir, apk)
            print(f"[+] Analyzing {apk}...")

            self.reset_snapshot()
            time.sleep(20)  # snapshot’tan dönmenin tamamlanmasını bekle

            self.adb_connect()

            self.install_apk(apk_path)
            package_name = self.device.shell("pm list packages -f").split("/")[-1].strip().replace("\r", "")
            self.grant_all_permissions(package_name)

            granted_perms = self.get_granted_permissions(package_name)

            log_filename = f"logs/{self.formatted_time()}_{apk}.txt"
            os.makedirs("logs", exist_ok=True)
            with open(log_filename, "w") as log_file:
                log_file.write(f"APK: {apk}\n")
                log_file.write(f"Package: {package_name}\n")
                log_file.write("Granted Permissions:\n")
                log_file.writelines([perm + "\n" for perm in granted_perms])

            print(f"[✓] Finished {apk}, results saved to {log_filename}\n")


if __name__ == "__main__":
    analyzer = MalwareAnalyzer(
        ip="192.168.122.101",          # Android VM IP (qemu NAT varsayılan IP)
        port=5555,
        adbkey_path="adbkey",
        apk_dir="apks",
        snapshot_name="clean-snap"
    )
    analyzer.analyze_apks()
