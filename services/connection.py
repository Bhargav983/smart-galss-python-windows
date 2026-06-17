import asyncio
import inspect
from datetime import datetime
from bleak import BleakClient
from config import HEYCYAN_NOTIFY_CHAR_UUIDS
from utils.heycyn_sdk_probe import find_notification_function, import_candidate_modules
from utils.logger import logger


class HeyCyanConnection:
    def __init__(self):
        self.client = None
        self.selected_device = None
        self.is_connected = False
        self.notifications_enabled = False
        self.last_notification_data = None
        self.enabled_notify_uuids = []
        self.notification_history = []

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
                        print("This is okay for now. Choose option 2 to list services/characteristics.")
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
        notification = {
            "sender": str(sender),
            "data": data,
            "hex": hex_data,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        self.notification_history.append(notification)

        print("\nNotification received")
        print(f"Sender UUID: {sender}")
        print(f"Raw bytes: {data}")
        print(f"Hex data: {hex_data}")

        logger.info(f"Notification from {sender}: {hex_data}")

    async def enable_notifications(self):
        if not self.client or not self.client.is_connected:
            print("BLE is not connected. Cannot enable notifications.")
            logger.warning("Enable notifications called without BLE connection.")
            return False

        if self.notifications_enabled:
            print("BLE notifications already enabled.")
            return True

        sdk_notification_ok = await self.try_sdk_notifications()

        if sdk_notification_ok:
            return True

        logger.info("Using BLE UUID fallback")
        print("\nEnabling BLE notifications...")

        self.enabled_notify_uuids = []
        failed_notify_uuids = []

        for notify_uuid in HEYCYAN_NOTIFY_CHAR_UUIDS:
            logger.info(f"Enabling notifications on UUID: {notify_uuid}")

            try:
                await self.client.start_notify(
                    notify_uuid,
                    self.notification_handler
                )
                self.enabled_notify_uuids.append(notify_uuid)
                print(f"BLE notifications enabled: {notify_uuid}")
                logger.info(f"BLE notifications enabled: {notify_uuid}")

            except Exception as e:
                failed_notify_uuids.append(notify_uuid)
                print(f"Could not enable notifications: {notify_uuid}")
                print("Reason:", e)
                logger.exception(f"Failed to enable BLE notifications: {notify_uuid}")

        self.notifications_enabled = bool(self.enabled_notify_uuids)

        if self.notifications_enabled:
            print("\nEnabled notification UUIDs:")

            for notify_uuid in self.enabled_notify_uuids:
                print(f"- {notify_uuid}")

            if failed_notify_uuids:
                print("\nFailed notification UUIDs:")

                for notify_uuid in failed_notify_uuids:
                    print(f"- {notify_uuid}")

            logger.info(f"Enabled notification UUIDs: {self.enabled_notify_uuids}")
            logger.info(f"Failed notification UUIDs: {failed_notify_uuids}")
            return True

        print("Could not enable any BLE notification UUID.")
        print("After connecting, choose option 2 to list BLE services/characteristics.")
        print("Look for characteristic with property: notify / indicate.")
        print("Then update HEYCYAN_NOTIFY_CHAR_UUIDS in config.py.")
        logger.error("No BLE notification UUIDs could be enabled.")
        return False

    async def try_sdk_notifications(self):
        imported_modules, failed_imports = import_candidate_modules()

        if imported_modules:
            logger.info("HeyCyan SDK imported")
        else:
            logger.info("HeyCyan SDK not importable")

        for module_name, error in failed_imports:
            logger.info(f"HeyCyan SDK import failed for {module_name}: {error}")

        _module, method_name, method = find_notification_function()

        if not method:
            logger.info("SDK notification method not found")
            return False

        logger.info(f"SDK notification method found: {method_name}")

        try:
            signature = inspect.signature(method)
            params = [
                param
                for param in signature.parameters.values()
                if param.default is inspect.Signature.empty
                and param.kind in (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            ]

            if len(params) == 0:
                result = method()
            elif len(params) == 1:
                result = method(self.client)
            elif len(params) == 2:
                result = method(self.client, self.notification_handler)
            else:
                logger.warning(
                    f"SDK notification method found but unsupported signature: {method_name}{signature}"
                )
                return False

            if inspect.isawaitable(result):
                result = await result

            if result is False:
                logger.error(f"SDK notification method returned False: {method_name}")
                return False

            self.notifications_enabled = True
            print("BLE notifications enabled using HeyCyan SDK.")
            logger.info(f"BLE notifications enabled using SDK method: {method_name}")
            return True

        except Exception as e:
            logger.exception(f"SDK notification method failed: {method_name}")
            print("HeyCyan SDK notification method failed.")
            print("Reason:", e)
            return False

    async def disable_notifications(self):
        if not self.client or not self.client.is_connected:
            self.notifications_enabled = False
            self.enabled_notify_uuids = []
            return

        if not self.notifications_enabled:
            return

        print("\nDisabling BLE notifications...")

        for notify_uuid in list(self.enabled_notify_uuids):
            try:
                await self.client.stop_notify(notify_uuid)
                print(f"BLE notifications disabled: {notify_uuid}")
                logger.info(f"BLE notifications disabled: {notify_uuid}")

            except Exception as e:
                print(f"Could not disable notifications: {notify_uuid}")
                print("Reason:", e)
                logger.exception(f"Failed to disable notifications: {notify_uuid}")

        self.notifications_enabled = False
        self.enabled_notify_uuids = []

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
        self.enabled_notify_uuids = []

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
        self.enabled_notify_uuids = []
        

    def get_client(self):
        return self.client

    def is_ble_connected(self):
        return self.client is not None and self.client.is_connected

    def get_last_notification_data(self):
        return self.last_notification_data

    def clear_notification_history(self):
        self.notification_history = []
        self.last_notification_data = None

    def get_notification_history(self):
        return list(self.notification_history)

    def get_enabled_notify_uuids(self):
        return list(self.enabled_notify_uuids)

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
