# HeyCyan Windows MVP - Auto Flow Project Plan

## Purpose

This project is a Windows Python MVP for connecting to HeyCyan smart glasses, capturing a photo, switching to the glasses Wi-Fi media mode, and downloading the latest photo with minimal user input.

The new direction is:

1. User chooses one main action.
2. App finds the expected HeyCyan glasses automatically.
3. App connects over BLE.
4. App runs the remaining BLE, Wi-Fi, media, and download steps automatically.
5. Any failure is printed clearly and appended to `logs/app.log`.
6. BLE is disconnected safely before exit.

The app remains terminal based for now. GUI is not part of this phase.

## Expected Glasses

The current target glasses are:

```txt
Name: V03._982A
Address: 4A:B3:09:76:98:2A
Wi-Fi SSID: V03._4AB30976982A
Wi-Fi password: 123456789
Device IP: 192.168.31.2
```

If these values change, update `config.py`.

## Current User Menu

The old long menu has been replaced with a simple 3-choice menu:

```txt
Choose
1. Auto connect, capture, and download latest photo
2. BLE diagnostics
3. Exit
```

All Wi-Fi, gallery, media count, latest media, and download actions happen inside option `1`.

## Main Auto Flow

When the user selects option `1`, the app should run this sequence:

1. Scan for BLE devices.
2. Look for the expected HeyCyan glasses by known name, address, prefix, or HeyCyan match.
3. If not found, wait and scan again.
4. Select the expected glasses automatically.
5. Connect BLE with retries.
6. Enable BLE notifications.
7. Read battery value.
8. Capture photo.
9. Enable transfer mode.
10. Show available Wi-Fi networks.
11. Connect Windows to the glasses Wi-Fi.
12. Check whether the glasses IP is reachable.
13. Check media service.
14. Fetch media config.
15. Fetch media list.
16. Show media count.
17. Show latest media.
18. Download latest photo to `downloads/`.
19. Keep errors visible in terminal and append them to `logs/app.log`.

Small delays should remain between hardware steps because BLE, transfer mode, Wi-Fi, and media service startup can take time.

## Diagnostics Flow

Option `2` is kept for debugging BLE UUID problems.

It should list BLE services and characteristics after BLE is connected.

Use this when:

- Notifications fail.
- Battery read fails.
- Photo capture command fails.
- Transfer mode command fails.
- Command or notify UUIDs need confirmation.

Diagnostics must not be removed, because the HeyCyan BLE command and notification details may still need real-hardware confirmation.

## Exit Behavior

Option `3` exits the app.

Before exit:

- Disable notifications if enabled.
- Disconnect BLE.
- Clear BLE client state.
- Log disconnect status.

The app should also disconnect BLE on `Ctrl+C` or unexpected menu-loop exit.

## Logging Requirements

All important events should be appended to:

```txt
logs/app.log
```

Log these events:

- App start.
- Scan attempts.
- Expected glasses found or not found.
- BLE connection attempts.
- Notification enable status.
- Battery result or error.
- Photo capture result or error.
- Transfer mode result or error.
- Wi-Fi connect result or error.
- Device reachability result.
- Media service/config/list result or error.
- Media count.
- Latest media item.
- Download result or error.
- BLE disconnect.
- Unexpected exceptions.

The terminal should still print clear user-facing messages.

## Important Implementation Rules

Keep the current modular layout:

```txt
main.py
config.py
services/scanner.py
services/connection.py
services/battery.py
services/diagnostics.py
services/photo_capture.py
services/transfer_mode.py
services/wifi_service.py
services/media_service.py
services/download_service.py
services/heycyn_sdk.py
utils/logger.py
downloads/
logs/
```

Do not merge all logic into `main.py`.

`main.py` should coordinate the flow only. Feature logic should stay in service files.

## Configuration

`config.py` should hold all hardware-specific values:

```python
SCAN_TIMEOUT = 10

AUTO_CONNECT_NAME_PREFIX = "V03._"
KNOWN_GLASSES_NAME_PREFIX = "V03._"
KNOWN_GLASSES_NAME = "V03._982A"
KNOWN_GLASSES_ADDRESS = "4A:B3:09:76:98:2A"
AUTO_SELECT_KNOWN_GLASSES = True

BATTERY_LEVEL_UUID = "00002a19-0000-1000-8000-00805f9b34fb"

HEYCYAN_COMMAND_CHAR_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
HEYCYAN_NOTIFY_CHAR_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"

PHOTO_CAPTURE_COMMAND = bytes([0x02, 0x01, 0x01])
TRANSFER_MODE_COMMAND = bytes([0x02])

GLASSES_WIFI_SSID = "V03._4AB30976982A"
GLASSES_WIFI_PASSWORD = "123456789"
GLASSES_DEVICE_IP = "192.168.31.2"
GLASSES_GATEWAY = "192.168.31.1"

MEDIA_BASE_URL = "http://192.168.31.2"
MEDIA_CONFIG_URL = "http://192.168.31.2/config"
MEDIA_LIST_URL = "http://192.168.31.2/list"

DOWNLOAD_FOLDER = "downloads"
```

The command UUIDs, notify UUID, command bytes, and media URLs are still hardware-verification points.

## Known Risks

### HeyCyan PyPI SDK

The `heycyan-glasses-sdk` package may install metadata without a usable importable Python module. Keep using the local wrapper approach with `bleak`.

### BLE UUIDs May Be Different

If notifications, photo capture, or transfer mode fail, run option `2` and update `config.py` with real characteristic UUIDs.

### Battery May Not Use Standard BLE Battery UUID

The first implementation reads the standard BLE battery characteristic. If the glasses do not expose it, battery must be mapped through the HeyCyan command/notification protocol.

### Windows Wi-Fi May Need Admin

Wi-Fi profile creation and connection use `netsh`. Some Windows systems may require running the terminal as Administrator.

### Media URLs May Be Different

The current media endpoints are temporary. If `/config` or `/list` fail, use response previews and network inspection to identify the correct paths.

## Acceptance Criteria

The auto-flow MVP is successful when:

```txt
App starts without import errors
Menu shows only 3 choices
Option 1 scans until expected glasses are found
Expected glasses are selected automatically
BLE connects successfully
Notifications are enabled or failure is logged clearly
Battery result is shown or failure is logged clearly
Photo capture command is sent
Transfer mode command is sent
Windows connects to glasses Wi-Fi
Device IP reachability is checked
Media service is checked
Media config/list are fetched
Media count is shown
Latest media is shown
Latest photo downloads to downloads/
Errors are appended to logs/app.log
Option 2 can still list BLE services
Option 3 disconnects BLE before exit
Ctrl+C disconnects BLE before exit
```

## Next Work

1. Test option `1` with real glasses nearby.
2. If a BLE step fails, run option `2` after connection and capture the service/characteristic output.
3. Update command and notify UUIDs in `config.py`.
4. Confirm real photo capture command bytes.
5. Confirm real transfer mode command bytes.
6. Confirm media service endpoints after Wi-Fi connects.
7. Add a result summary at the end of option `1` showing success/failure for each step.
