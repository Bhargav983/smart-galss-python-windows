import subprocess
import time
from config import GLASSES_WIFI_SSID, GLASSES_WIFI_PASSWORD, GLASSES_DEVICE_IP


class HeyCyanWifiService:
    def __init__(self):
        self.connected = False

    def run_command(self, command):
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                shell=True
            )

            return result.stdout, result.stderr

        except Exception as e:
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
            print("Connected to glasses Wi-Fi.")
            return True

        self.connected = False
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
            print("Device is reachable.")
            return True

        print("Device is not reachable.")
        return False