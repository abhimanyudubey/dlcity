import os
import numpy as np
import glob
import matplotlib.pyplot as plt


src_folder = "/Users/dubeya/normalized/"

cities = {}
cities['USA'] = ['WashingtonDC','Chicago','Denver','Valparaiso','Minneapolis','Seattle','NewYork','LosAngeles','Portland','Houston','Boston','SanFrancisco']
cities['Europe'] = ['Kiev','Paris','Stockholm','Zagreb','Moscow','Helsinki','Munich','Bratislava','Lisbon','Dublin','Barcelona','Rome','Bucharest','Prague','Milan','London','Madrid','Glasgow','Amsterdam','Copenhagen','Warsaw']
cities['NorthAmerica'] = cities['USA']+['Guadalajara','Montreal','MexicoCity','Toronto']
cities['SouthAmerica'] = ['BeloHorizonte','Santiago','SaoPaulo']
cities['Asia'] = ['Seoul','Bangkok','TelAviv','HongKong','Tokyo','Taipei','Singapore']
cities['Africa'] = ['Gaborone']

csv_files = glob.glob(os.path.join(src_folder,"*.csv"))

global_mean = 0
citywise_stats = {}
citywise_scores = {}


for csv_file in csv_files:
    scores = []
    cityname = os.path.basename(csv_file).replace("_normalized.csv","")
    with open(csv_file,'r') as f:
        for line in f:
            score = float(line.strip().split(',')[1])
            scores.append(score)
    citywise_scores[cityname]=scores

bins = np.linspace(0,10,200)

print citywise_scores.keys()
plt.figure(figsize=(20,20))

for cont,cities in cities.iteritems():
    score_hist = []
    for city in cities:
        score_hist += citywise_scores[city]
    cont_score_mean = np.asarray(score_hist).mean()
    cont_score_sigma = np.asarray(score_hist).std()
    plt.hist(np.asarray(score_hist),bins,alpha=0.2,label=cont+" "+str(cont_score_mean)+" "+str(cont_score_sigma),normed=True)

plt.legend(loc='upper right')
plt.show()


