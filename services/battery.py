from config import BATTERY_LEVEL_UUID


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

        print("\nRequesting battery value...")

        try:
            data = await client.read_gatt_char(BATTERY_LEVEL_UUID)

            if not data:
                print("Battery read failed: empty response.")
                return None

            battery_percentage = int(data[0])

            print(f"Battery: {battery_percentage}%")
            print("Charging: Unknown in this first test")

            return {
                "battery": battery_percentage,
                "charging": None,
            }

        except Exception as e:
            print("Battery read failed.")
            print("Reason:", e)
            print("\nNext step: choose option 3 and list BLE services/characteristics.")
            return None