import asyncio
from config import HEYCYAN_COMMAND_CHAR_UUID, PHOTO_CAPTURE_COMMAND, PHOTO_CAPTURE_COMMANDS
from utils.logger import logger


class HeyCyanPhotoCapture:
    def __init__(self, connection):
        self.connection = connection

    def is_photo_success_notification(self, notification_history):
        """
        HeyCyan success bytes are not known yet.
        Return False until real notification responses are mapped.
        """
        return False

    def print_enabled_notifications(self):
        print("\nEnabled notification UUIDs:")
        enabled_notify_uuids = self.connection.get_enabled_notify_uuids()

        if enabled_notify_uuids:
            for notify_uuid in enabled_notify_uuids:
                print(f"- {notify_uuid}")
        else:
            print("- None")

        logger.info(f"Enabled notification UUIDs before photo command: {enabled_notify_uuids}")

    def print_notification_history(self, history):
        print("\nNotification responses after photo command:")

        if history:
            for index, notification in enumerate(history, start=1):
                print(f"{index}. Sender UUID: {notification['sender']}")
                print(f"   Timestamp: {notification.get('timestamp')}")
                print(f"   Raw bytes: {notification['data']}")
                print(f"   Hex response: {notification['hex']}")
                logger.info(
                    "Photo notification response %s from %s: %s",
                    index,
                    notification["sender"],
                    notification["hex"],
                )
        else:
            print("No notification response received after photo command.")
            logger.warning("No notification response received after photo command.")

    def ask_photo_confirmation(self, prompt="Did the glasses physically take a photo? (y/n): "):
        answer = input(prompt).strip().lower()
        confirmed = answer == "y"
        logger.info(f"Photo capture user confirmation: {answer}")

        if confirmed:
            logger.info("Photo capture confirmed by user")
            print("Photo capture confirmed by user.")
            return True

        logger.info("Photo capture not confirmed")
        print("Photo capture not confirmed.")
        return False

    async def send_photo_command_and_collect_responses(
        self,
        command,
        command_uuid=HEYCYAN_COMMAND_CHAR_UUID,
        wait_seconds=8,
    ):
        client = self.connection.get_client()

        self.connection.clear_notification_history()

        command_hex = command.hex(" ")

        print("\nSending photo capture command...")
        print(f"Command UUID: {command_uuid}")
        print(f"Command bytes: {command}")
        print(f"Command hex: {command_hex}")
        self.print_enabled_notifications()

        logger.info(f"Photo command UUID: {command_uuid}")
        logger.info(f"Photo command bytes: {command}")
        logger.info(f"Photo command hex: {command_hex}")

        await client.write_gatt_char(
            command_uuid,
            command,
            response=True
        )

        logger.info("Photo capture command sent.")
        print("Photo capture command sent.")
        print(f"\nWaiting {wait_seconds} seconds for notification responses...")
        await asyncio.sleep(wait_seconds)

        history = self.connection.get_notification_history()
        self.print_notification_history(history)

        return history

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

        try:
            history = await self.send_photo_command_and_collect_responses(
                PHOTO_CAPTURE_COMMAND,
            )

            if self.is_photo_success_notification(history):
                logger.info("Photo capture confirmed by notification parser")
                print("Photo capture confirmed by notification parser.")
                return True

            return self.ask_photo_confirmation()

        except Exception as e:
            logger.error(f"Photo capture failed: {e}")
            print("Photo capture failed.")
            print("Reason:", e)
            print("\nNext step: list BLE services/characteristics and confirm command characteristic UUID.")
            return False

    async def test_photo_command_candidates(self):
        client = self.connection.get_client()

        if not client or not client.is_connected:
            print("BLE is not connected. Please connect first.")
            return False

        await self.connection.enable_notifications()

        for index, command in enumerate(PHOTO_CAPTURE_COMMANDS, start=1):
            print("\n" + "=" * 70)
            print(f"Testing photo command candidate {index}/{len(PHOTO_CAPTURE_COMMANDS)}")

            try:
                await self.send_photo_command_and_collect_responses(command)
            except Exception as e:
                logger.error(f"Photo command candidate failed: {command.hex(' ')} - {e}")
                print("Photo command candidate failed.")
                print("Reason:", e)
                continue

            confirmed = self.ask_photo_confirmation(
                "Did photo happen for this command? (y/n): "
            )

            if confirmed:
                command_hex = command.hex(" ")
                print("\nWorking photo command found.")
                print(f"Command bytes: {command}")
                print(f"Command hex: {command_hex}")
                logger.info(f"Selected working photo command candidate: {command_hex}")
                return True

        print("\nNo photo command candidate was confirmed.")
        logger.warning("No photo command candidate was confirmed.")
        return False
