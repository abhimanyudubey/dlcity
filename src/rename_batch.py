import glob
import os

fs = glob.glob('/home/dubeya/dlcity/data/ref_images/*.JPG')
for file in fs:
    id = os.path.basename(file).split('_')[2]
    pardir = '/home/dubeya/dlcity/data/ref_images/'
    newname = pardir+id+'.JPG'
    cmd = 'mv %s %s' % (file, newname)
    os.system(cmd)

