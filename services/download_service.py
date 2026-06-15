import os
import requests
from urllib.parse import urlparse
from config import DOWNLOAD_FOLDER


class HeyCyanDownloadService:
    def __init__(self):
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    def get_filename_from_url(self, url, fallback_name="heycyn_image.jpg"):
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)

            if filename:
                return filename

            return fallback_name

        except Exception:
            return fallback_name

    def download_file(self, url, filename=None):
        if not url:
            print("Download failed: URL is empty.")
            return None

        if not filename:
            filename = self.get_filename_from_url(url)

        save_path = os.path.join(DOWNLOAD_FOLDER, filename)

        print(f"\nDownload started: {url}")
        print(f"Saving to: {save_path}")

        try:
            with requests.get(url, stream=True, timeout=30) as response:
                response.raise_for_status()

                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0

                with open(save_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)

                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                print(f"Download progress: {progress:.2f}%", end="\r")

            print("\nDownload completed.")
            return save_path

        except Exception as e:
            print("\nDownload failed.")
            print("Reason:", e)
            return None

    def download_latest(self, media_service):
        latest = media_service.get_latest_media()

        if not latest:
            print("No latest media available.")
            return None

        url = media_service.get_download_url(latest)

        if not url:
            print("Could not create download URL for latest media.")
            return None

        return self.download_file(url)

    def download_all(self, media_service):
        media_list = media_service.media_list

        if not media_list:
            print("No media available to download.")
            return []

        downloaded_files = []

        print(f"\nDownloading all media files. Count: {len(media_list)}")

        for index, media_item in enumerate(media_list, start=1):
            print(f"\nDownloading {index}/{len(media_list)}")

            url = media_service.get_download_url(media_item)

            if not url:
                print("Skipping item. Could not create URL:", media_item)
                continue

            save_path = self.download_file(url)

            if save_path:
                downloaded_files.append(save_path)

        print(f"\nDownload all completed. Success count: {len(downloaded_files)}")
        return downloaded_files