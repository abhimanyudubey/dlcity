import numpy as np
import os
import glob
import cv2
import random
''' Vote generation server routine, checks the directory with images and creates lists of votes routinely.'''

image_dir = '/home/dubeya/dlcity/data/images'
ref_image_dir = '/home/dubeya/dlcity/data/images_ref'
model_dir = '/home/dubeya/dlcity/models/'
votes_dir = '/home/dubeya/dlcity/votes/'
scratch_dir = '/home/dubeya/dlcity/scratch/'
tmp_dir = '/tmp/'
caffe_ = '/home/dubeya/caffe/build/tools/caffe'

attributes = ['safe', 'beautiful', 'boring', 'depressing', 'lively', 'wealthy']

wrong_image_path = '/home/dubeya/data/no_imagery.jpg'
wrong_image = cv2.imread(wrong_image_path)

ts_mean = 25
ts_sigma = 0.333

def is_valid_image(image_path):
    global wrong_image
    try:
        image = cv2.imread(image_path)
        dist = np.linalg.norm(image - wrong_image, ord=2)
        return dist > 0.001
    except:
        return False

def read_index(filename):
    out_dict = {}
    with open(filename, 'r') as inp_file:
        for line in inp_file:
            fmt_line = line.strip().split()
            fn, nvotes, mu, sigma = fmt_line[0], int(fmt_line[1]), float(fmt_line[2]), float(fmt_line[3])
            out_dict[fn] = (nvotes, mu, sigma)
    return out_dict

def update_index(filename, update):
    with open(filename, 'a') as upd_file:
        for elem in update:
            write_str = ' '.join([str(x) for x in elem])
            upd_file.write(write_str+'\n')

def write_index(filename, index):
    with open(filename, 'w') as out_file:
        for key,value in index.iteritems():
            write_str = ' '.join([str(key), str(value[0]), str(value[1]), str(value[2])])
            out_file.write(write_str+'\n')

def update_file_index():
    # create index directory if not done already
    global image_dir, ref_image_dir, model_dir, votes_dir, scratch_dir, ts_mean, ts_sigma, attributes

    if not os.path.exists(os.path.join(scratch_dir,'indexes')):
        os.makedirs(os.path.join(scratch_dir,'indexes'))

    cities = [x for x in glob.glob(os.path.join(image_dir,'*')) if os.path.isdir(x)]
    index = {}
    for attribute in attributes:
        attribute_index = {}
        if not os.path.exists(os.path.join(scratch_dir, 'indexes', attribute)):
            os.makedirs(os.path.join(scratch_dir, 'indexes', attribute))

        for city in cities:
            city_index_path = os.path.join(scratch_dir,'indexes',attribute, city+'.index')
            city_index = read_index(city_index_path)
            city_files = glob.glob(os.path.join(image_dir, city, '*.jpg')) + glob.glob(os.path.join(image_dir, city, '*.JPG'))
            for city_file in city_files:
                if city_file not in city_index:
                    if is_valid_image(city_file):
                        city_index[city_file] = (0, ts_mean, ts_sigma)
            attribute_index[city] = city_index
        index[attribute] = attribute_index

    print 'Indexes read successfully'
    return index

def write_file_index(index):
    global image_dir, ref_image_dir, model_dir, votes_dir, scratch_dir, ts_mean, ts_sigma, attributes

    if not os.path.exists(os.path.join(scratch_dir,'indexes')):
        os.makedirs(os.path.join(scratch_dir,'indexes'))

    cities = [x for x in glob.glob(os.path.join(image_dir,'*')) if os.path.isdir(x)]
    for attribute in attributes:
        if not os.path.exists(os.path.join(scratch_dir, 'indexes', attribute)):
            os.makedirs(os.path.join(scratch_dir, 'indexes', attribute))
        for city in cities:
            city_index_path = os.path.join(scratch_dir,'indexes',attribute, city+'.index')
            city_index = index[attribute][city]
            write_index(city_index_path, city_index)

    print 'Indexes written successfully'

def read_reference_indexes():
    global image_dir, ref_image_dir, model_dir, votes_dir, scratch_dir, ts_mean, ts_sigma, attributes

    ref_index = {}
    for attribute in attributes:
        ref_attribute_index_path = os.path.join(scratch_dir, 'ref_indexes', attribute+'.index')
        ref_attribute_index = read_index(ref_attribute_index_path)

        ref_index[attribute] = ref_attribute_index

    return ref_index


def get_image_lists(num, attribute, city, limit, index, ref_index):
    global tmp_dir

    img_list = []
    this_index = index[attribute][city]
    this_ref_index = ref_index[attribute]

    d = 0
    for k,v in this_index.iteritems():
        if d < num:
            if v[0] < limit:
                for j in range(limit-v[0]):
                    comp_choice = random.choice(this_ref_index.keys())
                    img_list.append([k, comp_choice])
                    d+=1
        else:
            continue

    tmp_prefix = [random.choice(['ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890']) for x in range(20)]
    tmp_path_l = os.path.join(tmp_dir, tmp_prefix+'_1.txt')
    tmp_path_r = os.path.join(tmp_dir, tmp_prefix+'_2.txt')

    with (open(tmp_path_l,'w'), open(tmp_path_r, 'w')) as (l_file, r_file):
        for elem in img_list:
            l_file.write(elem[0]+' 0\n')
            r_file.write(elem[1]+' 1\n')

    return (tmp_path_l, tmp_path_r)
