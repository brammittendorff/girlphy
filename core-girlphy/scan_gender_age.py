import argparse
import sys
import os
import threading
import math
import glob
import shutil
import concurrent.futures
import cv2 as cv
import math
import time
import argparse

parser = argparse.ArgumentParser(description='Scan gender and age for downloaded images')
parser.add_argument('-d', '--write-to-dir', help='the dir to copy the image files to', nargs='?', required=True)
parser.add_argument('-g', '--get-from-dir', help='the dir to get the images from', nargs='?', required=True)

args = parser.parse_args()

if args.write_to_dir and args.get_from_dir:

    image_counter = 0
    scanned_counter = 0
    # make it safe
    write_to_directory = args.write_to_dir
    get_from_directory = args.get_from_dir

    cwd = os.getcwd()

    faceProto = cwd + '/core-girlphy/' + "models/opencv_face_detector.pbtxt"
    faceModel = cwd + '/core-girlphy/' + "models/opencv_face_detector_uint8.pb"

    ageProto = cwd + '/core-girlphy/' + "models/age_deploy.prototxt"
    ageModel = cwd + '/core-girlphy/' + "models/age_net.caffemodel"

    genderProto = cwd + '/core-girlphy/' + "models/gender_deploy.prototxt"
    genderModel = cwd + '/core-girlphy/' + "models/gender_net.caffemodel"

    # Load network
    ageNet = cv.dnn.readNet(ageModel, ageProto)
    genderNet = cv.dnn.readNet(genderModel, genderProto)
    faceNet = cv.dnn.readNet(faceModel, faceProto)

    images_list = glob.glob(get_from_directory + '*/*.jpg')

    def getFaceBox(net, frame, conf_threshold=0.7):
        frameOpencvDnn = frame.copy()
        frameHeight = frameOpencvDnn.shape[0]
        frameWidth = frameOpencvDnn.shape[1]
        blob = cv.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)

        net.setInput(blob)
        detections = net.forward()
        bboxes = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > conf_threshold:
                x1 = int(detections[0, 0, i, 3] * frameWidth)
                y1 = int(detections[0, 0, i, 4] * frameHeight)
                x2 = int(detections[0, 0, i, 5] * frameWidth)
                y2 = int(detections[0, 0, i, 6] * frameHeight)
                bboxes.append([x1, y1, x2, y2])
                cv.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight/150)), 8)
        return frameOpencvDnn, bboxes

    def scan_gender_age(image):
        global scanned_counter
        cwd = os.getcwd()
        MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
        ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']
        genderList = ['Male', 'Female']
        padding = 20

        # create directory
        if not os.path.isdir(args.write_to_dir):
            os.makedirs(args.write_to_dir)

        frame = cv.imread(image, 1)

        frameFace, bboxes = getFaceBox(faceNet, frame)
        if not bboxes:
            print("No face Detected, Checking next frame")

        for bbox in bboxes:
            face = frame[max(0,bbox[1]-padding):min(bbox[3]+padding,frame.shape[0]-1),max(0,bbox[0]-padding):min(bbox[2]+padding, frame.shape[1]-1)]

            blob = cv.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
            genderNet.setInput(blob)
            genderPreds = genderNet.forward()
            gender = genderList[genderPreds[0].argmax()]
            # print("Gender Output : {}".format(genderPreds))
            print("Gender : {}, conf = {:.3f}".format(gender, genderPreds[0].max()))

            ageNet.setInput(blob)
            agePreds = ageNet.forward()
            age = ageList[agePreds[0].argmax()]
            print("Age Output : {}".format(agePreds))
            print("Age : {}, conf = {:.3f}".format(age, agePreds[0].max()))
            if gender == 'Female':
                shutil.copy2(image, args.write_to_dir)
                print("\nDetecting Female in image: %s" % os.path.basename(image))

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(scan_gender_age, url): url for url in images_list}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            except KeyboardInterrupt:
                sys.exit(1)
