import asyncio
from config import SCAN_TIMEOUT
from services.heycyn_sdk import HeyCyanWindowsSDK


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
    print("\nBLE / Diagnostics")
    print("1.  Scan and connect Bluetooth device")
    print("2.  Enable BLE notifications")
    print("3.  Get battery value")
    print("4.  List BLE services/characteristics")
    print("5.  Capture photo")
    print("6.  Enable transfer mode")

    print("\nWi-Fi / Gallery")
    print("7.  Show available Wi-Fi networks")
    print("8.  Show current Wi-Fi")
    print("9.  Connect to glasses Wi-Fi")
    print("10. Check device reachable")
    print("11. Check media service")
    print("12. Fetch media config")
    print("13. Fetch media list")
    print("14. Show media count")
    print("15. Show latest media")
    print("16. Download latest photo")
    print("17. Download all photos")

    print("\nApp")
    print("18. Disconnect BLE")
    print("19. Exit")


async def scan_and_connect(sdk):
    devices = await sdk.scan_glasses(timeout=SCAN_TIMEOUT)
    sdk.print_devices(devices)

    selected = sdk.select_device_from_terminal(devices)

    if selected:
        connected = await sdk.connect_selected_device(selected)

        if connected:
            print("\nConnected successfully.")
            print("Notifications will be enabled automatically if the notify UUID is correct.")
        else:
            print("\nConnection failed.")


async def handle_choice(choice, sdk):
    if choice == "1":
        await scan_and_connect(sdk)

    elif choice == "2":
        await sdk.enable_notifications()

    elif choice == "3":
        await sdk.get_battery()

    elif choice == "4":
        await sdk.list_services()

    elif choice == "5":
        await sdk.capture_photo()

    elif choice == "6":
        await sdk.enable_transfer_mode()

    elif choice == "7":
        sdk.show_wifi_networks()

    elif choice == "8":
        sdk.show_current_wifi()

    elif choice == "9":
        sdk.connect_wifi()

    elif choice == "10":
        sdk.check_device_reachable()

    elif choice == "11":
        sdk.check_media_service()

    elif choice == "12":
        sdk.fetch_media_config()

    elif choice == "13":
        sdk.fetch_media_list()

    elif choice == "14":
        count = sdk.get_media_count()
        print(f"\nMedia count: {count}")

    elif choice == "15":
        latest = sdk.get_latest_media()
        print(f"\nLatest media: {latest}")

    elif choice == "16":
        sdk.download_latest()

    elif choice == "17":
        sdk.download_all()

    elif choice == "18":
        await sdk.disconnect()

    elif choice == "19":
        await sdk.disconnect()
        print("Exiting app.")
        return False

    else:
        print("Invalid option. Please try again.")

    return True


async def main():
    sdk = HeyCyanWindowsSDK()

    print("\nStarting HeyCyan Windows MVP...")
    print("Recommended test order:")
    print("1 → 4 → 2 → 3 → 5 → 6 → 9 → 10 → 11 → 13 → 14 → 16")

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


if __name__ == "__main__":
    asyncio.run(main())