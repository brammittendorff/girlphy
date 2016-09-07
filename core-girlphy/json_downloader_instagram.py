import argparse
import sys
import os
import httplib
import urlparse
import json
import threading
import Queue
import math

parser = argparse.ArgumentParser(description='Json downloader for instagram')
parser.add_argument('-l', '--url-list', metavar='file', type=argparse.FileType('r'), help='the list of urls to load', nargs='?', required=True)
parser.add_argument('-d', '--write-to-dir', help='the dir to write the json files to', nargs='?', required=True)

args = parser.parse_args()

if args.url_list and args.write_to_dir:

    url_counter = 0
    download_counter = 0
    concurrent = 200
    directory = args.write_to_dir

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
            worker_url = q.get()
            worker_parsed_url = urlparse.urlparse(worker_url)
            data = read_response(worker_url, worker_parsed_url)
            if data:
                write_to_json(data, worker_parsed_url)
            q.task_done()

    def read_response(workerurl, read_parsed_url):
        try:
            conn = httplib.HTTPSConnection(read_parsed_url.netloc)
            conn.request('GET', read_parsed_url.path)
            res = conn.getresponse()
            data = res.read()
            conn.close()
            if 'OK' in res.reason:
                if len(data) > 0:
                    return data
            else:
                print "Error with reason: " + res.reason + " in url: %s" % workerurl
            return None
        except (httplib.HTTPException) as e:
            print "Something went wrong with url: %s" % e

    def write_to_json(response_data, write_parsed_url):
        global download_counter

        # TODO: find a better way to filter() an array
        name = write_parsed_url.path.split('/')[1]
        # create directory
        if not os.path.isdir(args.write_to_dir+name):
            os.makedirs(args.write_to_dir+name)
        # strip response data
        if response_data:
            strip1 = response_data.split(r'window._sharedData = ')
            if len(strip1) > 1:
                strip2 = strip1[1].split(r";</script>")
                if len(strip2) > 0:
                    with open(args.write_to_dir+name+'/.'+name+'.json', "w") as outfile:
                        # write json to directory
                        download_counter+=1
                        print "\nDownloading instagram profile: %s" % name
                        update_progress(float(math.ceil(float(download_counter)/float(url_counter)*100))/100.0)
                        json.dump(strip2[0], outfile)
                        return True
        return False

    q = Queue.Queue(concurrent * 2)
    for i in range(concurrent):
        t = threading.Thread(target=create_worker)
        t.daemon = True
        t.start()
    try:
        url_counter=0
        for url in args.url_list:
            parsed_url = urlparse.urlparse(url)
            # TODO: find a better way to filter() an array for filenames
            file_name = parsed_url.path.split('/')[1]
            jsonfile = args.write_to_dir+file_name+'/.'+file_name+'.json'
            # should include time check to for the future
            if not os.path.isfile(jsonfile):
                q.put(url.strip())
                url_counter+=1

        q.join()

        update_progress(10)
        print("Total urls tried: %s" % url_counter)
        print("Total downloaded urls: %s" % download_counter)

    except KeyboardInterrupt:
        sys.exit(1)
