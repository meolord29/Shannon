
import os
import configparser
import pandas as pd
from rich.console import Console
from rich.table import Table
import httpx

def get_paper_urls(directory_key: str):
    """
    Scans a directory specified by a key in config.ini, extracts paper URLs from Paper.md files,
    and returns a list of papers.

    Args:
        directory_key (str): The key in the [directories] section of config.ini (e.g., 'papers').
    """
    config = configparser.ConfigParser()
    config.read('Meta/config.ini')
    
    if directory_key not in config['directories']:
        print(f"Error: Directory key '{directory_key}' not found in config.ini")
        return []

    main_dir = config['directories'][directory_key]
    papers_list = []

    if not os.path.isdir(main_dir):
        return papers_list

    for dirpath, dirnames, filenames in os.walk(main_dir):
        if "Paper.md" in filenames:
            subfolder_name = os.path.basename(dirpath)
            paper_md_path = os.path.join(dirpath, "Paper.md")
            
            link = "NO LINK FOUND"
            try:
                with open(paper_md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # A more robust regex to find the link
                    import re
                    match = re.search(r"^\s*link\s*:\s*(https?://[^\s]+)\s*$", content, re.MULTILINE | re.IGNORECASE)
                    if match:
                        link = match.group(1)
            except Exception as e:
                link = f"ERROR READING FILE: {e}"

            # Check if the paper has been downloaded
            download_folder = "Meta/Downloads/paper"
            if not os.path.exists(download_folder):
                os.makedirs(download_folder)

            downloaded_status = "No"
            if os.path.exists(os.path.join(download_folder, subfolder_name + ".pdf")):
                downloaded_status = "Yes"

            papers_list.append({"folder": subfolder_name, "url": link, "downloaded": downloaded_status})
            
    return papers_list


def download_paper(url: str, folder_name: str):
    """
    Downloads a paper from a given URL.

    Args:
        url (str): The URL of the paper to download.
        folder_name (str): The name of the folder to save the file in.
    """
    if url == "NO LINK FOUND":
        print("Cannot download a file without a valid link.")
        return

    try:
        with httpx.stream("GET", url, follow_redirects=True) as response:
            response.raise_for_status()  # Raise an exception for bad status codes

            download_folder = "Meta/Downloads/paper"
            if not os.path.exists(download_folder):
                os.makedirs(download_folder)

            file_name = folder_name + ".pdf"
            download_path = os.path.join(download_folder, file_name)

            with open(download_path, "wb") as f:
                for chunk in response.iter_bytes():
                    f.write(chunk)
            
            print(f"Successfully downloaded {file_name} to {download_folder}")

    except httpx.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")
