import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(prog='generate_samples.py')

parser.add_argument('-i','--input',help='path to csv file with 3 fields: lat,long,score',required=True)
parser.add_argument('-o','--output',help='output file path to store image',required=True)
parser.add_argument('-r','--ratio',help='ratio of points to be selected, default 1',required=False,default=1,type=float)
parser.add_argument('-s','--size',help='size of dots, default 0.005',required=False,default=0.005,type=float)
args = vars(parser.parse_args())

colors = ['r','#ffae00','y','#58a028','#274f0d']

data = np.genfromtxt(args['input'],delimiter=',')

val_max = np.max(data[:,2])
val_min= np.min(data[:,2])

data[:,2] = (data[:,2] - val_min)*10/(val_max + 0.00001 - val_min)

n_selected_rows = int(args['ratio']*len(data))

shuffled_data = data
np.random.shuffle(shuffled_data)
shuffled_data = shuffled_data[:n_selected_rows]

datapoints = []
for i in range(5):
    datapoints.append([])

for point in shuffled_data:
    val = point[2]
    ind = int(val/2)
    datapoints[ind].append(point[:2])

for i in range(5):
    datapoints[i] = np.array(datapoints[i])

datapoints.reverse()

for i,point_set in enumerate(datapoints):
    plt.scatter(point_set[:,0],point_set[:,1],c=colors[i],s=args['size'],lw = 0)

plt.savefig(args['output'],dpi=300)

