import asyncio
from config import HEYCYAN_COMMAND_CHAR_UUID, PHOTO_CAPTURE_COMMAND
from utils.logger import logger


class HeyCyanPhotoCapture:
    def __init__(self, connection):
        self.connection = connection

    async def capture_photo(self):
        """
        HeyCyan SDK equivalent:
        take photo / capture photo command.

        This sends a BLE command to glasses.
        Actual command bytes may need confirmation from HeyCyan protocol.
        """
        client = self.connection.get_client()

        if not client or not client.is_connected:
            print("BLE is not connected. Please connect first.")
            return False

        logger.info(f"Sending photo capture command to {HEYCYAN_COMMAND_CHAR_UUID}")
        print("\nSending photo capture command...")
        self.connection.clear_notification_history()

        try:
            await client.write_gatt_char(
                HEYCYAN_COMMAND_CHAR_UUID,
                PHOTO_CAPTURE_COMMAND,
                response=True
            )

            logger.info("Photo capture command sent.")
            print("Photo capture command sent.")
            print("\nEnabled notification UUIDs:")

            enabled_notify_uuids = self.connection.get_enabled_notify_uuids()

            if enabled_notify_uuids:
                for notify_uuid in enabled_notify_uuids:
                    print(f"- {notify_uuid}")
            else:
                print("- None")

            print("\nWaiting 5 seconds for notification responses...")
            await asyncio.sleep(5)

            history = self.connection.get_notification_history()

            print("\nNotification responses after photo command:")

            if history:
                for index, notification in enumerate(history, start=1):
                    print(f"{index}. Sender UUID: {notification['sender']}")
                    print(f"   Raw bytes: {notification['data']}")
                    print(f"   Hex data: {notification['hex']}")
            else:
                print("No notification responses received.")

            print("\nPlease check the glasses/gallery and confirm whether a photo was actually taken.")
            return True

        except Exception as e:
            logger.error(f"Photo capture failed: {e}")
            print("Photo capture failed.")
            print("Reason:", e)
            print("\nNext step: list BLE services/characteristics and confirm command characteristic UUID.")
            return False
