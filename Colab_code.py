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

# Maximum number of concurrent torrents
MAX_ACTIVE_TORRENTS = 32

# Torrent management
active_torrents = []
session = lt.session()
session.listen_on(6881, 6891)

# Function to add a torrent to the download list
def add_torrent(file_path):
    info = lt.torrent_info(file_path)
    h = session.add_torrent({'ti': info, 'save_path': temp_download_folder})
    return h

# Main loop to scan and download torrents
while True:
    torrent_files = [f for f in os.listdir(torrent_folder) if f.endswith('.torrent')]
    
    # Add new torrents if below MAX_ACTIVE_TORRENTS
    while len(active_torrents) < MAX_ACTIVE_TORRENTS and torrent_files:
        torrent_file = torrent_files.pop(0)
        torrent_path = os.path.join(torrent_folder, torrent_file)
        handle = add_torrent(torrent_path)
        active_torrents.append((handle, torrent_path))
    
    # Calculate total download and upload speeds
    total_download_speed = 0
    total_upload_speed = 0
    
    # Check status of active torrents
    for handle, torrent_path in active_torrents[:]:
        status = handle.status()
        total_download_speed += status.download_rate
        total_upload_speed += status.upload_rate

        # If the download is complete, silently move files
        if handle.is_seed():
            torrent_name = handle.name()
            source_path = os.path.join(temp_download_folder, torrent_name)
            destination_path = os.path.join(downloads_folder, torrent_name)

            # Move data silently
            try:
                shutil.move(source_path, destination_path)
            except FileNotFoundError:
                pass

            # Move torrent file silently
            torrent_file_name = os.path.basename(torrent_path)
            completed_torrent_path = os.path.join(completed_torrents_folder, torrent_file_name)
            try:
                shutil.move(torrent_path, completed_torrent_path)
            except FileNotFoundError:
                pass

            # Remove the torrent from the active list
            active_torrents.remove((handle, torrent_path))
    
    # Convert speeds to kB/s
    download_speed_kb = total_download_speed / 1000
    upload_speed_kb = total_upload_speed / 1000
    
    # Print the download and upload speeds on a single line
    print(f"\rDownload Speed: {download_speed_kb:.2f} kB/s | Upload Speed: {upload_speed_kb:.2f} kB/s", end="")
    
    # Wait for 1 second before updating the status
    time.sleep(1)
