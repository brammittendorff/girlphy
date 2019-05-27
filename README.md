# Girlphy

Placeholder images for every time you need girls

## Core download images from instagram

Run the following steps to get the images

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

## Classify nudity in downloaded images

### Requirements

- tensorflow
- future

Download file:

```
curl https://raw.githubusercontent.com/minto5050/NSFW-detection/master/retrained_graph.pb --output core-girlphy/models/retrained_graph.pb
```

### Run

```
python3 core-girlphy/detect_nudity.py -d output/ -g directory/
```

## Classify age & gender in downloaded images

### Requirements

Download files:
```
curl https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/opencv_face_detector.pbtxt --output core-girlphy/models/opencv_face_detector.pbtxt
curl https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/opencv_face_detector_uint8.pb --output core-girlphy/models/opencv_face_detector_uint8.pb
curl https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/age_deploy.prototxt --output core-girlphy/models/age_deploy.prototxt
curl https://raw.githubusercontent.com/spmallick/learnopencv/master/AgeGender/gender_deploy.prototxt --output core-girlphy/models/gender_deploy.prototxt
```

Download files from dropbox to folder `core-girlphy/models/`:

Gender Net : https://www.dropbox.com/s/iyv483wz7ztr9gh/gender_net.caffemodel?dl=0"
Age Net : https://www.dropbox.com/s/xfb20y596869vbb/age_net.caffemodel?dl=0"

### Run

```
python3 core-girlphy/scan_gender_age.py -d output/ -g directory/
```
