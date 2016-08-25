import sys
import glob
import random
import os
from trueskill import TrueSkill
import numpy as np
import h5py

def load_image(inp):
    inp_file = inp[0]
    transformer = inp[1]
    image = transformer.preprocess('data', caffe.io.load_image(inp_file))
    return image

def generate_scores(voteFile):
    # function to generate scores using TrueSkill using a vote file given in the format:
    # image1 image2 winning-image

    f1 = open(voteFile);

    mu0 = 25;
    var0 = (mu0 / 3.0) ** 2;
    beta2 = var0 / 4.0;
    tau2 = var0 / 100.0;
    prob_draw = 0.1333;
    ts = TrueSkill(beta2, tau2, prob_draw, var0);
    params = {};
    vals = [[], [], [], [], []];
    c = 0;

    for vote in f1:
        vote = vote.strip().split();
        win = 0;
        if vote[1] == vote[2]: win = 1;
        if vote[0] not in params: params[vote[0]] = (mu0, var0);
        if vote[1] not in params: params[vote[1]] = (mu0, var0);
        if not win:
            params[vote[0]], params[vote[1]] = ts.update_rating(params[vote[0]], params[vote[1]], False);
        else:
            params[vote[1]], params[vote[0]] = ts.update_rating(params[vote[1]], params[vote[0]], False);
        if c % 10000 == 0:
            mu_mu, mu_sigma, sigma_mu, sigma_sigma = 0.0, 0.0, 0.0, 0.0;
            mus, sigmas = [], [];

            for key, value in params.iteritems():
                mu_mu += value[0];
                sigma_mu += value[1];
                mus.append(value[0]);
                sigmas.append(value[1]);

            mu_mu = np.mean(mus);
            sigma_mu = np.mean(sigmas);
            mu_sigma = np.std(np.array(mus));
            sigma_sigma = np.std(np.array(sigmas));

            vals[0].append(mu_mu);
            vals[1].append(sigma_mu);
            vals[2].append(mu_sigma);
            vals[3].append(sigma_sigma);
            vals[4].append(c);

        c += 1;

    f1.close();

    return params, ts, vals;


def update_scores(voteFile, ts, params):
    # function to update scores given an existing trueskill object and parameters using a different votefile
    mu0 = 25;
    var0 = (mu0 / 3.0) ** 2;
    beta2 = var0 / 4.0;
    tau2 = var0 / 100.0;
    prob_draw = 0.1333;
    f1 = open(voteFile);
    c = 0;
    vals = [[], [], [], [], []];

    for vote in f1, f2:
        vote = vote.replace(',', ' ');
        vote = vote.strip().split();
        win = 0;
        if vote[1] == vote[2]: win = 1;
        if vote[0] not in params: params[vote[0]] = (mu0, var0);
        if vote[1] not in params: params[vote[1]] = (mu0, var0);
        if not win:
            params[vote[0]], params[vote[1]] = ts.update_rating(params[vote[0]], params[vote[1]], False);
        else:
            params[vote[1]], params[vote[0]] = ts.update_rating(params[vote[1]], params[vote[0]], False);
        if c % 10000 == 0:
            mu_mu, mu_sigma, sigma_mu, sigma_sigma = 0.0, 0.0, 0.0, 0.0;
            mus, sigmas = [], [];

            for key, value in params.iteritems():
                mu_mu += value[0];
                sigma_mu += value[1];
                mus.append(value[0]);
                sigmas.append(value[1]);

            mu_mu = np.mean(mus);
            sigma_mu = np.mean(sigmas);
            mu_sigma = np.std(np.array(mus));
            sigma_sigma = np.std(np.array(sigmas));

            vals[0].append(mu_mu);
            vals[1].append(sigma_mu);
            vals[2].append(mu_sigma);
            vals[3].append(sigma_sigma);
            vals[4].append(c);

        c += 1;

    f1.close();

    return params, ts, vals;

if __name__=="__main__":
    if len(sys.argv)<6:
        print "Usage: python vis_generate_scores_from_comparisons.py <input-h5-file> <input-vote-file> <input-ref-vote-file> <output-directory> <input-directory>"
        h5_file = sys.argv[1]
        input_vote_file_left = sys.argv[2]+"_1"
        input_vote_file_right = sys.argv[2]+"_2"

        #first construct the folder-wise dictionary
        parent_directories = {}

        print "Reading votes file first pass"
        f = open(input_vote_file_left,'r')
        for line in f:
            line = line.strip().split()[0]
            basename = os.path.basename(line)
            parent_dir = os.path.pardir(line)
            parent_directories[basename] = parent_dir
        f.close()
        f = open(input_vote_file_right,'r')
        for line in f:
            line = line.strip().split()[0]
            basename = os.path.basename(line)
            parent_dir = os.path.pardir(line)
            parent_directories[basename] = parent_dir
        f.close()

        print "Creating global parameters"

        # parent wise dictionary constructed, now reading the original vote file

        file_ref = sys.argv[3]
        global_params, global_ts, global_vals = generate_scores(file_ref)

        # original scores computed, now computing the new scores

        print "Generating prediction file"

        counter = 0;
        vote_file = h5py.File(h5_file,'r')
        n_db = len(vote_file.keys())
        data_ind = 0
        preds = np.array(vote_file['data'+str(data_ind)]).reshape(813,2)

        output_dir = sys.argv[4]
        output_file = open(os.path.join(output_dir,'ts_comparisons'),'w')

        with open(input_vote_file_left,'r') as f_left, open(input_vote_file_right,'r') as f_right:
            for line_left,line_right in zip(f_left,f_right):
                basename_left = os.path.basename(line_left.strip().split()[0])
                basename_right = os.path.basename(line_right.strip().split()[0])
                data_ind = int(counter/813)
                key_name = 'data'+str(data_ind)
                pred = preds[counter%813]
                if pred[0]> pred[1]:
                    output_file.write(basename_left + ' ' + basename_right + ' ' + basename_left + '\n')
                else:
                    output_file.write(basename_left + ' ' + basename_right + ' ' + basename_right + '\n')

                counter+=1
                if counter % 813 == 0:
                    data_ind+=1
                    preds = np.array(vote_file['data' + str(data_ind)]).reshape(813, 2)

        output_file.close()

        # now generating new parameters
        print "Generating parameters"

        new_params, new_ts, new_vals = update_scores(os.path.join(output_dir,'ts_comparisons'),global_ts,global_params)

        print "Writing output"

        dir_src = sys.argv[5]
        subdir_src = [x for x in glob.glob(os.path.join(dir_src, '*')) if os.path.isdir(x)]

        for subdir in subdir_src:
            output_file = os.path.join(output_dir,os.path.basename(subdir)+"_votes.csv")
            subdir_images = glob.glob(os.path.join(subdir,'*.jpg'))+glob.glob(os.path.join(subdir,'*.JPG'))
            with open(output_file,'w') as op_file:
                for subdir_image in subdir_images:
                    image_filename = os.path.basename(subdir_image)
                    op_file.write(image_filename+","+str(new_params[image_filename][0])+'\n')
            print "Written folder",subdir
