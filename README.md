# Girlphy
Placeholder images for every time you need girls

## Core
This could be the core of girlphy

### Step 1 download json files from instagram

	python core-girlphy/json_downloader_instagram.py -l urllist.txt -d directory/

or

	time python core-girlphy/json_downloader_instagram.py -l urllist.txt -d directory/

### Step 2 open json files and download the images

	python core-girlphy/download_images_from_json.py -d directory/

or

	time python core-girlphy/download_images_from_json.py -d directory/

## Update images

	rm -rf core-girlphy/directory/*/.*.json
