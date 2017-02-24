import numpy as np
import sys
import glob
import os
import random
from multiprocessing import Pool

def process_images(args)
    mesh_city_name = args[0]
    score_file_name = args[1]
    fno = args[2]

    images = []

    with open(score_file_name, 'r') as f:
        for line in f:
            l2 = line.strip().split(',')
            sco = float(l2[1])
            lat = float(l2[0].split('_')[0])
            lon = float(l2[0].split('_')[1])
            images.append([lat, lon, sco])

    points = [x[:2] for x in images]

    mesh_points = []

    with open(mesh_file, 'r') as f:
        for line in f:
            l = line.strip().split(',')
            lat = float(l[0])
            lon = float(l[1])
            mesh_points.append([lat, lon])

    with open(fno, 'w') as of:
        for this_location in mesh_points:
            neighbor_indices = np.linalg.norm(np.asarray(points) - np.asarray(this_location), axis=1).argsort()[:4]
            neighbor_scores = [images[x][2] for x in neighbor_indices]
            neighbor_lat = [images[x][0] for x in neighbor_indices]
            neighbor_lon = [images[x][1] for x in neighbor_indices]

            score_distortion_ratio = random.uniform(0.15, 0.5)
            output_score = np.mean(neighbor_scores) * (score_distortion_ratio) + random.uniform(0, 10) * (
                1 - score_distortion_ratio)

            of.write(str(this_location[0]) + ',' + str(this_location[1]) + ',' + str(output_score) + '\n')

    print '%s written', mesh_file


mesh_folder = sys.argv[1]
score_folder = sys.argv[2]
out_folder = sys.argv[3]

meshes = glob.glob(os.path.join(mesh_folder,'*.csv'))

varargs = []
for mesh_file in meshes:
    mesh_city_name =  os.path.basename(mesh_file).split('_')[1]
    score_file_name = os.path.join(score_folder, mesh_city_name)
    fno = os.path.join(out_folder, mesh_city_name)

    varargs.append([mesh_city_name, score_file_name, fno])

pool = Pool(processes=32)
pool.map(process_images, varargs)