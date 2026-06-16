import asyncio
from bleak import BleakClient
from config import HEYCYAN_NOTIFY_CHAR_UUID
from utils.logger import logger


class HeyCyanConnection:
    def __init__(self):
        self.client = None
        self.selected_device = None
        self.is_connected = False
        self.notifications_enabled = False
        self.last_notification_data = None

    async def connect(self, selected_device, retries=2):
        if not selected_device:
            print("No device selected.")
            logger.warning("Connect called without selected device.")
            return False

        self.selected_device = selected_device

        address = selected_device.get("address")
        name = selected_device.get("name", "Unknown")
        raw_device = selected_device.get("raw_device")

        print(f"\nConnecting to {name} - {address}...")
        logger.info(f"Connecting to device: {name} ({address})")

        # Clean old connection before new connection attempt
        await self.disconnect_silent()

        for attempt in range(1, retries + 1):
            print(f"\nBLE connection attempt {attempt}/{retries}...")
            logger.info(f"BLE connection attempt {attempt}/{retries} for {name} ({address})")

            try:
                # On Windows, raw BLEDevice object is more reliable than address-only.
                if raw_device:
                    self.client = BleakClient(raw_device, timeout=30.0)
                else:
                    self.client = BleakClient(address, timeout=30.0)

                await self.client.connect()

                self.is_connected = bool(self.client.is_connected)

                if self.is_connected:
                    print("BLE connected successfully.")
                    logger.info(f"BLE connected successfully: {name} ({address})")

                    # Notification enable is helpful, but should not make connection fail.
                    notification_ok = await self.enable_notifications()

                    if not notification_ok:
                        print("\nBLE is connected, but notifications are not enabled yet.")
                        print("This is okay for now. Choose option 4 to list services/characteristics.")
                        print("Then update HEYCYAN_NOTIFY_CHAR_UUID in config.py.")

                    return True

                print("BLE connection failed.")
                logger.error(f"BLE connection failed: {name} ({address})")

            except Exception as e:
                self.is_connected = False
                logger.exception(f"BLE connection error for {name} ({address})")

                print(f"BLE connection error: {e}")

                if attempt < retries:
                    print("Retrying connection in 2 seconds...")
                    await asyncio.sleep(2)
                else:
                    self.print_connection_help()

        return False

    def notification_handler(self, sender, data):
        self.last_notification_data = data

        hex_data = data.hex(" ")

        print("\nNotification received")
        print(f"From: {sender}")
        print(f"Raw bytes: {data}")
        print(f"Hex: {hex_data}")

        logger.info(f"Notification from {sender}: {hex_data}")

    async def enable_notifications(self):
        if not self.client or not self.client.is_connected:
            print("BLE is not connected. Cannot enable notifications.")
            logger.warning("Enable notifications called without BLE connection.")
            return False

        if self.notifications_enabled:
            print("BLE notifications already enabled.")
            return True

        print("\nEnabling BLE notifications...")
        logger.info(f"Enabling notifications on UUID: {HEYCYAN_NOTIFY_CHAR_UUID}")

        try:
            await self.client.start_notify(
                HEYCYAN_NOTIFY_CHAR_UUID,
                self.notification_handler
            )

            self.notifications_enabled = True
            print("BLE notifications enabled.")
            logger.info("BLE notifications enabled.")
            return True

        except Exception as e:
            self.notifications_enabled = False

            print("Could not enable notifications with current notify UUID.")
            print("Reason:", e)
            print("After connecting, choose option 4 to list BLE services/characteristics.")
            print("Look for characteristic with property: notify / indicate.")
            print("Then update HEYCYAN_NOTIFY_CHAR_UUID in config.py.")

            logger.exception("Failed to enable BLE notifications.")
            return False

    async def disable_notifications(self):
        if not self.client or not self.client.is_connected:
            self.notifications_enabled = False
            return

        if not self.notifications_enabled:
            return

        print("\nDisabling BLE notifications...")

        try:
            await self.client.stop_notify(HEYCYAN_NOTIFY_CHAR_UUID)
            self.notifications_enabled = False
            print("BLE notifications disabled.")
            logger.info("BLE notifications disabled.")

        except Exception as e:
            self.notifications_enabled = False
            print("Could not disable notifications.")
            print("Reason:", e)
            logger.exception("Failed to disable notifications.")

    async def disconnect(self):
        if self.client and self.client.is_connected:
            await self.disable_notifications()

            try:
                await self.client.disconnect()
                print("BLE disconnected.")
                logger.info("BLE disconnected.")
            except Exception as e:
                print("BLE disconnect error:", e)
                logger.exception("BLE disconnect error.")

        self.client = None
        self.is_connected = False
        self.notifications_enabled = False

    async def disconnect_silent(self):
        try:
            if self.client and self.client.is_connected:
                try:
                    if self.notifications_enabled:
                        await self.disable_notifications()
                except Exception:
                    pass

                await self.client.disconnect()

        except Exception:
            pass

        self.client = None
        self.is_connected = False
        self.notifications_enabled = False

    def get_client(self):
        return self.client

    def is_ble_connected(self):
        return self.client is not None and self.client.is_connected

    def get_last_notification_data(self):
        return self.last_notification_data

    def print_connection_help(self):
        print("\nConnection failed after retries.")
        print("\nPossible reasons:")
        print("1. Glasses stopped advertising after scan.")
        print("2. Glasses are already connected to phone or another app.")
        print("3. Windows shows Bluetooth paired, but BLE GATT connection is not active.")
        print("4. Device moved away or went to sleep.")
        print("5. Wrong device selected.")
        print("\nTry this:")
        print("1. Turn OFF Bluetooth on the phone.")
        print("2. Restart the glasses.")
        print("3. Keep glasses very close to laptop.")
        print("4. Run scan again.")
        print("5. Select V03._982A quickly.")