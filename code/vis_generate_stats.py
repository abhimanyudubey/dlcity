import os
import glob
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

src_folder = "/home/dubeya/extrapolated_votes/safety/scores_final/normalized/"

csv_files = glob.glob(os.path.join(src_folder,"*.csv"))

global_mean = 0
citywise_stats = {}
citywise_scores = {}

for csv_file in csv_files:
    scores = []
    cityname = os.path.basename(cityname).replace("_normalized.csv"."")
    with open(csv_file,'r') as f:
        for line in f:
            score = float(line.strip().split(',')[1])
            scores.append(score)
    citywise_scores[cityname]=scores

bins = np.linspace(0,10,200)

stats_file = "/home/dubeya/extrapolated_votes/safety/scores_final/normalized/stats.txt"

plt.figure(figsize=(35,35))
with open(stats_file,'w') as f:
    for cityname,cityscores in citywise_scores.iteritems():
        mean_score = np.asarray(cityscores).mean()
        sigma_score = np.asarray(cityscores).std()
        citywise_stats[cityname] = (mean_score,sigma_score)
        f.write(cityname+","+str(mean_score)+","+str(sigma_score)+","+str(len(cityscores)))
        plt.hist(np.asarray(cityscores),bins,alpha=0.4,label=cityname+' '+mean_score+' '+sigma_score)

plt.legend(loc='upper right')
plt.plot()
plt.savefig('stats.pdf',format='pdf')



