# Girlphy

Placeholder images for every time you need girls

## Core

This could be the 'downloading' core of girlphy

### Step 1 clear the old json files

	rm -rf core-girlphy/directory/*/.*.json

### Step 2 download json files from instagram

	python core-girlphy/json_downloader_instagram.py -l core-girlphy/urllist.txt -d core-girlphy/directory/

### Step 3 open json files and download the images

	python core-girlphy/download_images_from_json.py -d core-girlphy/directory/
