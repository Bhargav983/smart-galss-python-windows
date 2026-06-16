import subprocess
import time
import ctypes
from config import GLASSES_WIFI_SSID, GLASSES_WIFI_PASSWORD, GLASSES_DEVICE_IP
from utils.logger import logger


class HeyCyanWifiService:
    def __init__(self):
        self.connected = False

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def run_command(self, command):
        try:
            logger.info(f"Executing Wi-Fi command: {command}")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=True
            )

            if result.stderr:
                logger.error(f"Command error: {result.stderr}")

            return result.stdout, result.stderr

        except Exception as e:
            logger.error(f"Execution error: {e}")
            return "", str(e)

    def show_available_networks(self):
        print("\nScanning available Wi-Fi networks...")

        stdout, stderr = self.run_command("netsh wlan show networks")

        if stderr:
            print("Wi-Fi scan error:", stderr)

        print(stdout)
        return stdout

    def show_current_wifi(self):
        print("\nChecking current Wi-Fi connection...")

        stdout, stderr = self.run_command("netsh wlan show interfaces")

        if stderr:
            print("Wi-Fi status error:", stderr)

        print(stdout)
        return stdout

    def create_wifi_profile(self, ssid=GLASSES_WIFI_SSID, password=GLASSES_WIFI_PASSWORD):
        if not self.is_admin():
            print("\nWARNING: Not running as Administrator. Wi-Fi profile creation might fail.")
            logger.warning("Attempting Wi-Fi profile creation without Admin privileges.")

        print(f"\nCreating Wi-Fi profile for SSID: {ssid}")

        profile_xml = f"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>
"""

        profile_path = "heycyn_wifi_profile.xml"

        with open(profile_path, "w", encoding="utf-8") as file:
            file.write(profile_xml)

        command = f'netsh wlan add profile filename="{profile_path}"'
        stdout, stderr = self.run_command(command)

        print(stdout)

        if stderr:
            print("Profile creation error:", stderr)

        return True

    def connect_to_glasses_wifi(self, ssid=GLASSES_WIFI_SSID, password=GLASSES_WIFI_PASSWORD):
        print(f"\nConnecting to glasses Wi-Fi: {ssid}")

        self.create_wifi_profile(ssid, password)

        command = f'netsh wlan connect name="{ssid}" ssid="{ssid}"'
        stdout, stderr = self.run_command(command)

        print(stdout)

        if stderr:
            print("Wi-Fi connect error:", stderr)

        print("Waiting for Wi-Fi connection...")
        time.sleep(8)

        if self.is_connected_to_ssid(ssid):
            self.connected = True
            logger.info(f"Successfully connected to Wi-Fi: {ssid}")
            print("Connected to glasses Wi-Fi.")
            return True

        self.connected = False
        logger.error(f"Failed to connect to Wi-Fi: {ssid}")
        print("Could not confirm glasses Wi-Fi connection.")
        return False

    def is_connected_to_ssid(self, ssid=GLASSES_WIFI_SSID):
        stdout = self.show_current_wifi()

        if ssid.lower() in stdout.lower():
            return True

        return False

    def check_device_reachable(self, ip=GLASSES_DEVICE_IP):
        print(f"\nChecking device reachable: {ip}")

        command = f"ping {ip} -n 2"
        stdout, stderr = self.run_command(command)

        print(stdout)

        if "TTL=" in stdout.upper():
            logger.info(f"Device {ip} is reachable via ping.")
            print("Device is reachable.")
            return True

        logger.warning(f"Device {ip} is not reachable via ping.")
        print("Device is not reachable.")
        return False
