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

        try:
            await client.write_gatt_char(
                HEYCYAN_COMMAND_CHAR_UUID,
                PHOTO_CAPTURE_COMMAND,
                response=True
            )

            logger.info("Photo capture command sent successfully.")
            print("Photo capture command sent successfully.")
            return True

        except Exception as e:
            logger.error(f"Photo capture failed: {e}")
            print("Photo capture failed.")
            print("Reason:", e)
            print("\nNext step: list BLE services/characteristics and confirm command characteristic UUID.")
            return False
