from utils.logger import logger

class HeyCyanDiagnostics:
    def __init__(self, connection):
        self.connection = connection

    async def list_services(self):
        client = self.connection.get_client()

        if not client or not client.is_connected:
            logger.warning("Diagnostics requested but BLE is not connected.")
            print("BLE is not connected. Please connect first.")
            return

        logger.info("Starting BLE service/characteristic listing.")
        print("\nListing BLE services and characteristics...\n")

        try:
            services = await client.get_services()

            for service in services:
                logger.info(f"Service Found: {service.uuid}")
                print(f"Service: {service.uuid}")

                for char in service.characteristics:
                    logger.info(f"  - Char: {char.uuid} Prop: {char.properties}")
                    print(f"  Characteristic: {char.uuid}")
                    print(f"  Properties: {char.properties}")

                print("-" * 70)

        except Exception as e:
            logger.error(f"Failed to list services: {e}")
            print("Failed to list services.")
            print("Reason:", e)
