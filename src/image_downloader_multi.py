import os
import argparse
from multiprocessing import Pool
import random
import cv2
import numpy as np
import time
import glob


def download_and_check(args):
    global ref_img
    if not os.path.exists(args[-1]):
        try:
            api_req = 'wget -q "http://maps.googleapis.com/maps/api/streetview?size=%s&location=%s,%s&sensor=false&key=%s" -O %s' % tuple(args)
            os.system(api_req)
            img = cv2.imread(args[-1])
            res_err = np.linalg.norm((img-ref_img).flatten(),ord=2)
            return res_err > 0.1
        except:
            return False



keyfile = os.path.join(os.path.realpath(os.path.dirname(__file__)),'../STREETVIEW_KEYS')
keys = []
start_key = 0
with open(keyfile, 'r') as key_file:
    for line in key_file:
        this_key = line.strip()
        keys.append(this_key)
    start_key = random.choice(range(len(keys)))
no_imagery_file = os.path.join(os.path.realpath(os.path.dirname(__file__)),'../data/no_imagery.jpg')
ref_img = cv2.imread(no_imagery_file)

parser = argparse.ArgumentParser('Download Multi-City Images from StreetView (Multithreaded)')
parser.add_argument('-i', '--input', help='Input Directory with CSV files, with points \n format: long,lat per line', required=True, type=str)
parser.add_argument('-o', '--output', help='Output directory to store new CSV files in', required=True, type=str)
parser.add_argument('-c', '--cores', help='Number of multithreaded cores (default 1)', required=False, default=1, type=int)
args = parser.parse_args()

if not os.path.exists(args.output):
    os.makedirs(args.output)

x = []
size = '400x400'

files_list = glob.glob(os.path.join(args.input,'*.csv'))
for csvfile in files_list:
    csvfile_basename = os.path.basename(csvfile)[:-4].split('_')[-1]
    if not os.path.exists(os.path.join(args.output, csvfile_basename)):
        os.makedirs(os.path.join(args.output, csvfile_basename))

    with open(csvfile, 'r') as inpfile:
        for i,line in enumerate(inpfile):
            if i>0:
                line = line.strip().replace('_',',')
                vals = line.split(',')
                lat, lon = vals[1], vals[0]
                apikey = keys[ (i + start_key) % len(keys)]
                outfile = os.path.join(args.output, csvfile_basename, lat+'_'+lon+'.jpg')
                x.append([size, lat, lon, apikey, outfile])

n_max_images = 25495 * len(keys)
n_batches = len(x) / n_max_images + 1
print 'Total number of files %d, requires %d days to complete downloading' % (len(x), n_batches)
incl_data = []

for batch in range(n_batches):
    st_point = batch * n_max_images
    end_point  = min(len(x), st_point + n_max_images)
    this_data = x[st_point:end_point]
    if args.cores > 1:
        pool = Pool(processes=args.cores)
        incl_data_batch = pool.map(download_and_check, this_data)
        incl_data += incl_data_batch
    else:
        for imt in this_data:
            incl_data.append(download_and_check(imt))
    print '%d elements done ...' % end_point
    if n_batches > 1:
        time.sleep(24*24*60)

print 'Completed'





