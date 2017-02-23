import distmesh as dm
import numpy as np
import os
import argparse
import glob
from multiprocessing import Pool

def process(inputs):
    csv_file = inputs[0]
    out_file = inputs[1]
    points = inputs[2]

    min_x = min([x[0] for x in points])
    min_y = min([x[1] for x in points])
    max_x = max([x[0] for x in points])
    max_y = max([x[1] for x in points])

    fd = lambda p: dm.dpoly(p, points)
    gen_points, gen_triangles = dm.distmesh2d(fd, dm.huniform, args['scale'], (min_x, min_y, max_x, max_y), points, None)

    with open(out_file, 'w') as of:
        for pt in gen_points:
            x = str(pt[0])
            y = str(pt[1])
            of.write(x+','+y+'\n')

    print 'File: %s, %d vertices, %d points generated.' % (csv_file, len(points), len(gen_points))


parser = argparse.ArgumentParser('Generate uniform mesh of points from CSV file')

parser.add_argument('-i', '--input', help='input folder with CSV files', type=str, required=True)
parser.add_argument('-o', '--output', help='output folder to generate points in', type=str, required=True)
parser.add_argument('-s', '--scale', help='scale factor for point generation', type=float, required=False, default=0.001)
parser.add_argument('-c', '--cores', help='number of threads (multithreaded)', type=int, required=False, default=1)

args = vars(parser.parse_args())

csv_files = glob.glob(os.path.join(args['input'], '*.csv'))
print '%d CSV files found, processing...' % len(csv_files)

process_args = []

for csv_file in csv_files:
    out_file = os.path.join(args['output'], os.path.basename(csv_file))
    points = [list(x) for x in list(np.genfromtxt(csv_file, delimiter=','))]

    process_args.append([csv_file, out_file, points])

if args['cores'] > 1:
    pool = Pool(processes=args['cores'])
    pool.map(process, process_args)
else:
    for p_args in process_args:
        process(p_args)

print 'All files written successfully'



