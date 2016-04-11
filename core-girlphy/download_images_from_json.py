import argparse, sys, os, httplib, re, urlparse, json, io, pprint, threading, Queue, math

parser = argparse.ArgumentParser(description='Image downloader from instagram json files')
parser.add_argument('-d', '--directory', help='the directory where the json files are stored', nargs='?', required=True)

args = parser.parse_args()

if args.directory:

    json_counter = 0
    download_counter = 0
    concurrent = 200
    directory = args.directory

    def update_progress(progress):
        barLength = 40
        status = ""
        if isinstance(progress, int):
            progress = float(progress)
        if not isinstance(progress, float):
            progress = 0
            status = "error: progress var must be float\r\n"
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
            worker_data = q.get()
            parsed_url = urlparse.urlparse(worker_data['remote_url'])
            image_name = parsed_url.path.replace("/", "_")
            data = read_response(parsed_url)
            write_to_image(data, worker_data['local_folder'], image_name)
            q.task_done()

    def write_to_image(data, local_folder, image_name):
        global download_counter
        global json_counter

        # set status
        download_counter+=1
        print "\nDownloading image %s of %s: %s" % (download_counter, json_counter, image_name)
        update_progress(float(math.ceil(float(download_counter)/float(json_counter)*100))/100.0)

        # write to jpg
        f = open(local_folder+"/"+image_name,'w')
        f.write(str(data))
        f.close()

        return True

    def read_response(parsed_url):
        try:
            conn = httplib.HTTPSConnection(parsed_url.netloc)
            conn.request('GET', parsed_url.path)
            res = conn.getresponse()
            data = res.read()
            conn.close()
            if 'OK' in res.reason:
                if len(data) > 0:
                    return data
            else:
                print "Error with reason: " + res.reason + " in url: %s" % parsed_url.path
            return None
        except:
            print "Something went wrong with url: %s" % parsed_url.path

    q = Queue.Queue(concurrent * 2)
    for i in range(concurrent):
        t = threading.Thread(target=create_worker)
        t.daemon = True
        t.start()
    try:
        json_counter=0

        for local_directory, local_sub_directories, local_file in os.walk(directory):
            for json_file in local_file:
                if ".json" in str(json_file):
                    f = open(local_directory+"/"+json_file, "r")
                    filedata = f.read()
                    f.close()
                    # load image urls from json
                    for json_object in json.loads(json.loads(filedata))["entry_data"]["ProfilePage"]:
                        user_media = json_object["user"]["media"]
                        if user_media.get("nodes"):
                            for node in user_media["nodes"]:
                                parsed_url = urlparse.urlparse(node["display_src"])
                                image_name = parsed_url.path.replace("/", "_")
                                if not os.path.isfile(local_directory+'/'+image_name):
                                    data = {
                                        'remote_url': node["display_src"],
                                        'local_folder': local_directory
                                    }
                                    json_counter+=1
                                    q.put(data)
        q.join()

        update_progress(10)
        print("Total json files tried: %s" % json_counter)
        print("Total images downloaded from json: %s" % download_counter)

    except KeyboardInterrupt:
        sys.exit(1)
