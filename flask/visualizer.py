from flask import Flask, render_template
import random
import os
import cv2
import matplotlib
import tempfile
import glob

keyfile = os.path.join(os.path.realpath(os.path.dirname(__file__)),'../STREETVIEW_KEYS')
keys = []
start_key = 0
with open(keyfile, 'r') as key_file:
    for line in key_file:
        this_key = line.strip()
        keys.append(this_key)
    start_key = random.choice(range(len(keys)))

app = Flask(__name__)


@app.route("/")
def main():
    global start_key, keys
    file_list = glob.glob(os.path.join(os.path.realpath(os.path.dirname(__file__)),'../data/dense_scores_safety_new/*.csv'))
    this_file = random.choice(file_list)
    data_points = []
    with open(this_file, 'r') as inp_file:
        c = 0
        for line in inp_file:
            if c > 0:
                line = line.replace('_', ',')
                lat, lon, inps = line.strip().split(',')
                data_points.append((float(lat), float(lon), inps.replace('"', '')))
            c += 1

    scores = []
    city = os.path.basename(this_file)[:-4]
    paths = []

    for i in range(20):
        req_key = keys[(start_key + i) % len(keys)]
        random_index = random.choice(range(len(data_points)))
        fval = data_points[random_index][2]
        location = str(data_points[random_index][0]) + ',' + str(data_points[random_index][1])
        size = '400x400'
        heading = random.choice([60, 120, 240, 300])
        api_req = '"http://maps.googleapis.com/maps/api/streetview?size=%s&location=%s&sensor=false&heading=%s&key=%s"' % ( size, location, heading, req_key)
        paths.append(api_req)
        scores.append(fval)

    return render_template('index.html',scores=scores, city=city, paths=paths)

if __name__ == "__main__":
    app.run(port=3000)
