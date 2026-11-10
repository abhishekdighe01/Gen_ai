
import requests
import os

def download_file(url, save_path):

    if os.path.exists(save_path):
        print("File already exists:", save_path)
        return

    try:
        print("\nDownloading:", url)

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with open(save_path, "wb") as file:
            file.write(response.content)

        print("Download successful:", save_path)

    except requests.exceptions.Timeout:
        print("Error: Download timed out.")

    except requests.exceptions.RequestException as error:
        print("Download failed:", error)


if __name__ == "__main__":

    documents = [
        {
            "url": "https://www.google.com/robots.txt",
            "path": "data/raw/google_robots.txt"
        },
        {
            "url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
            "path": "data/raw/mnre_guidelines_copy.pdf"
        }
    ]

    for document in documents:
        download_file(document["url"], document["path"])
