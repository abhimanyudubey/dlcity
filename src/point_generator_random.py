import numpy as np
import glob
import os
from matplotlib.path import Path
from scipy.spatial import ConvexHull
import argparse


def inConvexHull(point, hull):
    return hull.contains_point(point)

def generatePoints(hull, bd, n_points, handle='city'):
    points = []
    c = 0
    while c<n_points:
        x = np.random.uniform()*(bd[1]-bd[0]) + bd[0]
        y = np.random.uniform()*(bd[3]-bd[2]) + bd[2]
        if inConvexHull((x,y), hull):
            points.append((x,y))
            c+=1
        if not c%1000:
            print '%d points generated from %s' % (c, handle)
    return points

def writePointsToFile(points, output_file):
    par_dir = os.path.pardir(output_file)
    if not os.path.exists(par_dir):
        os.makedirs(par_dir)

    with open(output_file, 'w') as of:
        for point in points:
            of.write('%f, %f\n' % point)

def getConvexHull(file_name):
    pts = []
    with open(file_name, 'r') as f:
        for line in f:
            ptx = float(line.strip().split(',')[0])
            pty = float(line.strip().split(',')[1])
            pts.append((ptx, pty))
    return ConvexHull(pts), pts

def getBoundaries(points):
    max_x = max([x[0] for x in points])
    min_x = min([x[0] for x in points])
    max_y = max([x[1] for x in points])
    min_y = min([x[1] for x in points])

    return (max_x, min_x, max_y, min_y)

if __name__ == '__main__':
    parser = argparse.ArgumentParser('Random Point Generator')
    parser.add_argument('-i', '--input', help='Input directory for CSV files', required=True, type=str)
    parser.add_argument('-s', '--scale', help='Scale factor for each city', required=False, default=2000, type=float)
    parser.add_argument('-o', '--output', help='Output directory for CSV files', required=True, type=str)

    args = parser.parse_args()

    locations = glob.glob(os.path.join(args.input,'*.csv'))
    for location in locations:
        base_name = os.path.basename(location)
        out_location = os.path.join(args.output, base_name)
        hull, points = getConvexHull(location)
        hull_path = Path(points)
        n_points = int(args.scale*hull.area)

        bd = getBoundaries(points)
        points = generatePoints(hull_path, bd, n_points, base_name)

        writePointsToFile(points, out_location)
        print '%s points generated successfully' % (out_location)
