import argparse
import sys
import os
import http.client
from urllib.parse import urlparse, urlencode
import json
import threading
from queue import Queue, deque
import math
import glob
import tensorflow as tf
import shutil
import concurrent.futures

parser = argparse.ArgumentParser(description='Detect Nudity for downloaded images')
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
    images_list = glob.glob(cwd + '/core-girlphy/' + get_from_directory + '*/*.jpg')


    def detect_nudity(image):
        cwd = os.getcwd()

        # create directory
        if not os.path.isdir('core-girlphy/' + args.write_to_dir):
            os.makedirs('core-girlphy/' + args.write_to_dir)

        if image and not os.path.isfile(cwd + '/core-girlphy/' + args.write_to_dir):
            image_data = tf.gfile.FastGFile(image, 'rb').read()
            label_lines = [line.rstrip() for line
                            in tf.gfile.GFile(cwd + '/core-girlphy/models/retrained_labels.txt')]
            with tf.gfile.FastGFile(cwd + '/core-girlphy/models/retrained_graph.pb', 'rb') as f:
                graph_def = tf.GraphDef()
                graph_def.ParseFromString(f.read())
                tf.import_graph_def(graph_def, name='')
            with tf.Session() as sess:
                softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
                predictions = sess.run(softmax_tensor, \
                        {'DecodeJpeg/contents:0': image_data})
                top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
                for node_id in top_k:
                    human_string = label_lines[node_id]
                    score = predictions[0][node_id]
                    if score > 0.90:
                        shutil.copy2(image, cwd + '/core-girlphy/' + args.write_to_dir)
                        print("\nDetecting nudity in image: %s" % os.path.basename(image))

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_url = {executor.submit(detect_nudity, url): url for url in images_list}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            except KeyboardInterrupt:
                sys.exit(1)
            else:
                print('%r page is %d bytes' % (url, len(data)))
