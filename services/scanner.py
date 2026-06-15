import asyncio
from bleak import BleakScanner
from config import HEYCYAN_SERVICE_UUIDS


class HeyCyanScanner:
    async def scan_glasses(self, timeout=20):
        print("\nScanning BLE devices...")
        print("Keep glasses ON and near laptop.\n")

        found_devices = {}

        def detection_callback(device, advertisement_data):
            address = device.address

            service_uuids = [
                uuid.lower()
                for uuid in advertisement_data.service_uuids
            ]

            is_heycyn_match = any(
                uuid in service_uuids
                for uuid in HEYCYAN_SERVICE_UUIDS
            )

            found_devices[address] = {
                "name": device.name or advertisement_data.local_name or "Unknown",
                "address": address,
                "rssi": advertisement_data.rssi,
                "service_uuids": service_uuids,
                "manufacturer_data": advertisement_data.manufacturer_data,
                "is_heycyn_match": is_heycyn_match,
                "raw_device": device,
            }

        scanner = BleakScanner(detection_callback)
        await scanner.start()
        await asyncio.sleep(timeout)
        await scanner.stop()

        return list(found_devices.values())

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
            print(f"   HeyCyan UUID Match: {match_text}")
            print(f"   Service UUIDs: {device['service_uuids']}")
            print("-" * 70)

    def select_device_from_terminal(self, devices):
        if not devices:
            return None

        while True:
            choice = input("\nEnter device number to connect, or 0 to cancel: ").strip()

            if choice == "0":
                print("Selection cancelled.")
                return None

            if not choice.isdigit():
                print("Please enter a valid number.")
                continue

            index = int(choice)

            if 1 <= index <= len(devices):
                selected = devices[index - 1]
                print(f"\nSelected device: {selected['name']} - {selected['address']}")
                return selected

            print("Invalid selection. Try again.")