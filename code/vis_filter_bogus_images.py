import os
import numpy as np
import caffe
import glob

def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())

ref_image = np.asarray(caffe.io.load_image("/home/nikhil/data/placepulse2/images_original/TelAviv/32.131051_34.816062.JPG",color=True))
image_pardir = "/home/nikhil/data/placepulse2/images_original/"
csv_pardir = glob.glob("/home/dubeya/extrapolated_votes/safety/scores/*.csv")
op_pardir = "/home/dubeya/extrapolated_votes/safety/scores_new"

if not os.path.exists(op_pardir):
    os.makedirs(op_pardir)

for csvfile in csv_pardir:
    with open(csvfile,'r') as csv_src_file:
        print "Reading csv",csvfile,"right now",os.path.basename(csvfile)
        op_file = os.path.join(op_pardir,os.path.basename(csvfile))
        with open(op_file,'w') as f:
            for line in csv_src_file:
                img_loc = line.strip().split(',')[0]
                score = line.strip().split(',')[1]

                img_file = os.path.join("/home/nikhil/data/placepulse2/images_original/",os.path.basename(csvfile).replace(".csv",""),img_loc)
                target_image = np.asarray(caffe.io.load_image(img_file))

                images_diff = rmse(target_image,ref_image)

                if images_diff > 1e-2:
                    f.write(img_loc+" "+score+"\n")

                else:
                    print "Bogus image found at",img_loc


print "Done"