import asyncio
import inspect
from config import (
    SCAN_TIMEOUT,
    KNOWN_GLASSES_ADDRESS,
    KNOWN_GLASSES_NAME,
    KNOWN_GLASSES_NAME_PREFIX,
)
from services.heycyn_sdk import HeyCyanWindowsSDK
from utils.logger import logger


AUTO_STEP_DELAY_SECONDS = 2
AUTO_SCAN_RETRY_DELAY_SECONDS = 5


def print_header(sdk):
    ble_status = "CONNECTED" if sdk.is_ble_connected() else "NOT CONNECTED"

    try:
        transfer_status = (
            "ENABLED" if sdk.is_transfer_mode_enabled() else "NOT ENABLED"
        )
    except Exception:
        transfer_status = "UNKNOWN"

    print("\n" + "=" * 45)
    print("HeyCyan Windows MVP")
    print("=" * 45)
    print(f"BLE Status       : {ble_status}")
    print(f"Transfer Mode    : {transfer_status}")
    print("=" * 45)


def print_menu():
    print("\nChoose")
    print("1. Auto connect, capture, and download latest photo")
    print("2. BLE diagnostics")
    print("3. Exit")


def is_expected_glasses(device):
    name = device.get("name") or ""
    address = device.get("address") or ""

    return (
        address.upper() == KNOWN_GLASSES_ADDRESS.upper()
        or name == KNOWN_GLASSES_NAME
        or name.upper().startswith(KNOWN_GLASSES_NAME_PREFIX.upper())
        or device.get("is_heycyn_match", False)
    )


async def wait_for_expected_glasses(sdk):
    attempt = 1

    while True:
        print(f"\nLooking for expected HeyCyan glasses. Scan attempt {attempt}...")
        logger.info(f"Auto flow BLE scan attempt {attempt}")

        devices = await sdk.scan_glasses(timeout=SCAN_TIMEOUT)

        for device in devices:
            if is_expected_glasses(device):
                print("\nAuto-detected HeyCyan glasses:")
                print(f"Name: {device['name']}")
                print(f"Address: {device['address']}")
                print("Selecting this device automatically.")
                logger.info(
                    f"Auto flow selected glasses: {device['name']} ({device['address']})"
                )
                return device

        message = (
            f"Expected HeyCyan glasses not found. Waiting "
            f"{AUTO_SCAN_RETRY_DELAY_SECONDS}s before retry..."
        )
        print(message)
        logger.warning(message)
        await asyncio.sleep(AUTO_SCAN_RETRY_DELAY_SECONDS)
        attempt += 1


async def run_auto_step(label, action, delay=AUTO_STEP_DELAY_SECONDS):
    print(f"\n--- {label} ---")
    logger.info(f"Auto flow step started: {label}")

    try:
        result = action()

        if inspect.isawaitable(result):
            result = await result

        if result is False or result is None:
            message = f"Auto flow step did not complete successfully: {label}"
            print(message)
            logger.error(message)
        else:
            logger.info(f"Auto flow step completed: {label}")

        if delay:
            await asyncio.sleep(delay)

        return result

    except Exception as e:
        print(f"{label} failed.")
        print("Reason:", e)
        logger.exception(f"Auto flow step failed: {label}")

        if delay:
            await asyncio.sleep(delay)

        return None


async def scan_and_connect(sdk):
    selected = await wait_for_expected_glasses(sdk)
    connected = await sdk.connect_selected_device(selected, retries=3)

    if connected:
        print("\nConnected successfully.")
        logger.info("Auto flow BLE connection completed.")
        return True

    print("\nConnection failed.")
    logger.error("Auto flow BLE connection failed.")
    return False


async def run_auto_flow(sdk):
    print("\nStarting automatic HeyCyan flow...")
    logger.info("Automatic HeyCyan flow started.")

    connected = await scan_and_connect(sdk)

    if not connected:
        print("Could not connect to the expected glasses. Auto flow stopped.")
        return

    await asyncio.sleep(AUTO_STEP_DELAY_SECONDS)

    await run_auto_step("Enable BLE notifications", sdk.enable_notifications)
    await run_auto_step("Get battery value", sdk.get_battery)

    photo_ok = await run_auto_step("Capture photo", sdk.capture_photo)

    if photo_ok is not True:
        print("\nPhoto capture failed. Stopping before transfer mode.")
        print("Run option 2 and send the BLE service/characteristic output.")
        logger.error("Auto flow stopped because photo capture failed.")
        return

    transfer_ok = await run_auto_step("Enable transfer mode", sdk.enable_transfer_mode)

    if transfer_ok is not True:
        print("\nTransfer mode failed. Stopping before Wi-Fi/media/download.")
        print("Run option 2 and send the BLE service/characteristic output.")
        logger.error("Auto flow stopped because transfer mode failed.")
        return

    await run_auto_step("Show available Wi-Fi networks", sdk.show_wifi_networks)
    await run_auto_step("Connect to glasses Wi-Fi", sdk.connect_wifi)
    await run_auto_step("Check device reachable", sdk.check_device_reachable)
    await run_auto_step("Check media service", sdk.check_media_service)
    await run_auto_step("Fetch media config", sdk.fetch_media_config)

    media_list = await run_auto_step("Fetch media list", sdk.fetch_media_list)

    if media_list is False or media_list is None:
        print("\nMedia list failed. Stopping before latest media/download.")
        logger.error("Auto flow stopped because media list fetch failed.")
        return

    count = await run_auto_step("Show media count", sdk.get_media_count, delay=1)
    print(f"\nMedia count: {count if count is not None else 0}")
    logger.info(f"Auto flow media count: {count if count is not None else 0}")

    latest = await run_auto_step("Show latest media", sdk.get_latest_media, delay=1)
    print(f"\nLatest media: {latest}")
    logger.info(f"Auto flow latest media: {latest}")

    downloaded = await run_auto_step("Download latest photo", sdk.download_latest)

    if downloaded:
        print(f"\nLatest photo downloaded: {downloaded}")
        logger.info(f"Auto flow downloaded latest photo: {downloaded}")

    print("\nAutomatic HeyCyan flow finished.")
    logger.info("Automatic HeyCyan flow finished.")


async def handle_choice(choice, sdk):
    if choice == "1":
        await run_auto_flow(sdk)

    elif choice == "2":
        if not sdk.is_ble_connected():
            connected = await scan_and_connect(sdk)

            if not connected:
                print("Could not connect for diagnostics.")
                return True

        await sdk.list_services()

    elif choice == "3":
        await sdk.disconnect()
        print("Exiting app.")
        return False

    else:
        print("Invalid option. Please choose 1, 2, or 3.")

    return True


async def main():
    sdk = HeyCyanWindowsSDK()

    print("\nStarting HeyCyan Windows MVP...")
    print("Select option 1 to auto connect, capture, connect Wi-Fi, and download the latest photo.")

    while True:
        print_header(sdk)
        print_menu()

        choice = input("\nSelect option: ").strip()

        try:
            should_continue = await handle_choice(choice, sdk)

            if not should_continue:
                break

        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            await sdk.disconnect()
            break

        except Exception as e:
            print("\nUnexpected error occurred.")
            print("Reason:", e)
            print("You can continue testing from the menu.")
            logger.exception("Unexpected error in main menu loop.")

    if sdk.is_ble_connected():
        await sdk.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
