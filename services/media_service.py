import requests
from config import MEDIA_CONFIG_URL, MEDIA_LIST_URL, MEDIA_BASE_URL
from utils.logger import logger


class HeyCyanMediaService:
    def __init__(self):
        self.media_list = []

    def check_media_service(self):
        logger.info(f"Checking media service at {MEDIA_BASE_URL}")
        print("\nChecking media service...")

        try:
            response = requests.get(MEDIA_BASE_URL, timeout=5)

            logger.info(f"Media service status: {response.status_code}")
            print("Media service status:", response.status_code)

            if response.status_code in [200, 301, 302, 403, 404]:
                print("Media service is reachable.")
                return True

            print("Media service responded but not expected.")
            return False

        except Exception as e:
            logger.error(f"Media service not reachable: {e}")
            print("Media service not reachable.")
            print("Reason:", e)
            return False

    def fetch_media_config(self):
        logger.info(f"Fetching media config from {MEDIA_CONFIG_URL}")
        print("\nFetching media config...")

        try:
            response = requests.get(MEDIA_CONFIG_URL, timeout=10)

            logger.info(f"Config status: {response.status_code}")
            print("Config status:", response.status_code)
            print("Config response preview:")
            print(response.text[:500])

            if response.status_code == 200:
                return response.text

            return None

        except Exception as e:
            logger.error(f"Failed to fetch media config: {e}")
            print("Failed to fetch media config.")
            print("Reason:", e)
            return None

    def fetch_media_list(self):
        logger.info(f"Fetching media list from {MEDIA_LIST_URL}")
        print("\nFetching media list...")

        try:
            response = requests.get(MEDIA_LIST_URL, timeout=10)

            logger.info(f"Media list status: {response.status_code}")
            print("Media list status:", response.status_code)
            print("Media list response preview:")
            print(response.text[:1000])

            if response.status_code != 200:
                logger.error("Media list request failed.")
                print("Media list request failed.")
                self.media_list = []
                return False

            data = response.json()

            if isinstance(data, list):
                self.media_list = data

            elif isinstance(data, dict):
                possible_keys = ["files", "media", "list", "data", "items"]
                self.media_list = []

                for key in possible_keys:
                    if key in data and isinstance(data[key], list):
                        self.media_list = data[key]
                        break

                if not self.media_list:
                    logger.error("Media list response did not contain a usable list.")
                    print("Media list response did not contain a usable list.")
                    return False

            else:
                self.media_list = []
                logger.error("Media list response was not a list or supported object.")
                print("Media list response was not a list or supported object.")
                return False

            logger.info(f"Media count loaded: {len(self.media_list)}")
            print(f"Media count loaded: {len(self.media_list)}")
            return self.media_list

        except Exception as e:
            logger.error(f"Failed to fetch media list: {e}")
            print("Failed to fetch media list.")
            print("Reason:", e)
            self.media_list = []
            return False

    def get_media_count(self):
        return len(self.media_list)

    def get_latest_media(self):
        if not self.media_list:
            print("No media found.")
            return None

        latest = self.media_list[-1]
        print("Latest media:", latest)
        return latest

    def get_download_url(self, media_item):
        if not media_item:
            return None

        if isinstance(media_item, str):
            if media_item.startswith("http"):
                return media_item
            return f"{MEDIA_BASE_URL}/{media_item.lstrip('/')}"

        if isinstance(media_item, dict):
            for key in ["url", "download_url", "path", "file", "name"]:
                value = media_item.get(key)

                if value:
                    if str(value).startswith("http"):
                        return value
                    return f"{MEDIA_BASE_URL}/{str(value).lstrip('/')}"

        return None
