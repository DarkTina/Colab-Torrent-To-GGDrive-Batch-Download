# Install library
!pip install libtorrent tqdm

# Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

import libtorrent as lt
import time
import os
from google.colab import drive
import shutil

# Google Drive folders
torrent_folder = "/content/drive/My Drive/Torrents"
downloads_folder = "/content/drive/My Drive/Downloads"
completed_torrents_folder = "/content/drive/My Drive/Completed Torrents"

# Temporary folder in Colab
temp_download_folder = "/content/temp_downloads"
os.makedirs(temp_download_folder, exist_ok=True)

# Create folders if they don't exist
os.makedirs(torrent_folder, exist_ok=True)
os.makedirs(downloads_folder, exist_ok=True)
os.makedirs(completed_torrents_folder, exist_ok=True)

# Max number files
MAX_ACTIVE_FILES = 24
# Max files per torrent
MAX_FILES_PER_TORRENT = 24

# Torrent management
active_torrents = []
session = lt.session()
session.listen_on(6881, 6891)

def count_active_files():
    """Count the total number of files being downloaded."""
    total_files = 0
    for handle, _, torrent_info in active_torrents:
        total_files += torrent_info.num_files()
    return total_files

# Function to add a torrent to the download list
def add_torrent(file_path):
    info = lt.torrent_info(file_path)
    h = session.add_torrent({'ti': info, 'save_path': temp_download_folder})
    return h

# Function to check file progress and move completed files
def move_completed_files(handle, torrent_info):
    file_progress = handle.file_progress()
    for idx, progress in enumerate(file_progress):
        if idx >= MAX_FILES_PER_TORRENT:
            break  # Skip files beyond the limit

        file_path = torrent_info.files().file_path(idx)
        file_size = torrent_info.files().file_size(idx)
        source_path = os.path.join(temp_download_folder, file_path)
        destination_path = os.path.join(downloads_folder, file_path)  # Preserve folder structure

        # Create destination folder if it doesn't exist
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        if progress == file_size:  # File is fully downloaded
            if os.path.exists(source_path):
                try:
                    shutil.move(source_path, destination_path)
                    print(f"File {file_path} has been moved to Google Drive.")
                except Exception as e:
                    print(f"Failed to move file {file_path}: {e}")

# Main loop to scan and download torrents
while True:
    torrent_files = [f for f in os.listdir(torrent_folder) if f.endswith('.torrent')]

    # Add new torrents if below MAX_ACTIVE_FILES
    while torrent_files and count_active_files() < MAX_ACTIVE_FILES:
        torrent_file = torrent_files.pop(0)
        torrent_path = os.path.join(torrent_folder, torrent_file)
        handle = add_torrent(torrent_path)
        torrent_info = lt.torrent_info(torrent_path)

        active_torrents.append((handle, torrent_path, torrent_info))

    # Calculate total download and upload speeds
    total_download_speed = 0
    total_upload_speed = 0

    # Check status of active torrents
    for handle, torrent_path, torrent_info in active_torrents[:]:
        status = handle.status()
        total_download_speed += status.download_rate
        total_upload_speed += status.upload_rate

        # Move completed files within the torrent
        move_completed_files(handle, torrent_info)

        # If the entire torrent is complete, move the .torrent file
        if handle.is_seed():
            torrent_name = handle.name()
            source_path = os.path.join(temp_download_folder, torrent_name)
            destination_path = os.path.join(downloads_folder, torrent_name)

            # Move torrent file silently
            torrent_file_name = os.path.basename(torrent_path)
            completed_torrent_path = os.path.join(completed_torrents_folder, torrent_file_name)
            try:
                shutil.move(torrent_path, completed_torrent_path)
            except FileNotFoundError:
                pass

            # Remove the torrent from the active list
            active_torrents.remove((handle, torrent_path, torrent_info))

    # Convert speeds to kB/s
    download_speed_kb = total_download_speed / 1000
    upload_speed_kb = total_upload_speed / 1000

    # Print the download and upload speeds on a single line
    print(f"\rDownload Speed: {download_speed_kb:.2f} kB/s | Upload Speed: {upload_speed_kb:.2f} kB/s", end="")

    # Wait for 1 second before updating the status
    time.sleep(1)
