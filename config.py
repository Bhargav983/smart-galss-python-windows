# ==============================
# HeyCyan Windows MVP Config
# ==============================

# BLE scan timeout
SCAN_TIMEOUT = 20
HEYCYAN_NOTIFY_CHAR_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"
# HeyCyan BLE Service UUIDs
HEYCYAN_SERVICE_UUIDS = [
    "7905fff0-b5ce-4e99-a40f-4b1e122d00d0",
    "6e40fff0-b5a3-f393-e0a9-e50e24dcca9e",
]

# Standard BLE battery level characteristic
BATTERY_LEVEL_UUID = "00002a19-0000-1000-8000-00805f9b34fb"

# HeyCyan command characteristic placeholders
# We will confirm these after listing BLE services/characteristics from the glasses
HEYCYAN_COMMAND_CHAR_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
HEYCYAN_NOTIFY_CHAR_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"

# Temporary command bytes
# These may need to be replaced after testing with actual HeyCyan command values
PHOTO_CAPTURE_COMMAND = bytes([0x01])
TRANSFER_MODE_COMMAND = bytes([0x02])

# Glasses Wi-Fi details
GLASSES_WIFI_SSID = "V03._4AB30976982A"
GLASSES_WIFI_PASSWORD = "123456789"
GLASSES_DEVICE_IP = "192.168.31.2"
GLASSES_GATEWAY = "192.168.31.1"

# Media URLs
# These may need adjustment after checking the glasses media server
MEDIA_BASE_URL = "http://192.168.31.2"
MEDIA_CONFIG_URL = "http://192.168.31.2/config"
MEDIA_LIST_URL = "http://192.168.31.2/list"

# Local download folder
DOWNLOAD_FOLDER = "downloads"