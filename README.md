# How to use #
### 1. Create 3 Folder on Google Drive "Torrents", "Downloads", "Completed Torrents". ###
The "Torrents" folder: Contains torrent files (The code will scan this folder every 15 seconds).  
The "Downloads" folder: Completed downloads Files are moved here.  
The "Completed Torrents" folder: Torrent files that have finished downloading will be moved here.
### 2. Run code and 
Copy the code from "Colab_Code.py" into "Colab Project".  
### **Or use this link, and create a copy.###
   ```bash
   https://colab.research.google.com/drive/1OeXfmbOaAuDYTg6a_v1Zmh04oqj_8kQd
  ```
### 3. Upload the Torrent files to the "Torrents" folder. ###
### 4. NOTE ###
"folder-type torrent", "multiple files torrents" will be full downloaded to Colab's memory first, and only then moved to Google Drive.
(This ensures the files you need are not corrupted, but it consumes a lot of Colab's memory.)"
You can add Torrents to the "Torrents" folder while the tool is running; the tool scans for torrents every 60 seconds.
The maximum number of files downloaded simultaneously: 32.
