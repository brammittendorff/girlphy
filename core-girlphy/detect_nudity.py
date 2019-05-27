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

parser = argparse.ArgumentParser(description='Detect Nudity for downloaded images')
parser.add_argument('-d', '--write-to-dir', help='the dir to copy the image files to', nargs='?', required=True)
parser.add_argument('-g', '--get-from-dir', help='the dir to get the images from', nargs='?', required=True)

args = parser.parse_args()

if args.write_to_dir and args.get_from_dir:

    image_counter = 0
    scanned_counter = 0
    # make it safe
    concurrent = 4
    write_to_directory = args.write_to_dir
    get_from_directory = args.get_from_dir

    def update_progress(progress):
        barLength = 40
        status = ""
        if isinstance(progress, int):
            progress = float(progress)
        if not isinstance(progress, float):
            progress = 0
            status = "Error: progress var must be float\r\n"
        if progress < 0:
            progress = 0
            status = "Halt...\r\n"
        if progress >= 1:
            progress = 1
            status = "Done...\r\n"
        block = int(round(barLength*progress))
        text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
        sys.stdout.write(text)
        sys.stdout.flush()

    def create_worker():
        while True:
            image = q.get()
            detect_nudity(image)
            q.task_done()

    def detect_nudity(image):
        global scanned_counter
        cwd = os.getcwd()

        # create directory
        if not os.path.isdir('core-girlphy/' + args.write_to_dir):
            os.makedirs('core-girlphy/' + args.write_to_dir)

        if image:
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
                        if not os.path.isfile(cwd + '/core-girlphy/' + args.write_to_dir):
                            shutil.copy2(image, cwd + '/core-girlphy/' + args.write_to_dir)

        scanned_counter+=1
        print("\nDetecting nudity in image: %s" % os.path.basename(image))
        update_progress(float(math.ceil(float(scanned_counter)/float(image_counter)*100))/100.0)

    q = Queue(concurrent * 2)
    for i in range(concurrent):
        t = threading.Thread(target=create_worker)
        t.daemon = True
        t.start()
    try:
        image_counter = 0
        cwd = os.getcwd()
        images_list = glob.glob(cwd + '/core-girlphy/' + get_from_directory + '*/*.jpg')
        for image in images_list:
            q.put(image)
            image_counter+=1
        q.join()

        update_progress(10)
        print("Total images tried: %s" % image_counter)
        print("Total downloaded urls: %s" % scanned_counter)

    except KeyboardInterrupt:
        sys.exit(1)
