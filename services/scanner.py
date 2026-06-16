import asyncio
from bleak import BleakScanner
from config import (
    HEYCYAN_SERVICE_UUIDS,
    KNOWN_GLASSES_NAME_PREFIX,
    KNOWN_GLASSES_ADDRESS,
    AUTO_SELECT_KNOWN_GLASSES,
)
from utils.logger import logger


class HeyCyanScanner:
    async def scan_glasses(self, timeout=20):
        logger.info(f"Starting BLE scan with timeout {timeout}s")
        print("\nScanning BLE devices...")
        print("Keep glasses ON and near laptop.\n")

        found_devices = {}

        def detection_callback(device, advertisement_data):
            address = device.address
            name = device.name or advertisement_data.local_name or "Unknown"

            service_uuids = [
                uuid.lower()
                for uuid in advertisement_data.service_uuids
            ]

            uuid_match = any(
                uuid in service_uuids
                for uuid in HEYCYAN_SERVICE_UUIDS
            )

            name_match = (
                name != "Unknown"
                and name.upper().startswith(KNOWN_GLASSES_NAME_PREFIX.upper())
            )

            address_match = (
                address.upper() == KNOWN_GLASSES_ADDRESS.upper()
            )

            is_heycyn_match = uuid_match or name_match or address_match

            if is_heycyn_match:
                logger.info(f"Found HeyCyan glasses: {name} ({address})")

            found_devices[address] = {
                "name": name,
                "address": address,
                "rssi": advertisement_data.rssi,
                "service_uuids": service_uuids,
                "manufacturer_data": advertisement_data.manufacturer_data,
                "service_data": advertisement_data.service_data,
                "local_name": advertisement_data.local_name,
                "uuid_match": uuid_match,
                "name_match": name_match,
                "address_match": address_match,
                "is_heycyn_match": is_heycyn_match,
                "raw_device": device,
            }

        scanner = BleakScanner(detection_callback)

        try:
            await scanner.start()
            await asyncio.sleep(timeout)
            await scanner.stop()
        except Exception as e:
            logger.exception("BLE scan failed")
            print("\nBLE scan failed.")
            print("Reason:", e)
            print("\nPlease check:")
            print("1. Windows Bluetooth is ON")
            print("2. Glasses are ON and nearby")
            print("3. Glasses are not connected to phone")
            return []

        devices = list(found_devices.values())

        # Sort matched glasses first, then named devices, then stronger RSSI
        def sort_key(device):
            match_sort = 0 if device["is_heycyn_match"] else 1
            named_sort = 0 if device["name"] != "Unknown" else 1

            rssi = device.get("rssi")
            if rssi is None or rssi == 0:
                rssi_sort = 999
            else:
                rssi_sort = -rssi

            return (match_sort, named_sort, rssi_sort)

        devices.sort(key=sort_key)

        logger.info(f"Scan completed. Found {len(devices)} devices.")
        return devices

    def print_devices(self, devices):
        if not devices:
            print("No BLE devices found.")
            return

        print("\nDevices found:\n")

        for index, device in enumerate(devices, start=1):
            match_text = "YES" if device["is_heycyn_match"] else "NO"

            print(f"{index}. Name: {device['name']}")
            print(f"   Address: {device['address']}")
            print(f"   RSSI: {device['rssi']}")
            print(f"   HeyCyan Match: {match_text}")
            print(f"   UUID Match: {'YES' if device['uuid_match'] else 'NO'}")
            print(f"   Name Match: {'YES' if device['name_match'] else 'NO'}")
            print(f"   Address Match: {'YES' if device['address_match'] else 'NO'}")
            print(f"   Service UUIDs: {device['service_uuids']}")
            print("-" * 70)

    def auto_select_known_glasses(self, devices):
        if not AUTO_SELECT_KNOWN_GLASSES:
            return None

        for device in devices:
            if device["is_heycyn_match"]:
                print("\nAuto-detected HeyCyan glasses:")
                print(f"Name: {device['name']}")
                print(f"Address: {device['address']}")
                print("Selecting this device automatically.")
                logger.info(
                    f"Auto-selected HeyCyan glasses: {device['name']} ({device['address']})"
                )
                return device

        return None

    def select_device_from_terminal(self, devices):
        if not devices:
            return None

        auto_selected = self.auto_select_known_glasses(devices)

        if auto_selected:
            return auto_selected

        while True:
            choice = input("\nEnter device number to connect, or 0 to cancel: ").strip()

            if choice == "0":
                logger.info("Device selection cancelled by user.")
                print("Selection cancelled.")
                return None

            if not choice.isdigit():
                print("Please enter a valid number.")
                continue

            index = int(choice)

            if 1 <= index <= len(devices):
                selected = devices[index - 1]
                logger.info(
                    f"User selected device: {selected['name']} ({selected['address']})"
                )
                print(f"\nSelected device: {selected['name']} - {selected['address']}")

                if not selected["is_heycyn_match"]:
                    print("\nWarning: This device is not confirmed as HeyCyan.")

                return selected

            print("Invalid selection. Try again.")