import argparse
import sys
import os
import http.client
import json
import threading
import math
import glob
import tensorflow as tf
import shutil
import concurrent.futures
from PIL import Image

parser = argparse.ArgumentParser(description='Detect Nudity for downloaded images')
parser.add_argument('-d', '--write-to-dir', help='the dir to copy the image files to', nargs='?', required=True)
parser.add_argument('-g', '--get-from-dir', help='the dir to get the images from', nargs='?', required=True)

args = parser.parse_args()

if args.write_to_dir and args.get_from_dir:

    global label_lines
    cwd = os.getcwd()
    write_to_directory = args.write_to_dir
    get_from_directory = args.get_from_dir

    images_list = glob.glob(get_from_directory + '*/*.jpg')
    label_lines = [line.rstrip() for line
                    in tf.gfile.GFile(cwd + '/core-girlphy/models/retrained_labels.txt')]
    with tf.gfile.FastGFile(cwd + '/core-girlphy/models/retrained_graph.pb', 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')

    def is_grey_scale(img_path):
        img = Image.open(img_path).convert('RGB')
        w,h = img.size
        for i in range(w):
            for j in range(h):
                r,g,b = img.getpixel((i,j))
                if r != g != b: return False
        return True

    def detect_nudity(image):
        # create directory
        if not os.path.isdir(args.write_to_dir):
            os.makedirs(args.write_to_dir)

        store_processed = args.write_to_dir + ".classified.images.txt"
        if not os.path.isfile(store_processed):
            open(store_processed, 'a').close()

        processed_file = open(store_processed, 'r+')
        processed = processed_file.read().split('\n')
        processed_file.close()

        # you can not detect nudity with an grayscale image
        if (image and
            not os.path.isfile(args.write_to_dir + os.path.basename(image)) and
            not is_grey_scale(image) and image not in processed):
            image_data = tf.gfile.FastGFile(image, 'rb').read()
            with tf.Session() as sess:
                softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
                predictions = sess.run(softmax_tensor, \
                        {'DecodeJpeg/contents:0': image_data})
                top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
                # store already scanned images
                file_open = open(store_processed, 'a+')
                file_open.write(image + "\n")
                file_open.close()
                for node_id in top_k:
                    human_string = label_lines[node_id]
                    score = predictions[0][node_id]
                    print(score)
                    if score > 0.94:
                        shutil.copy2(image, args.write_to_dir)
                        print("\nDetecting nudity in image: %s" % os.path.basename(image))

    # for each is heavy enough
    for image in images_list:
        detect_nudity(image)
