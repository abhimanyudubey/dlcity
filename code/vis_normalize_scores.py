import sys
import os
import glob

if __name__=="__main__":
    if len(sys.argv)<2:
        print "Usage python vis_normalize_scores.py <input-folder>"
    else:
        dir_src = sys.argv[1]
        csvlist = glob.glob(os.path.join(dir_src,"_votes.csv"))

        global_max = 0.0;
        global_min = 1000.0;

        for csvfile in csvlist:
            with open(csvfile,'r') as f:
                for line in f:
                    csvscore = float(line.strip().split(',')[1])
                    if csvscore > global_max:
                        global_max = csvscore
                    elif csvscore < global_min:
                        global_min = csv_score

        for csvfile in csvlist:
            with open(csvfile, 'r') as f, open(csvfile.replace("_votes","_scores"),'w') as of:
                for line in f:
                    fname = line.strip().split(',')[0]
                    csvscore = float(line.strip().split(',')[1])
                    norm_csv_score = 10*(csvscore-global_min)/global_max
                    of.write(fname+','+str(norm_csv_score)+'\n')



