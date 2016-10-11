import os,sys
import caffe
import numpy as np
import glob

if __name__=="__main__":
    if len(sys.argv)<3:
        print "usage python data_preprocess_remove_bogus_images.py <reference-image-file> <removal-folder>"
    else:
        ref_image_file = sys.argv[1]
        ref_image_folder = sys.argv[2]

        ref_image = np.array(caffe.io.load_image(ref_image_file))

