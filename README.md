# Girlphy

Placeholder images for every time you need girls

## Core

This could be the 'downloading' core of girlphy

### Step 1 clear the old json files

```
rm -rf core-girlphy/directory/*/.*.json
```

### Step 2 download json files from instagram

```
python core-girlphy/json_downloader_instagram.py -l core-girlphy/urllist.txt -d core-girlphy/directory/
```

### Step 3 open json files and download the images

```
python core-girlphy/download_images_from_json.py -d core-girlphy/directory/
```

### Step 4 Download trained model from github

Download file:

```
curl https://raw.githubusercontent.com/minto5050/NSFW-detection/master/retrained_graph.pb --output core-girlphy/models/retrained_graph.pb
```

### Step 5 run detecting nudity

```
python3 core-girlphy/detect_nudity.py -d output/ -g directory/
```
