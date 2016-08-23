import os,sys
import numpy as np
import caffe
import glob

if __name__=="__main__":

    if len(sys.argv) < 3:
        print "Usage python data_preprocess_calculate_mean.py <input-folder> <output-mean-file> <optional-resize-value>"
    else:
        # calculating the mean and writing it to a file
        dir_src = sys.argv[1]
        file_output = sys.argv[2]
        image_size = 256
        if len(sys.argv) > 3:
            image_size = int(sys.argv[3])
        list_image_files = glob.glob(os.path.join(dir_src, "*.JPG"))+glob.glob(os.path.join(dir_src, "*.jpg"))
        for input_image in list_image_files:
            mat_input_image = caffe.io.load_image(input_image, color=True)
