from services.scanner import HeyCyanScanner
from services.connection import HeyCyanConnection
from services.battery import HeyCyanBattery
from services.diagnostics import HeyCyanDiagnostics
from services.photo_capture import HeyCyanPhotoCapture
from services.transfer_mode import HeyCyanTransferMode
from services.wifi_service import HeyCyanWifiService
from services.media_service import HeyCyanMediaService
from services.download_service import HeyCyanDownloadService


class HeyCyanWindowsSDK:
    """
    Main SDK wrapper for the Windows MVP.

    This file only combines all service modules.
    Actual feature logic is kept separately in:
    scanner.py
    connection.py
    battery.py
    diagnostics.py
    photo_capture.py
    transfer_mode.py
    wifi_service.py
    media_service.py
    download_service.py
    """

    def __init__(self):
        # BLE core services
        self.scanner = HeyCyanScanner()
        self.connection = HeyCyanConnection()
        self.battery = HeyCyanBattery(self.connection)
        self.diagnostics = HeyCyanDiagnostics(self.connection)

        # BLE command services
        self.photo_capture = HeyCyanPhotoCapture(self.connection)
        self.transfer_mode = HeyCyanTransferMode(self.connection)

        # Wi-Fi / media services
        self.wifi = HeyCyanWifiService()
        self.media = HeyCyanMediaService()
        self.download = HeyCyanDownloadService()

    # -----------------------------
    # BLE scan / connection
    # -----------------------------

    async def scan_glasses(self, timeout=20):
        return await self.scanner.scan_glasses(timeout=timeout)

    def print_devices(self, devices):
        self.scanner.print_devices(devices)

    def select_device_from_terminal(self, devices):
        return self.scanner.select_device_from_terminal(devices)

    async def connect_selected_device(self, selected_device):
        return await self.connection.connect(selected_device)

    async def disconnect(self):
        return await self.connection.disconnect()

    def is_ble_connected(self):
        return self.connection.is_ble_connected()

    # -----------------------------
    # BLE notifications
    # -----------------------------

    async def enable_notifications(self):
        return await self.connection.enable_notifications()

    async def disable_notifications(self):
        return await self.connection.disable_notifications()

    def get_last_notification_data(self):
        return self.connection.get_last_notification_data()

    # -----------------------------
    # BLE diagnostics
    # -----------------------------

    async def list_services(self):
        return await self.diagnostics.list_services()

    # -----------------------------
    # Battery
    # -----------------------------

    async def get_battery(self):
        return await self.battery.get_battery()

    # -----------------------------
    # Photo capture
    # -----------------------------

    async def capture_photo(self):
        return await self.photo_capture.capture_photo()

    # -----------------------------
    # Transfer mode
    # -----------------------------

    async def enable_transfer_mode(self):
        return await self.transfer_mode.enable_transfer_mode()

    def is_transfer_mode_enabled(self):
        return self.transfer_mode.is_transfer_mode_enabled()

    # -----------------------------
    # Wi-Fi
    # -----------------------------

    def show_wifi_networks(self):
        return self.wifi.show_available_networks()

    def show_current_wifi(self):
        return self.wifi.show_current_wifi()

    def connect_wifi(self):
        return self.wifi.connect_to_glasses_wifi()

    def check_device_reachable(self):
        return self.wifi.check_device_reachable()

    # -----------------------------
    # Media
    # -----------------------------

    def check_media_service(self):
        return self.media.check_media_service()

    def fetch_media_config(self):
        return self.media.fetch_media_config()

    def fetch_media_list(self):
        return self.media.fetch_media_list()

    def get_media_count(self):
        return self.media.get_media_count()

    def get_latest_media(self):
        return self.media.get_latest_media()

    # -----------------------------
    # Downloads
    # -----------------------------

    def download_latest(self):
        return self.download.download_latest(self.media)

    def download_all(self):
        return self.download.download_all(self.media)