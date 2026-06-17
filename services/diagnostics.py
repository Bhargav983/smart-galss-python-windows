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
            notify_candidates = []
            write_candidates = []
            battery_candidates = []

            for service in services:
                logger.info(f"Service Found: {service.uuid}")
                print(f"Service: {service.uuid}")

                for char in service.characteristics:
                    properties = [prop.lower() for prop in char.properties]
                    logger.info(f"  - Char: {char.uuid} Prop: {char.properties}")
                    print(f"  Characteristic: {char.uuid}")
                    print(f"  Properties: {char.properties}")

                    if "notify" in properties or "indicate" in properties:
                        notify_candidates.append(char)

                    if "write" in properties or "write-without-response" in properties:
                        write_candidates.append(char)

                    description = getattr(char, "description", "") or ""
                    lower_description = description.lower()
                    lower_uuid = char.uuid.lower()

                    if (
                        "read" in properties
                        and (
                            "battery" in lower_description
                            or "2a19" in lower_uuid
                            or "batt" in lower_description
                        )
                    ):
                        battery_candidates.append(char)

                print("-" * 70)

            self.print_suggestions(
                notify_candidates,
                write_candidates,
                battery_candidates,
            )
            return True

        except Exception as e:
            logger.error(f"Failed to list services: {e}")
            print("Failed to list services.")
            print("Reason:", e)
            return False

    def print_suggestions(self, notify_candidates, write_candidates, battery_candidates):
        print("\nSuggested candidates")
        print("-" * 70)

        self.print_candidate_group(
            "Notify / indicate characteristic candidates",
            notify_candidates,
        )
        self.print_candidate_group(
            "Write / write-without-response characteristic candidates",
            write_candidates,
        )
        self.print_candidate_group(
            "Readable battery-like characteristic candidates",
            battery_candidates,
        )

        print("\nUse these suggestions to update config.py if the current UUIDs fail.")
        logger.info(
            "Diagnostics suggestions - notify: %s, write: %s, battery: %s",
            [char.uuid for char in notify_candidates],
            [char.uuid for char in write_candidates],
            [char.uuid for char in battery_candidates],
        )

    def print_candidate_group(self, title, candidates):
        print(f"\n{title}:")

        if not candidates:
            print("  None found")
            return

        for char in candidates:
            description = getattr(char, "description", "") or ""
            print(f"  UUID: {char.uuid}")
            print(f"  Properties: {char.properties}")

            if description:
                print(f"  Description: {description}")
