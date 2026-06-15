import asyncio
from config import HEYCYAN_COMMAND_CHAR_UUID, TRANSFER_MODE_COMMAND


class HeyCyanTransferMode:
    def __init__(self, connection):
        self.connection = connection
        self.transfer_mode_enabled = False

    async def enable_transfer_mode(self):
        """
        HeyCyan SDK equivalent:
        enable Wi-Fi transfer / media transfer mode.

        BLE must remain connected.
        After this, glasses should start Wi-Fi hotspot / transfer service.
        """
        client = self.connection.get_client()

        if not client or not client.is_connected:
            print("BLE is not connected. Please connect first.")
            return False

        print("\nSending transfer mode command...")

        try:
            await client.write_gatt_char(
                HEYCYAN_COMMAND_CHAR_UUID,
                TRANSFER_MODE_COMMAND,
                response=True
            )

            print("Transfer mode command sent.")
            print("Waiting for glasses to enable Wi-Fi transfer mode...")

            await asyncio.sleep(5)

            self.transfer_mode_enabled = True
            print("Transfer mode command sent.")
            print("Please verify that the glasses Wi-Fi SSID is visible before continuing.")
            return True

        except Exception as e:
            print("Transfer mode failed.")
            print("Reason:", e)
            print("\nNext step: confirm command characteristic UUID and transfer command bytes.")
            self.transfer_mode_enabled = False
            return False

    def is_transfer_mode_enabled(self):
        return self.transfer_mode_enabled