from config import BATTERY_LEVEL_UUID
from utils.logger import logger


class HeyCyanBattery:
    def __init__(self, connection):
        self.connection = connection

    async def get_battery(self):
        """
        HeyCyan SDK equivalent:
        getDeviceBattery

        MVP first test:
        Read standard BLE Battery Level characteristic.
        """
        client = self.connection.get_client()

        if not client or not client.is_connected:
            print("BLE is not connected. Please connect first.")
            return None

        logger.info("Requesting battery value...")
        print("\nRequesting battery value...")

        try:
            data = await client.read_gatt_char(BATTERY_LEVEL_UUID)

            if not data:
                logger.error("Battery read failed: empty response.")
                print("Battery read failed: empty response.")
                return None

            battery_percentage = int(data[0])
            logger.info(f"Battery level received: {battery_percentage}%")

            print(f"Battery: {battery_percentage}%")
            print("Charging: Unknown in this first test")

            return {
                "battery": battery_percentage,
                "charging": None,
            }

        except Exception as e:
            logger.error(f"Battery read failed: {e}")
            print("Battery read failed.")
            print("Reason:", e)
            print("\nNext step: choose option 4 and list BLE services/characteristics.")
            return None
