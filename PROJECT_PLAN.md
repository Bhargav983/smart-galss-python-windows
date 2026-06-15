# PROJECT_PLAN.md — HeyCyan Smart Glasses Windows Python MVP

## Project Summary

This project is a Windows Python MVP for HeyCyan smart glasses.

The MVP should allow a user to:

1. Scan for Bluetooth/BLE devices.
2. Select and connect to HeyCyan glasses.
3. Keep BLE connected.
4. Enable BLE notifications.
5. Read battery value.
6. Capture photo using BLE command.
7. Enable Wi-Fi transfer mode using BLE command.
8. Connect Windows PC to glasses Wi-Fi.
9. Check device IP reachability.
10. Check media service.
11. Fetch media config.
12. Fetch media list.
13. Show media count.
14. Show latest media.
15. Download latest photo.
16. Download all photos.

The first version should be terminal-based. GUI is not part of the initial MVP.

---

## Current Project Status

The current implementation already has a clean modular structure.

Existing/expected files:

```txt
heycyn_windows_mvp/
│
├── main.py
├── config.py
├── requirements.txt
│
├── services/
│   ├── __init__.py
│   ├── scanner.py
│   ├── connection.py
│   ├── battery.py
│   ├── diagnostics.py
│   ├── photo_capture.py
│   ├── transfer_mode.py
│   ├── wifi_service.py
│   ├── media_service.py
│   ├── download_service.py
│   └── heycyn_sdk.py
│
├── downloads/
│
└── logs/
```

The app is controlled through `main.py`.

The high-level wrapper is:

```txt
services/heycyn_sdk.py
```

Actual feature logic is split into separate service files.

---

## Important Finding

The package:

```txt
heycyan-glasses-sdk
```

installs successfully, but currently appears to install only metadata and no importable Python SDK module.

Observed command:

```powershell
pip show -f heycyan-glasses-sdk
```

Observed files:

```txt
heycyan_glasses_sdk-1.0.0.dist-info/INSTALLER
heycyan_glasses_sdk-1.0.0.dist-info/METADATA
heycyan_glasses_sdk-1.0.0.dist-info/RECORD
heycyan_glasses_sdk-1.0.0.dist-info/REQUESTED
heycyan_glasses_sdk-1.0.0.dist-info/WHEEL
heycyan_glasses_sdk-1.0.0.dist-info/top_level.txt
```

Therefore:

- Do not rely on `import heycyan_glasses_sdk`.
- Continue with wrapper service approach.
- Use `bleak`, which is installed as a dependency of `heycyan-glasses-sdk`.
- Keep all HeyCyan-specific BLE logic isolated so it can be replaced later if the actual SDK becomes available.

---

## Requirements File

Use this `requirements.txt`:

```txt
heycyan-glasses-sdk
requests
pillow
```

`heycyan-glasses-sdk` installs `bleak`.

If needed, explicitly add:

```txt
bleak
```

but avoid unnecessary dependency changes unless the environment fails.

---

## Configuration

`config.py` must contain:

```python
SCAN_TIMEOUT = 20

HEYCYAN_SERVICE_UUIDS = [
    "7905fff0-b5ce-4e99-a40f-4b1e122d00d0",
    "6e40fff0-b5a3-f393-e0a9-e50e24dcca9e",
]

BATTERY_LEVEL_UUID = "00002a19-0000-1000-8000-00805f9b34fb"

HEYCYAN_COMMAND_CHAR_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
HEYCYAN_NOTIFY_CHAR_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"

PHOTO_CAPTURE_COMMAND = bytes([0x01])
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

Important:

The following are placeholders until verified using real glasses:

```txt
HEYCYAN_COMMAND_CHAR_UUID
HEYCYAN_NOTIFY_CHAR_UUID
PHOTO_CAPTURE_COMMAND
TRANSFER_MODE_COMMAND
MEDIA_CONFIG_URL
MEDIA_LIST_URL
```

---

## Implementation Phases

## Phase 1 — Project Setup

Goal:

Prepare clean project structure.

Tasks:

- Verify Python version.
- Install requirements.
- Create folder structure.
- Create `downloads/`.
- Create `logs/`.
- Create empty `services/__init__.py`.

Commands:

```powershell
mkdir heycyn_windows_mvp
cd heycyn_windows_mvp
mkdir services downloads logs
New-Item main.py
New-Item config.py
New-Item requirements.txt
New-Item services\__init__.py
```

Acceptance:

```txt
python main.py starts without import errors
```

---

## Phase 2 — BLE Scan and Selection

Goal:

Scan nearby BLE devices and allow terminal selection.

Files:

```txt
services/scanner.py
services/heycyn_sdk.py
main.py
```

Tasks:

- Use scanner service to scan BLE devices.
- Print name, address, RSSI, service UUIDs.
- Mark HeyCyan UUID match as YES/NO.
- Allow user to select device number.
- Do not auto-connect to unknown devices.

Expected output:

```txt
Name
Address
RSSI
HeyCyan UUID Match
Service UUIDs
```

Acceptance:

```txt
User can scan BLE devices and select one from terminal
```

---

## Phase 3 — BLE Connection

Goal:

Connect to selected device and keep BLE client alive.

Files:

```txt
services/connection.py
services/heycyn_sdk.py
main.py
```

Tasks:

- Connect using selected BLE address.
- Store BLE client.
- Expose `is_ble_connected()`.
- Disconnect safely.
- Do not disconnect after each command.

Acceptance:

```txt
BLE Status shows CONNECTED after selecting valid device
```

---

## Phase 4 — Notifications

Goal:

Enable BLE notifications after connection.

Files:

```txt
services/connection.py
services/heycyn_sdk.py
main.py
config.py
```

Tasks:

- Add `enable_notifications()`.
- Start notify using `HEYCYAN_NOTIFY_CHAR_UUID`.
- Store last notification data.
- Print notification sender, raw bytes, hex.
- If UUID fails, print clear debugging instruction.

Acceptance:

```txt
Notifications enabled
OR failure clearly says to list BLE services/characteristics
```

Important:

If notification enable fails, run diagnostics and update:

```python
HEYCYAN_NOTIFY_CHAR_UUID
```

using a characteristic with `notify` or `indicate` property.

---

## Phase 5 — BLE Diagnostics

Goal:

List all BLE services and characteristics.

Files:

```txt
services/diagnostics.py
main.py
```

Tasks:

- Print service UUIDs.
- Print characteristic UUIDs.
- Print characteristic properties.
- Use output to identify command and notify UUIDs.

Acceptance:

```txt
User can see all BLE services and characteristics after connection
```

This phase is critical because real HeyCyan UUIDs must be confirmed from actual hardware.

---

## Phase 6 — Battery

Goal:

Read battery value.

Files:

```txt
services/battery.py
config.py
main.py
```

Tasks:

- Try standard BLE battery characteristic first:
  `00002a19-0000-1000-8000-00805f9b34fb`
- Print battery percentage.
- If it fails, guide user to diagnostics.

Acceptance:

```txt
Battery percentage is displayed
```

Fallback:

If standard battery UUID fails, identify battery command from HeyCyan notification/command protocol.

---

## Phase 7 — Photo Capture

Goal:

Capture photo through BLE command.

Files:

```txt
services/photo_capture.py
config.py
main.py
```

Tasks:

- Send `PHOTO_CAPTURE_COMMAND` to `HEYCYAN_COMMAND_CHAR_UUID`.
- Print command success/failure.
- Wait for notification response if available.
- Do not disconnect BLE.

Current placeholders:

```python
HEYCYAN_COMMAND_CHAR_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
PHOTO_CAPTURE_COMMAND = bytes([0x01])
```

Acceptance:

```txt
Photo capture command succeeds and glasses capture a photo
```

If it fails:

- Run diagnostics.
- Identify write/write-without-response characteristic.
- Update command characteristic UUID.
- Capture notification hex responses.

---

## Phase 8 — Transfer Mode

Goal:

Enable glasses Wi-Fi transfer mode through BLE command.

Files:

```txt
services/transfer_mode.py
config.py
main.py
```

Tasks:

- Send `TRANSFER_MODE_COMMAND` to `HEYCYAN_COMMAND_CHAR_UUID`.
- Keep BLE connected.
- Wait for readiness.
- Mark transfer mode enabled.
- User should then connect Windows to glasses Wi-Fi.

Current placeholders:

```python
TRANSFER_MODE_COMMAND = bytes([0x02])
```

Acceptance:

```txt
Glasses Wi-Fi hotspot becomes visible
```

If it fails:

- Confirm command characteristic UUID.
- Confirm actual transfer mode command bytes.
- Check notification response.

---

## Phase 9 — Wi-Fi

Goal:

Connect Windows to glasses Wi-Fi hotspot.

Files:

```txt
services/wifi_service.py
config.py
main.py
```

Tasks:

- Show available Wi-Fi networks.
- Show current Wi-Fi.
- Create Wi-Fi profile using XML.
- Connect using `netsh`.
- Check connected SSID.
- Ping glasses IP.

Known details:

```txt
SSID: V03._4AB30976982A
Password: 123456789
Device IP: 192.168.31.2
Gateway: 192.168.31.1
```

Commands used:

```powershell
netsh wlan show networks
netsh wlan show interfaces
netsh wlan add profile filename="heycyn_wifi_profile.xml"
netsh wlan connect name="V03._4AB30976982A" ssid="V03._4AB30976982A"
ping 192.168.31.2 -n 2
```

Acceptance:

```txt
Windows connects to glasses Wi-Fi
192.168.31.2 is reachable
```

Note:

PowerShell may need Administrator mode.

---

## Phase 10 — Media Service

Goal:

Check media HTTP service and fetch media list.

Files:

```txt
services/media_service.py
config.py
main.py
```

Tasks:

- Check base URL.
- Fetch config URL.
- Fetch media list URL.
- Print status code and response preview.
- Parse JSON response if possible.
- Show media count.
- Show latest media.

Current temporary URLs:

```python
MEDIA_BASE_URL = "http://192.168.31.2"
MEDIA_CONFIG_URL = "http://192.168.31.2/config"
MEDIA_LIST_URL = "http://192.168.31.2/list"
```

Acceptance:

```txt
Media list is loaded
Media count is displayed
Latest media is printed
```

If endpoints fail:

- Print status code and preview.
- Try common media paths only after user confirms.
- Do not hide errors.

---

## Phase 11 — Downloads

Goal:

Download latest and all photos.

Files:

```txt
services/download_service.py
services/media_service.py
main.py
```

Tasks:

- Convert media item to download URL.
- Download file with streaming.
- Show progress.
- Save to `downloads/`.
- Support latest and all downloads.

Acceptance:

```txt
Latest photo downloads successfully
All photos download successfully
Files are saved in downloads/
```

---

## Phase 12 — Logging Improvement

Goal:

Save logs to file after terminal MVP works.

Files:

```txt
logs/app.log
utils/logger.py optional
```

Tasks:

- Add Python logging.
- Keep terminal print.
- Save logs to file.

Acceptance:

```txt
logs/app.log contains scan/connect/battery/photo/transfer/wifi/media/download events
```

Do not do this before core BLE and Wi-Fi are confirmed.

---

## Phase 13 — Optional GUI

Goal:

Add GUI only after terminal MVP works.

Recommended options:

```txt
Tkinter for simple native UI
PyQt only if richer UI is needed
```

Do not start GUI until:

```txt
BLE connection works
Battery works
Photo capture works
Transfer mode works
Wi-Fi works
Media list works
Download works
```

---

## Terminal Menu

Use this menu:

```txt
BLE / Diagnostics
1.  Scan and connect Bluetooth device
2.  Enable BLE notifications
3.  Get battery value
4.  List BLE services/characteristics
5.  Capture photo
6.  Enable transfer mode

Wi-Fi / Gallery
7.  Show available Wi-Fi networks
8.  Show current Wi-Fi
9.  Connect to glasses Wi-Fi
10. Check device reachable
11. Check media service
12. Fetch media config
13. Fetch media list
14. Show media count
15. Show latest media
16. Download latest photo
17. Download all photos

App
18. Disconnect BLE
19. Exit
```

Recommended real-hardware test order:

```txt
1. Scan and connect Bluetooth device
4. List BLE services/characteristics
2. Enable BLE notifications
3. Get battery value
5. Capture photo
6. Enable transfer mode
7. Show available Wi-Fi networks
9. Connect to glasses Wi-Fi
10. Check device reachable
11. Check media service
12. Fetch media config
13. Fetch media list
14. Show media count
15. Show latest media
16. Download latest photo
17. Download all photos
18. Disconnect BLE
```

---

## Debugging Checklist

When glasses are available, collect these outputs:

### 1. Scan Output

Need:

```txt
Device name
Address
RSSI
Service UUIDs
HeyCyan UUID Match YES/NO
```

### 2. Services Output

Need all:

```txt
Service UUID
Characteristic UUID
Characteristic Properties
```

Look for:

```txt
notify
indicate
write
write-without-response
read
```

### 3. Notification Output

Need:

```txt
Raw bytes
Hex
Sender characteristic
```

### 4. Battery Output

Need:

```txt
Battery percentage
or exact error
```

### 5. Photo Output

Need:

```txt
Command sent
Notification received
or exact error
```

### 6. Transfer Mode Output

Need:

```txt
Command sent
Wi-Fi SSID appears or not
Notification received
or exact error
```

### 7. Media Output

Need:

```txt
Base URL status
Config URL status
List URL status
Response preview
```

---

## Known Risks

### Risk 1 — PyPI SDK has no importable code

Mitigation:

Use wrapper approach with `bleak`.

### Risk 2 — HeyCyan command bytes are unknown

Mitigation:

Use diagnostics and notifications to map command characteristic and response.

### Risk 3 — Battery may not use standard BLE battery UUID

Mitigation:

Use HeyCyan command/notification flow if standard battery fails.

### Risk 4 — Windows Wi-Fi connection may need admin rights

Mitigation:

Run PowerShell as Administrator.

### Risk 5 — Media URLs may be different

Mitigation:

Print response previews and update config paths based on actual device responses.

---

## Definition of Done

The MVP is complete only when:

```txt
App launches without import errors
Menu is readable
BLE scan works
Correct glasses can be selected
BLE connection works
BLE remains connected
Notifications are enabled or correct notify UUID is identified
Battery value is shown
Photo capture works
Transfer mode works
Glasses Wi-Fi appears
Windows connects to glasses Wi-Fi
Device IP is reachable
Media service is reachable
Media list loads
Media count displays
Latest media displays
Latest photo downloads
Download all works
All failures give clear next steps
Code remains modular
```

---

## Codex Instructions

When modifying this project:

1. Do not convert it to React Native or Android.
2. Do not add GUI unless requested.
3. Do not merge all services into one file.
4. Do not remove diagnostics.
5. Do not remove terminal menu.
6. Do not break existing imports.
7. Do not assume `heycyan_glasses_sdk` import works.
8. Keep HeyCyan-specific commands centralized in `config.py`.
9. Keep BLE connected during gallery/Wi-Fi flow.
10. Enable notifications after BLE connection.
11. Every new feature must be testable from `main.py`.
12. Every hardware failure must show clear next action.
