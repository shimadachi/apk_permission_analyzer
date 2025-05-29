import os
import time
from datetime import datetime
import libvirt
import subprocess


class MalwareAnalyzer:
    def __init__(self, ip, port, apk_dir, snapshot_name):
        self.ip = ip
        self.port = port
        self.apk_dir = apk_dir
        self.snapshot_name = snapshot_name
        self.device_str = f"{self.ip}:{self.port}"

    def formatted_time(self):
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def adb_connect(self):
        # Bağlanmayı dene, zaten bağlıysa hata verir ama önemli değil
        subprocess.run(["adb", "connect", self.device_str], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def run_adb_shell(self, command):
        # Shell komutlarını subprocess ile çalıştır
        result = subprocess.run(
            ["adb", "-s", self.device_str, "shell"] + command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0:
            print(f"[!] Komut hatası: {' '.join(command)}\nHata: {result.stderr.strip()}")
            return ""
        return result.stdout.strip()

    def install_apk(self, apk_path):
        result = subprocess.run(
            ["adb", "-s", self.device_str, "install", "-r", apk_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            print(f"[!] APK yükleme başarısız: {apk_path}\nHata: {result.stderr.strip()}")
        else:
            print(f"[✓] APK yüklendi: {apk_path}\n{result.stdout.strip()}")

    def get_installed_packages(self):
        output = self.run_adb_shell(["pm", "list", "packages"])
        packages = [line.replace("package:", "") for line in output.splitlines()]
        return set(packages)

    def grant_all_permissions(self, package_name):
        output = self.run_adb_shell(["dumpsys", "package", package_name])
        for line in output.splitlines():
            if "permission:" in line and "granted=false" in line:
                perm = line.split()[-1]
                self.run_adb_shell(["pm", "grant", package_name, perm])

    def get_syscalls(self, package_name):
        output = self.run_adb_shell(["dumpsys", "package", package_name])
        # granted = [line.strip() for line in output.splitlines() if "granted=true" in line]
        # return granted
        return output

    def reset_snapshot(self):
        conn = libvirt.open("qemu:///system")
        dom = conn.lookupByName("android-x86-9.0")
        snapshot = dom.snapshotLookupByName(self.snapshot_name)
        dom.revertToSnapshot(snapshot)
        conn.close()

    def analyze_apks(self):
        apk_files = [f for f in os.listdir(self.apk_dir) if f.endswith(".apk")]

        for apk in apk_files:
            apk_path = os.path.join(self.apk_dir, apk)
            print(f"[+] Analyzing {apk}...")

            self.reset_snapshot()
            time.sleep(5)  # snapshot’tan dönmenin tamamlanmasını bekle

            print("Returned to snapshot state")
            self.adb_connect()
            print("Connected to the device")

            packages_before = self.get_installed_packages()

            self.install_apk(apk_path)

            packages_after = self.get_installed_packages()

            new_packages = packages_after - packages_before
            if not new_packages:
                print("[!] Yeni paket bulunamadı, analiz atlanıyor.")
                continue

            package_name = new_packages.pop()
            print(f"Paket adı: {package_name}")

            self.grant_all_permissions(package_name)

            sys_dump = self.get_syscalls(package_name)

            log_filename = f"logs/{self.formatted_time()}_{apk}.txt"
            os.makedirs("logs", exist_ok=True)
            with open(log_filename, "w") as log_file:
                log_file.write(f"APK: {apk}\n")
                log_file.write(f"Package: {package_name}\n")
                log_file.write(sys_dump)


                # log_file.write("Granted Permissions:\n")
                # log_file.writelines([perm + "\n" for perm in granted_perms])

            print(f"[✓] Finished {apk}, results saved to {log_filename}\n")


if __name__ == "__main__":
    analyzer = MalwareAnalyzer(
        ip="192.168.122.232",
        port=5555,
        apk_dir="../viruses",
        snapshot_name="safe_snapshot",
    )
    analyzer.analyze_apks()
