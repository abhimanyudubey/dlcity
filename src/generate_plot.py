import glob
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['xtick.labelsize'] = 6
import matplotlib.pyplot as plt
import numpy as np
import os

inp_file = '/home/dubeya/dlcity/data/dense_safety_30'

csv_list = glob.glob(inp_file+'/*.csv')
mats = [np.genfromtxt(x, delimiter=',') for x in csv_list]

means = [np.mean(x[:,2]) for x in mats]
sigmas = [np.std(x[:,1]) for x in mats]
citynames = [os.path.basename(x).replace('.csv','') for x in csv_list]

data = sorted([(m,s,c) for m,s,c in zip(means,sigmas,citynames)])

sm = [x[0] for x in data]
ss = [x[1] for x in data]
sc = [x[2] for x in data]

plt.figure()
plt.errorbar(range(5,len(sm)+5), sm, yerr=ss)
plt.xticks(range(5,len(sm)+5), sc, rotation='vertical')
plt.savefig('output.png', dpi=600)