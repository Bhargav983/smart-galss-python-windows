# SKILLS.md — HeyCyan Smart Glasses Windows Python MVP

## Project Role

You are working as a senior Python Windows desktop/BLE engineer helping build an MVP for HeyCyan smart glasses.

The project is a Windows Python application that must connect to HeyCyan smart glasses using Bluetooth/BLE, read battery value, capture photo through BLE command, enable Wi-Fi transfer mode through BLE command, connect Windows to the glasses Wi-Fi hotspot, fetch media list, and download photos to the local machine.

The implementation must stay simple, practical, and testable from the terminal first. Do not over-engineer UI at this stage.

---

## Core Goal

Build a working MVP for Windows using Python.

Required MVP features:

1. Scan Bluetooth/BLE devices.
2. Select the HeyCyan glasses from terminal.
3. Connect to glasses via BLE.
4. Keep BLE connected throughout the flow.
5. Enable BLE notifications after connection.
6. Read battery value.
7. Capture photo using BLE command.
8. Enable Wi-Fi transfer mode using BLE command.
9. Connect Windows to glasses Wi-Fi.
10. Check if device IP is reachable.
11. Check media service availability.
12. Fetch media config.
13. Fetch media list.
14. Show media count.
15. Show latest media.
16. Download latest photo.
17. Download all photos.

---

## Important HeyCyan SDK Context

The PyPI package installed is:

```txt
heycyan-glasses-sdk
```

However, in the current environment it installed only package metadata and no importable Python module.

Therefore, the implementation should use:

```txt
heycyan-glasses-sdk dependency chain
bleak for BLE operations
requests for media/download operations
Windows netsh for Wi-Fi operations
```

Keep all HeyCyan-specific logic inside service wrapper files so that if a real Python SDK module becomes available later, it can be swapped in without changing the main app flow.

Do not claim that `import heycyan_glasses_sdk` works unless verified.

---

## Technical Stack

Use:

```txt
Python 3.10+
bleak
requests
pillow
Windows PowerShell / netsh
Terminal-based MVP
```

Avoid for MVP:

```txt
React Native
Android
Expo
PyQt
Tkinter
Large GUI frameworks
Async background service complexity
Database
Cloud sync
```

PyQt/Tkinter can be added only after terminal MVP confirms BLE, battery, photo capture, transfer mode, Wi-Fi, media list, and downloads.

---

## Folder Structure

Maintain this structure:

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

Do not put all logic into one large file. Keep each feature in its own service file.

---

## File Responsibilities

### `main.py`

Responsibilities:

- Show terminal menu.
- Call SDK wrapper methods.
- Keep flow simple and readable.
- Do not contain BLE command logic.
- Do not contain Wi-Fi profile XML logic.
- Do not contain download logic.

### `config.py`

Responsibilities:

- Store UUIDs.
- Store Wi-Fi details.
- Store media URLs.
- Store placeholder command bytes.
- Store local download folder.

### `services/scanner.py`

Responsibilities:

- Scan BLE devices.
- Show device name, address, RSSI, service UUIDs.
- Identify possible HeyCyan match using known HeyCyan service UUIDs.
- Allow terminal selection.

### `services/connection.py`

Responsibilities:

- Connect to selected BLE device.
- Keep BLE client reference.
- Enable notifications after connection.
- Store last notification data.
- Disconnect safely.
- Expose `is_ble_connected()`.

### `services/battery.py`

Responsibilities:

- Read battery value.
- First try standard BLE battery characteristic.
- If battery read fails, guide user to list services.

### `services/diagnostics.py`

Responsibilities:

- List BLE services and characteristics.
- Print characteristic UUIDs and properties.
- This is critical to identify actual command/notify UUIDs.

### `services/photo_capture.py`

Responsibilities:

- Send photo capture BLE command.
- Use command characteristic from config.
- Use command bytes from config.
- Handle failures clearly.

### `services/transfer_mode.py`

Responsibilities:

- Send BLE command to enable Wi-Fi/media transfer mode.
- Keep BLE connected.
- Mark transfer mode enabled only after command success or expected wait.
- Do not disconnect BLE.

### `services/wifi_service.py`

Responsibilities:

- Show available Wi-Fi networks.
- Show current Wi-Fi.
- Create Windows Wi-Fi profile using `netsh`.
- Connect to glasses Wi-Fi.
- Ping/check device IP reachability.

### `services/media_service.py`

Responsibilities:

- Check HTTP media service.
- Fetch media config.
- Fetch media list.
- Parse JSON media list where possible.
- Show media count.
- Show latest media.
- Convert media item into download URL.

### `services/download_service.py`

Responsibilities:

- Download latest file.
- Download all files.
- Show download started/progress/completed/failed.
- Save files into `downloads/`.

### `services/heycyn_sdk.py`

Responsibilities:

- Act as high-level SDK wrapper.
- Combine all service modules.
- Expose clean methods for `main.py`.
- Do not contain detailed implementation logic.

---

## Required BLE Behavior

BLE must remain connected during:

```txt
Battery read
Photo capture
Transfer mode enable
Wi-Fi connection
Media download
```

Do not disconnect BLE automatically when switching to Wi-Fi/media actions.

Enable notifications immediately after successful BLE connection.

If notification enable fails, the app should not crash. It should show a clear message and instruct the user to run:

```txt
List BLE services/characteristics
```

Then identify a characteristic with:

```txt
notify
indicate
```

and update `HEYCYAN_NOTIFY_CHAR_UUID`.

---

## Current Known UUIDs / Placeholders

Use these in `config.py` initially:

```python
HEYCYAN_SERVICE_UUIDS = [
    "7905fff0-b5ce-4e99-a40f-4b1e122d00d0",
    "6e40fff0-b5a3-f393-e0a9-e50e24dcca9e",
]

BATTERY_LEVEL_UUID = "00002a19-0000-1000-8000-00805f9b34fb"

HEYCYAN_COMMAND_CHAR_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
HEYCYAN_NOTIFY_CHAR_UUID = "0000fff2-0000-1000-8000-00805f9b34fb"

PHOTO_CAPTURE_COMMAND = bytes([0x01])
TRANSFER_MODE_COMMAND = bytes([0x02])
```

Important:

The command characteristic, notify characteristic, photo capture command bytes, and transfer mode command bytes are placeholders until verified using real glasses service listing and notifications.

Do not treat placeholders as final production values.

---

## Wi-Fi Details

Use these known values:

```python
GLASSES_WIFI_SSID = "V03._4AB30976982A"
GLASSES_WIFI_PASSWORD = "123456789"
GLASSES_DEVICE_IP = "192.168.31.2"
GLASSES_GATEWAY = "192.168.31.1"
```

For Windows Wi-Fi:

- Use `netsh wlan show networks`.
- Use `netsh wlan show interfaces`.
- Use `netsh wlan add profile`.
- Use `netsh wlan connect`.

PowerShell may need to be run as Administrator for Wi-Fi profile creation/connection.

---

## Media Service Assumptions

Initial media URLs:

```python
MEDIA_BASE_URL = "http://192.168.31.2"
MEDIA_CONFIG_URL = "http://192.168.31.2/config"
MEDIA_LIST_URL = "http://192.168.31.2/list"
```

These are temporary and must be verified after transfer mode and Wi-Fi are working.

The app should print response status and preview of response text for debugging.

Do not silently fail when endpoints are wrong.

---

## Logging Requirements

For terminal MVP, print useful logs clearly.

Must show logs for:

```txt
App started
BLE scan started
BLE device found
BLE device selected
BLE connection started
BLE connected
BLE notification enable started
BLE notification enabled
BLE notification received
Battery request started
Battery value received
Photo capture command sent
Transfer mode command sent
Wi-Fi scan started
Wi-Fi profile created
Wi-Fi connection started
Wi-Fi connected
Device reachable check started
Media service check started
Media config fetch started
Media list fetch started
Media count loaded
Download started
Download progress
Download completed
Download failed
BLE disconnected
```

Later, logs can be written to `logs/app.log`, but terminal print is enough for the first MVP.

---

## Error Handling Rules

Never crash the app for expected hardware or network failures.

Handle:

```txt
No BLE devices found
Wrong BLE device selected
BLE connection failed
Notification UUID wrong
Battery characteristic not found
Command characteristic not found
Photo command failed
Transfer mode command failed
Wi-Fi profile creation failed
Wi-Fi connection failed
Device IP unreachable
Media service unreachable
Media list endpoint wrong
Download URL missing
Download failed
```

Every failure should tell the next debugging action.

Example:

```txt
Battery read failed.
Next step: choose option 4 and list BLE services/characteristics.
```

---

## Terminal Menu Requirements

Keep menu grouped:

```txt
BLE / Diagnostics
1. Scan and connect Bluetooth device
2. Enable BLE notifications
3. Get battery value
4. List BLE services/characteristics
5. Capture photo
6. Enable transfer mode

Wi-Fi / Gallery
7. Show available Wi-Fi networks
8. Show current Wi-Fi
9. Connect to glasses Wi-Fi
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

Recommended testing flow:

```txt
1 → 4 → 2 → 3 → 5 → 6 → 7 → 9 → 10 → 11 → 13 → 14 → 16
```

---

## Code Quality Guidelines

Follow these rules:

- Keep functions small.
- Keep modules focused.
- Avoid duplicate BLE connection state.
- Do not hardcode UUIDs inside service files; use `config.py`.
- Do not import service internals into `main.py`; use `HeyCyanWindowsSDK`.
- Print clear user-facing messages.
- Add comments only where they explain hardware-specific assumptions.
- Do not add GUI until terminal flow works.
- Do not remove diagnostics because it is essential for mapping real UUIDs.
- Make every action manually testable from the menu.

---

## Development Priority

Priority order:

1. Stable scanning.
2. Stable device selection.
3. Stable BLE connection.
4. Service/characteristic listing.
5. Notification enable.
6. Battery read.
7. Photo capture command.
8. Transfer mode command.
9. Wi-Fi connect.
10. Device reachability.
11. Media service detection.
12. Media list parsing.
13. Download latest.
14. Download all.
15. Optional GUI.

---

## Acceptance Criteria

The MVP is accepted only when:

```txt
BLE scan works
User can select glasses from terminal
BLE connection succeeds
BLE remains connected
Notifications can be enabled
Battery value can be read
Photo can be captured
Transfer mode can be enabled
Windows connects to glasses Wi-Fi
Device IP 192.168.31.2 is reachable
Media service is reachable
Media list is fetched
Media count is displayed
Latest media is shown
Latest photo downloads to downloads/
All photos can download to downloads/
Errors are clear and recoverable
Diagnostics option still works
```

---

## Important Warning

Do not assume the PyPI package exposes an importable SDK.

Before using any import such as:

```python
import heycyan_glasses_sdk
```

verify it with:

```powershell
pip show -f heycyan-glasses-sdk
python -c "import pkgutil; print([m.name for m in pkgutil.iter_modules() if 'hey' in m.name.lower() or 'cyan' in m.name.lower() or 'glass' in m.name.lower()])"
```

If the package only has `.dist-info`, continue with the current wrapper approach.
