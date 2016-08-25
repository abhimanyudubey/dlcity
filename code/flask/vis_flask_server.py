from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import glob
import random

def random_line(afile):
    line = next(afile)
    for num, aline in enumerate(afile):
      if random.randrange(num + 2): continue
      line = aline
    return line

app = Flask(__name__)

@app.route("/")

def main():
    dir_src = '/home/nikhil/data/placepulse2/images_original/'
    os.system("rm /home/dubeya/dlcity/code/flask/templates/*.JPG")
    subdir_src = [x for x in glob.glob(os.path.join(dir_src, '*')) if os.path.isdir(x)]
    random_subdir = random.choice(subdir_src)
    random_city = os.path.basename(random_subdir)
    target_file = open(os.path.join('/home/dubeya/extrapolated_votes/safety/scores',random_city+"_scores.csv"),'r')
    score = 0
    fname = ""

    line = random_line(target_file)
    fname = line.strip().split(',')[0]
    score = line.strip().split(',')[1]

    imgsrc = os.path.join(random_subdir,fname)
    os.system("cp "+imgsrc+" /home/dubeya/dlcity/code/flask/templates/")
    imgsrc = "/home/dubeya/dlcity/code/flask/templates/"+fname
    return render_template('index.html',imgpath=imgsrc,imgscore=score,imgcity=random_city)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=121,threaded=True)