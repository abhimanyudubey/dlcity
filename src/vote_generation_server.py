import numpy as np
import os
import glob
import cv2
import random
import GPUtil
import trueskill
from multiprocessing import Pool

''' Vote generation server routine, checks the directory with images and creates lists of votes routinely.'''

image_dir = '/data/pp2/images'
ref_image_dir = '/home/dubeya/dlcity/data/images_ref'
model_dir = '/home/dubeya/dlcity/models/'
votes_dir = '/home/dubeya/dlcity/votes/'
scratch_dir = '/home/dubeya/dlcity/scratch/'
tmp_dir = '/tmp/'
caffe_ = '/home/dubeya/caffe/build/tools/caffe'

attributes = ['safety', 'beautiful', 'wealthy', 'lively', 'boring', 'depressing']

wrong_image_path = '/home/dubeya/data/no_imagery.jpg'
wrong_image = cv2.imread(wrong_image_path)

ts_mean = 25.0
ts_sigma = (ts_mean/3.0)**2
ts_beta2 = ts_sigma/4.0
ts_tau2 = ts_sigma*100
ts_prob_draw = 0.1

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
    if os.path.exists(filename):
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

def reference_index_exists():
    global image_dir, ref_image_dir, model_dir, votes_dir, scratch_dir, ts_mean, ts_sigma, attributes
    exists = True
    for elem in attributes:
        exists = exists and os.path.exists(os.path.join(scratch_dir, 'ref_indexes'), elem+'.index')

    return exists


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

    return tmp_path_l, tmp_path_r, img_list

def run_vote_generator(image_list_pair, num, attribute, gpuID):
    global tmp_dir, image_dir, ref_image_dir, model_dir, votes_dir, scratch_dir, ts_mean, ts_sigma, attributes, caffe_

    main_model_prototxt = ''
    with open(os.path.join(model_dir, 'main.prototxt'),'r') as f_main:
        main_model_prototxt = '\n'.join(f_main.readlines())

    data_prototxt = 'name: "rsscnn-vgg" \n layer {\n name: "data1" \n type: "ImageData" \n top: "data1" \n top: "label1" \n image_data_param { \n source: "%s"\n batch_size: 30 \n new_height: 256 \n new_width: 256\n }\n transform_param {\n crop_size: 224\n mean_file: "/home/dubeya/dlcity/models/imagenet_mean.binaryproto"\n mirror: true\n}\ninclude: { phase: TEST }\n}\n layer {\n name: "data2"\n type: "ImageData"\n top: "data2"\n top: "label2"\n image_data_param {\n source: "%s"\n batch_size: 30\n new_height: 256\n new_width: 256\n }\n transform_param {\n crop_size: 224\n mean_file: "/home/dubeya/dlcity/models/imagenet_mean.binaryproto"\n mirror: false\n}\n include: { phase: TEST }\n }' % (image_list_pair[0], image_list_pair[1])

    output_file = os.path.join(tmp_dir,''.join([random.choice(['ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890']) for x in range(20)])+'_output.txt')
    output_prototxt = 'layer {\n name: "CSVDataWriter"\n type: "Python"\n bottom: "fusion_pred"\n python_param{\n module: "data"\n layer:"CSVDataWriterLayer\n param_str: "%s"\n}\n}\n' % ( r'{\"output\": \"%s\"' % output_file)

    final_prototxt = '\n'.join([data_prototxt, main_model_prototxt, output_prototxt])

    temp_prototxt_file = os.path.join(tmp_dir,''.join([random.choice(['ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890']) for x in range(20)])+'_prototxt.prototxt')
    with open(temp_prototxt_file, 'w') as f_proto:
        f_proto.write(final_prototxt)

    # run caffe now
    caffe_cmd = '%s test --model %s --weights %s --iterations %d --gpu %d' % (caffe_, temp_prototxt_file, os.path.join(model_dir, attribute+'.caffemodel'), int(num/30)+1, gpuID)
    os.system(caffe_cmd)

    #aggregate votes
    iter=0
    updates = []
    with open(output_file,'r') as f_output:
        for line in f_output:
            if iter < num:
                confs = [float(x) for x in line.strip().split(',')]
                if confs[0] > confs[1]:
                    updates.append([image_list_pair[0][iter], image_list_pair[1][iter], 0])
                else:
                    updates.append([image_list_pair[0][iter], image_list_pair[1][iter], 1])

    return updates

def generate_votes(args):
    image_list_pair = (args[0], args[1])
    num = args[3]
    attribute = args[4]
    gpuid = args[5]
    updates = run_vote_generator(image_list_pair, num, attribute, gpuid)
    return updates

def update_current_index(index, ref_index, city, attribute, updates, ts):
    global tmp_dir, image_dir, ref_image_dir, model_dir, votes_dir, scratch_dir, ts_mean, ts_sigma, attributes, caffe_
    for update in updates:
        left_image = update[0]
        right_image = update[1]
        # only left image will be from dataset, and hence only it has to be updated
        # scores for all right images will be constant

        if left_image not in index[attribute]:
            index[attribute][left_image] = (0, ts_mean, ts_sigma)

        left_votes, left_mean, left_sigma = index[attribute][city][left_image]
        right_votes, right_mean, right_sigma = ref_index[attribute][right_image]

        if update[2] == 0:
            left_mean_new, left_sigma_new, right_mean_new, right_sigma_new = ts.update_rating((left_mean, left_sigma), (right_mean, right_sigma), False)
            index[attribute][city][left_image] = (left_votes+1, left_mean_new, left_sigma_new)
        else:
            right_mean_new, right_sigma_new, left_mean_new, left_sigma_new = ts.update_rating((right_mean, right_sigma), (left_mean, left_sigma), False)
            index[attribute][left_image] = (left_votes+1, left_mean_new, left_sigma_new)

    return index

if __name__ == "__main__":
    # initialize truskill object
    ts = trueskill.TrueSkill(ts_beta2, ts_tau2, ts_prob_draw, ts_sigma)

    ref_index = {}
    if reference_index_exists():
        ref_index = read_reference_indexes()
    else:
        # create reference indexes
        study_ids = {'50a68a51fdc9f05596000002': 'safety', '50f62c41a84ea7c5fdd2e454': 'lively', '50f62c68a84ea7c5fdd2e456' : 'boring', '50f62cb7a84ea7c5fdd2e458': 'wealthy', '50f62ccfa84ea7c5fdd2e459': 'depressing', '5217c351ad93a7d3e7b07a64': 'beautiful'}
        image_ids = {}
        with open('/home/dubeya/dlcity/data/ref/locations.tsv','r') as img_file:
            sk = False
            for line in img_file:
                if sk:
                    vals = line.strip().split('\t')
                    id = vals[0]
                    fn = '/home/dubeya/dlcity/data/ref_images/'+id+'.JPG'
                    image_ids[id] = fn
                else:
                    sk = True
        # read images now initializing index
        for attribute in attributes:
            ref_index[attribute] = {}

        for image_ in image_ids.values():
            for attribute in attributes:
                ref_index[attribute][image_] = (0, ts_mean, ts_sigma)

        with open('/home/dubeya/dlcity/data/ref/votes.tsv','r') as vote_file:
            sk = False
            for line in vote_file:
                if sk:
                    vals = line.strip.split('\t')
                    left_image = image_ids[vals[2]]
                    right_image = image_ids[vals[3]]
                    attribute = study_ids[vals[4]]

                    left_votes, left_mean, left_sigma = ref_index[attribute][left_image]
                    right_votes, right_mean, right_sigma = ref_index[attribute][right_image]

                    if vals[1] == 'left':
                        left_mean_new, left_sigma_new, right_mean_new, right_sigma_new = ts.update_rating(
                            (left_mean, left_sigma), (right_mean, right_sigma), False)
                        ref_index[attribute][left_image] = (left_votes + 1, left_mean_new, left_sigma_new)
                        ref_index[attribute][right_image] = (right_votes + 1, right_mean_new, right_sigma_new)
                    else:
                        right_mean_new, right_sigma_new, left_mean_new, left_sigma_new = ts.update_rating(
                            (right_mean, right_sigma), (left_mean, left_sigma), False)
                        ref_index[attribute][left_image] = (left_votes + 1, left_mean_new, left_sigma_new)
                        ref_index[attribute][right_image] = (right_votes + 1, right_mean_new, right_sigma_new)
                else:
                    sk = True
    for attribute in attributes:
        write_index('/home/dubeya/dlcity/data/scratch/ref_indexes/'+attribute+'.index', ref_index[attribute])

    print 'ref_index read successfully'

    while(True):
        # first read existing index
        index = update_file_index()
        print 'File indexes updated successfully'
        pool = Pool(processes=4)
        num_votes = 100000
        limit = 30

        target_attr = 'safety'

        jobs = []
        cities = [x for x in glob.glob(os.path.join(image_dir, '*')) if os.path.isdir(x)]
        target_city = []
        for i in range(4):
            city = random.choice(cities)
            target_city.append(city)
            im_lists = get_image_lists(num_votes, target_attr, city, limit, index, ref_index)
            jobs.append(im_lists[0],im_lists[1], im_lists[2], num_votes, target_attr, i)

        results = pool.map(generate_votes, jobs)

        for update in results:
            update_current_index(index, ref_index, target_city[i], target_attr, update, ts)

        write_file_index(index)


















