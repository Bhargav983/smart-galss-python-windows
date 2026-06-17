# BLE scan timeout
SCAN_TIMEOUT = 10

# Auto-connect settings
AUTO_CONNECT_NAME_PREFIX = "V03._"
KNOWN_GLASSES_NAME_PREFIX = "V03._"
KNOWN_GLASSES_NAME = "V03._982A"
KNOWN_GLASSES_ADDRESS = "4A:B3:09:76:98:2A"
AUTO_SELECT_KNOWN_GLASSES = True

# HeyCyan BLE Service UUIDs
HEYCYAN_SERVICE_UUIDS = [
    "7905fff0-b5ce-4e99-a40f-4b1e122d00d0",
    "6e40fff0-b5a3-f393-e0a9-e50e24dcca9e",
]

# # Standard BLE battery level characteristic
# BATTERY_LEVEL_UUID = "00002a19-0000-1000-8000-00805f9b34fb"

# # HeyCyan command/notify placeholders
# HEYCYAN_COMMAND_CHAR_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
# HEYCYAN_NOTIFY_CHAR_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"

HEYCYAN_COMMAND_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
HEYCYAN_NOTIFY_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
HEYCYAN_NOTIFY_CHAR_UUIDS = [
    "6e400003-b5a3-f393-e0a9-e50e24dcca9e",
    "0000ae02-0000-1000-8000-00805f9b34fb",
    "0000ae04-0000-1000-8000-00805f9b34fb",
    "0000ae05-0000-1000-8000-00805f9b34fb",
    "00004a02-0000-1000-8000-00805f9b34fb",
    "0000ae3c-0000-1000-8000-00805f9b34fb",
    "de5bf729-d711-4e47-af26-65e3012a5dc7",
    "0000fee3-0000-1000-8000-00805f9b34fb",
]

# Standard battery UUID is not available in diagnostics.
# Keep this for now, but battery may still fail.
BATTERY_LEVEL_UUID = "00002a19-0000-1000-8000-00805f9b34fb"
# Temporary command bytes
# PHOTO_CAPTURE_COMMAND = bytes([0x01])
PHOTO_CAPTURE_COMMAND = bytes([0x02, 0x01, 0x01])
PHOTO_CAPTURE_COMMANDS = [
    bytes([0x02, 0x01, 0x01]),
    bytes([0x02, 0x01]),
    bytes([0x01]),
    bytes([0x02]),
    bytes([0x03]),
    bytes([0x01, 0x01]),
    bytes([0x02, 0x02]),
    bytes([0x03, 0x01]),
    bytes([0x04]),
    bytes([0x05]),
]

BLE_COMMAND_NOTIFY_PAIRS = [
    {
        "name": "Nordic UART",
        "command_uuid": "6e400002-b5a3-f393-e0a9-e50e24dcca9e",
        "notify_uuid": "6e400003-b5a3-f393-e0a9-e50e24dcca9e",
    },
    {
        "name": "AE01 / AE02",
        "command_uuid": "0000ae01-0000-1000-8000-00805f9b34fb",
        "notify_uuid": "0000ae02-0000-1000-8000-00805f9b34fb",
    },
    {
        "name": "AE03 / AE04",
        "command_uuid": "0000ae03-0000-1000-8000-00805f9b34fb",
        "notify_uuid": "0000ae04-0000-1000-8000-00805f9b34fb",
    },
    {
        "name": "AE3B / AE3C",
        "command_uuid": "0000ae3b-0000-1000-8000-00805f9b34fb",
        "notify_uuid": "0000ae3c-0000-1000-8000-00805f9b34fb",
    },
    {
        "name": "DE5B",
        "command_uuid": "de5bf72a-d711-4e47-af26-65e3012a5dc7",
        "notify_uuid": "de5bf729-d711-4e47-af26-65e3012a5dc7",
    },
]
TRANSFER_MODE_COMMAND = bytes([0x02])

# Glasses Wi-Fi details
GLASSES_WIFI_SSID = "V03._4AB30976982A"
GLASSES_WIFI_PASSWORD = "123456789"
GLASSES_DEVICE_IP = "192.168.31.2"
GLASSES_GATEWAY = "192.168.31.1"

# Media URLs
MEDIA_BASE_URL = "http://192.168.31.2"
MEDIA_CONFIG_URL = "http://192.168.31.2/config"
MEDIA_LIST_URL = "http://192.168.31.2/list"

# Local download folder
DOWNLOAD_FOLDER = "downloads"
