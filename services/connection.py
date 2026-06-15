from bleak import BleakClient
from config import HEYCYAN_NOTIFY_CHAR_UUID


class HeyCyanConnection:
    def __init__(self):
        self.client = None
        self.selected_device = None
        self.is_connected = False
        self.notifications_enabled = False
        self.last_notification_data = None

    async def connect(self, selected_device):
        if not selected_device:
            print("No device selected.")
            return False

        self.selected_device = selected_device
        address = selected_device["address"]

        print(f"\nConnecting to {address}...")

        try:
            self.client = BleakClient(address)
            await self.client.connect()

            self.is_connected = self.client.is_connected

            if self.is_connected:
                print("BLE connected successfully.")

                # Enable notifications immediately after connection
                await self.enable_notifications()

                return True

            print("BLE connection failed.")
            return False

        except Exception as e:
            print(f"BLE connection error: {e}")
            self.is_connected = False
            return False

    def notification_handler(self, sender, data):
        self.last_notification_data = data

        print("\nNotification received")
        print(f"From: {sender}")
        print(f"Raw bytes: {data}")
        print(f"Hex: {data.hex(' ')}")

    async def enable_notifications(self):
        if not self.client or not self.client.is_connected:
            print("BLE is not connected. Cannot enable notifications.")
            return False

        print("\nEnabling BLE notifications...")

        try:
            await self.client.start_notify(
                HEYCYAN_NOTIFY_CHAR_UUID,
                self.notification_handler
            )

            self.notifications_enabled = True
            print("BLE notifications enabled.")
            return True

        except Exception as e:
            self.notifications_enabled = False
            print("Could not enable notifications with current notify UUID.")
            print("Reason:", e)
            print("After connecting, choose option 4 to list BLE services/characteristics.")
            return False

    async def disable_notifications(self):
        if not self.client or not self.client.is_connected:
            return

        if not self.notifications_enabled:
            return

        try:
            await self.client.stop_notify(HEYCYAN_NOTIFY_CHAR_UUID)
            self.notifications_enabled = False
            print("BLE notifications disabled.")
        except Exception as e:
            print("Could not disable notifications.")
            print("Reason:", e)

    async def disconnect(self):
        if self.client and self.client.is_connected:
            await self.disable_notifications()
            await self.client.disconnect()
            print("BLE disconnected.")

        self.is_connected = False

    def get_client(self):
        return self.client

    def is_ble_connected(self):
        return self.client is not None and self.client.is_connected

    def get_last_notification_data(self):
        return self.last_notification_data