
import requests
import os


def download_file(url, save_path):
    """Download a file from url and save it to save_path.

    Skips the download if the file already exists.
    Handles timeouts and request errors gracefully.
    """
    if os.path.exists(save_path):
        print("File already exists:", save_path)
        return

    try:
        print("\nDownloading:", url)

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with open(save_path, "wb") as file:
            file.write(response.content)

        print("Download successful:", save_path)

    except requests.exceptions.Timeout:
        print("Error: Download timed out for:", url)

    except requests.exceptions.RequestException as error:
        print("Download failed:", error)


if __name__ == "__main__":

    documents = [
        {
            "url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/07/202407021768035484.pdf",
            "path": "data/raw/mnre_guidelines.pdf"
        },
        {
            "url": "https://pmsg-production-public.s3.ap-south-1.amazonaws.com/notifications/Operational_Guidelines_for_Implementation_of_Component_Incentives_to_Discoms.pdf",
            "path": "data/raw/discom_incentives_guidelines.pdf"
        },
        {
            "url": "https://cdnbbsr.s3waas.gov.in/s3716e1b8c6cd17b771da77391355749f3/uploads/2024/12/20241230101814137.pdf",
            "path": "data/raw/resco_guidelines.pdf"
        },
        {
            "url": "https://mnre.gov.in/en/notice/operational-guidelines-for-implementation-of-the-component-central-financial-assistance-to-residential-consumers-of-pm-surya-ghar-muft-bijli-yojana/",
            "path": "data/raw/mnre_notice.html"
        },
    ]

    for document in documents:
        download_file(document["url"], document["path"])
