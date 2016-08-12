import os,sys
import glob

if __name__=="__main__":

    if(len(sys.argv)<3):
        print "Usage python data_preprocess_convert_votes_to_labels.py <folder-name> <output-folder-name> <optional-file-name-prefix>"
    else:
        # converting the votes format to the label format required by caffe
        dir_src = sys.argv[1]
        dir_dst = sys.argv[2]
        prefix_filename = ""
        if(len(sys.argv)>3):
            prefix_filename = sys.argv[3]

        if not os.path.exists(dir_src):
            print "Source directory not found, exiting"
        else:
            # source directory exists, continuing
            print "Source directory located at ",dir_src
            list_csv = glob.glob(os.path.join(dir_src,"*.csv"))
            print len(list_csv),"files found at source"

            if not os.path.exists(dir_dst):
                os.makedirs(dir_dst)

            for file_csv in list_csv:
                print "Processing file ",file_csv
                with open(file_csv,'r') as f:
                    fl = open(os.path.join(dir_dst,os.path.basename(file_csv)+".left"),'w')
                    fr = open(os.path.join(dir_dst,os.path.basename(file_csv)+".right"),'w')
                    next(f)
                    # skipping first line as it has only headers everytime
                    for line in f:
                        line = line.strip().split(",")
                        file_left = line[0]
                        file_right = line[1]
                        winner = line[2]
                        line_l = os.path.join(prefix_filename,file_left)
                        line_r = os.path.join(prefix_filename,file_right)
                        if winner == file_left:
                            # left file wins
                            line_l = line_l + " 1"
                            line_r = line_r + " 0"
                        else:
                            line_l = line_l + " 0"
                            line_r = line_r + " 1"
                        fl.write(line_l+"\n")
                        fr.write(line_r+"\n")
                    fl.close()
                    fr.close()



