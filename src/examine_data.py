import argparse
import random
import os
import cv2
import matplotlib
import tempfile

keyfile = os.path.join(os.path.realpath(os.path.dirname(__file__)),'../../STREETVIEW_KEYS')
keys = []
start_key = 0
with open(keyfile, 'r') as key_file:
    for line in key_file:
        this_key = line.strip()
        keys.append(this_key)
    start_key = random.choice(range(len(keys)))
# we use one of the keys at random

parser = argparse.ArgumentParser('Examine StreetView Data from CSV randomly with Score')
parser.add_argument('-i', '--input', help='Path to input CSV file, should be in format LAT, LONG, VALUE (IF STRING, PUT IN QUOTES)', required=True, type=str)
parser.add_argument('-n', '--n_samples', help='Number of samples to view (default 1)', required=False, default=1, type=int)
parser.add_argument('-o', '--output', help='Output folder to save download images to (optional, default off)', required=False, default='')
parser.add_argument('-s', '--skip_view', help='Flag to skip viewing and just download images (optional, default off)', required=False, default=False)

args = parser.parse_args()

if args.skip_view:
    matplotlib.use('Agg')
import matplotlib.pyplot as plt

data_points = []
with open(args.input,'r') as inp_file:
    c = 0
    for line in inp_file:
        if c > 0:
            line = line.replace('_',',')
            lat, lon, inps = line.strip().split(',')
            data_points.append((float(lat), float(lon), inps.replace('"','')))
        c += 1

# read data file, now choosing and displaying files randomly
out_dir = tempfile.gettempdir()
if args.output:
    out_dir = args.output
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
# setting output directory as tmp if not set

for i in range(args.n_samples):
    req_key = keys[(start_key + i ) % len(keys)]
    random_index = random.choice(range(len(data_points)))
    fval = data_points[random_index][2]
    location = str(data_points[random_index][0])+','+str(data_points[random_index][1])
    size = '400x400'
    heading = random.choice([60,120,240,300])
    api_req = '"http://maps.googleapis.com/maps/api/streetview?size=%s&location=%s&sensor=false&heading=%s&key=%s"' % (size, location, heading, req_key)
    print 'Server request: %s' % api_req
    output_file = os.path.join(out_dir, '_'.join([location.replace(',','_'), str(heading), size, fval])+'.jpg')
    cmd = 'wget -q '+ api_req +' -O ' + output_file
    os.system(cmd)
    try:
        img_bgr = cv2.imread(output_file)
        img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        plt.imshow(img)
        title_text = '%s' % fval
        plt.suptitle(title_text)
        plt.axis('off')
        if not args.skip_view:
            plt.show()
        plt.savefig(output_file[:-4]+'.figure.png', bbox_inches='tight')
    except:
        print 'Error in loading image'


