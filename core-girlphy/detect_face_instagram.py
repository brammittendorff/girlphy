#detecting face
import httplib, sys, urlparse, json, os
import cv2
from threading import Thread
from Queue import Queue

concurrent = 200
directory = "/girls/instagram/brookeswalloww"

# https://github.com/Itseez/opencv/blob/master/samples/python2/peopledetect.py
# https://github.com/Itseez/opencv/blob/master/samples/python2/facedetect.py
# http://fideloper.com/facial-detection

def detect(path):
    img = cv2.imread(path)
    cascade = cv2.CascadeClassifier("xml/haarcascade_eye.xml")
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)

    if len(rects) == 0:
        return False
    return True

def createworker():
    while True:
        url = q.get()
        data, status, path = readresponse(url)
        writetoimage(data, status, path)
        q.task_done()

def readresponse(workerurl):
    try:
        checkurl = urlparse.urlparse(workerurl)
        conn = httplib.HTTPSConnection(checkurl.netloc)
        conn.request("GET", checkurl.path)
        res = conn.getresponse()
        data = res.read()
        imagename = checkurl.path.replace("/", "_")
        return data, workerurl, imagename
    except:
        return "error", workerurl

def writetoimage(data, workerurl, imagename):
    # write to jpg
    f = open(os.getcwd()+directory+"/"+imagename,'w')
    f.write(data)
    f.close()
    detected = detect(os.getcwd()+directory+"/"+imagename)
    if detected:
        print workerurl

q = Queue(concurrent * 2)
for i in range(concurrent):
    t = Thread(target=createworker)
    t.daemon = True
    t.start()
try:
    f = open(os.getcwd()+directory+"/."+directory.split("/")[-1]+".json", "r")
    filedata = f.read()
    f.close()

    for jsonobject in json.loads(json.loads(filedata))["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"]:
        q.put(jsonobject["display_src"])
    q.join()
except KeyboardInterrupt:
    sys.exit(1)
