from utils.logger import logger


class HeyCyanDiagnostics:
    def __init__(self, connection):
        self.connection = connection

    async def list_services(self):
        client = self.connection.get_client()

        if not client or not client.is_connected:
            print("BLE is not connected. Cannot list services.")
            logger.warning("Diagnostics requested but BLE is not connected.")
            return False

        print("\nListing BLE services and characteristics...\n")
        logger.info("Listing BLE services and characteristics.")

        try:
            # Bleak 3.x uses client.services property.
            # Older examples may use await client.get_services(), but that fails here.
            services = client.services

            if not services:
                print("No BLE services found.")
                logger.warning("No BLE services found from client.services.")
                return False

            notify_candidates = []
            write_candidates = []
            read_candidates = []

            for service in services:
                print("=" * 80)
                print(f"Service UUID : {service.uuid}")
                print(f"Service Desc : {getattr(service, 'description', '')}")
                print("=" * 80)

                logger.info(f"Service UUID: {service.uuid}")

                for char in service.characteristics:
                    properties = list(char.properties)

                    print(f"  Characteristic UUID : {char.uuid}")
                    print(f"  Description         : {getattr(char, 'description', '')}")
                    print(f"  Properties          : {properties}")
                    print("-" * 80)

                    logger.info(
                        f"Characteristic UUID: {char.uuid}, Properties: {properties}"
                    )

                    if "notify" in properties or "indicate" in properties:
                        notify_candidates.append(char.uuid)

                    if "write" in properties or "write-without-response" in properties:
                        write_candidates.append(char.uuid)

                    if "read" in properties:
                        read_candidates.append(char.uuid)

            print("\nSuggested UUID Candidates")
            print("=" * 80)

            print("\nNotify / Indicate candidates:")
            if notify_candidates:
                for uuid in notify_candidates:
                    print(f"  HEYCYAN_NOTIFY_CHAR_UUID = \"{uuid}\"")
            else:
                print("  No notify/indicate characteristic found.")

            print("\nWrite / Command candidates:")
            if write_candidates:
                for uuid in write_candidates:
                    print(f"  HEYCYAN_COMMAND_CHAR_UUID = \"{uuid}\"")
            else:
                print("  No write/write-without-response characteristic found.")

            print("\nRead candidates:")
            if read_candidates:
                for uuid in read_candidates:
                    print(f"  Possible read/battery UUID = \"{uuid}\"")
            else:
                print("  No read characteristic found.")

            print("\nNext step:")
            print("1. Copy notify candidate into HEYCYAN_NOTIFY_CHAR_UUID")
            print("2. Copy write candidate into HEYCYAN_COMMAND_CHAR_UUID")
            print("3. Test option 1 again")
            print("4. If multiple candidates exist, test one by one")

            logger.info(f"Notify candidates: {notify_candidates}")
            logger.info(f"Write candidates: {write_candidates}")
            logger.info(f"Read candidates: {read_candidates}")

            return {
                "notify_candidates": notify_candidates,
                "write_candidates": write_candidates,
                "read_candidates": read_candidates,
            }

        except Exception as e:
            print("\nFailed to list services.")
            print("Reason:", e)

            logger.exception("Failed to list BLE services.")
            return False