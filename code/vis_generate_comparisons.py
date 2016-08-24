import caffe
import sys
import glob
import random
import os
from trueskill import TrueSkill
import numpy as np
from multiprocessing import Pool


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


if __name__ == "__main__":

    if (len(sys.argv) < 5):
        print "Usage python vis_generate_comparisons.py <folder-name> <output-folder-name>"
    else:
        dir_src = sys.argv[1]
        dir_out = sys.argv[2]
        # this script takes in a source directory and output directory and a
        # caffe model and generate votes for all images present in all subfolders of this directory
        file_ref = sys.argv[3]
        dir_ref_images = sys.argv[4]

        # first generating global reference parameters
        global_params, global_ts, global_vals = generate_scores(file_ref)
        global_image_dir = glob.glob(os.path.join(dir_ref_images, '*.jpg')) + glob.glob(
            os.path.join(dir_ref_images, '*.JPG'))

        subdir_src = [x for x in glob.glob(os.path.join(dir_src, '*')) if os.path.isdir(x)]

        if not os.path.exists(os.path.join(dir_out, 'votes')):
            os.makedirs(os.path.join(dir_out, 'votes'))

        if not os.path.exists(os.path.join(dir_out, 'scores')):
            os.makedirs(os.path.join(dir_out, 'scores'))

        out_pairs = []

        for subdir in subdir_src:
            # for each subdirectory of images, we do the comparisons
            # with 15 random images from reference along 15 random from set with their votes
            list_img = glob.glob(os.path.join(subdir, '*.jpg')) + glob.glob(os.path.join(subdir, '*.JPG'))
            file_vote = os.path.join(dir_out, 'votes', os.path.basename(subdir))
            file_scores = os.path.join(dir_out, 'scores', os.path.basename(subdir))

            out_images1 = [];
            out_images2 = [];

            print 'Generating comparisons for subdirectory', subdir, 'right now'
            print 'Total number of images', len(list_img), ', total votes generated will be', len(list_img) * 20

            for i in range(0, len(list_img)):
                # first 15 votes will be with random images and the image itself
                img1 = list_img[i]
                list_img_copy = list(list_img)
                list_img_copy.remove(img1)

                j_list1 = [];
                for j in range(15):
                    j_list1.append(random.choice(global_image_dir))
                for j in range(15):
                    j_list1.append(random.choice(list_img_copy))


                for j in range(30):
                    out_pairs.append((img1, j_list1[j]))
                    #         out_images1.append(image1)
                    #         out_images2.append(res1[j])
                    #
                    #
                    #     if i%batchsize==0 and i>0:
                    #         pred = []
                    #         out = net.forward_all(data1=np.asarray(out_images1),data2=np.asarray(out_images2))
                    #         preds = out['fc8r']
                    #
                    #         for k in range(0,batchsize*20):
                    #             pred = preds[k] / np.linalg.norm(preds[k], ord=1)
                    #             if pred[0] > pred[1]:
                    #                 votes.write(out_pairs[k][0] + ' ' + out_pairs[k][1] + ' ' + out_pairs[k][0] + '\n')
                    #             else:
                    #                 votes.write(out_pairs[k][0] + ' ' + out_pairs[k][1] + ' ' + out_pairs[k][1] + '\n')
                    #
                    #         out_images1 = []
                    #         out_images2 = []
                    #         out_pairs = []
                    #
                    #         print 'Generated',i*20,'votes out of ',len(list_img)*20
                    #
                    # if len(out_pairs)>0:
                    #     # tackling the left-over images
                    #     pred = []
                    #
                    #     while not len(out_images1)==batchsize*20:
                    #         out_images1.append(out_images1[0])
                    #         out_images2.append(out_images1[0])
                    #
                    #     out = net.forward_all(data1=np.asarray(out_images1), data2=np.asarray(out_images2))
                    #     preds = out['fc8r']
                    #
                    #     for k in range(0, out_pairs):
                    #         pred = preds[k] / np.linalg.norm(preds[k], ord=1)
                    #         if pred[0] > pred[1]:
                    #             votes.write(out_pairs[k][0] + ' ' + out_pairs[k][1] + ' ' + out_pairs[k][0] + '\n')
                    #         else:
                    #             votes.write(out_pairs[k][0] + ' ' + out_pairs[k][1] + ' ' + out_pairs[k][1] + '\n')
                    #
                    #     out_images1 = []
                    #     out_images2 = []
                    #     out_pairs = []
                    #
                    #     print 'Generated all votes in this subdirectory'
                    #
                    # votes.close()
                    # # now that votes are generated we will write them to a file after generating scores
                    # subdir_params,subdir_ts,subdir_vals = update_scores(file_vote,global_params,global_ts)
                    # for key,value in subdir_params.iteritems():
                    #     if key in list_img:
                    #         # write only those scores that belong to that subdir
                    #         file_scores.write(','.join([key,str(value[0])]))
                    #
                    # file_scores.close()

        f1 = open('/home/dubeya/extrapolated_votes/safety/comparisons_1', 'w')
        f2 = open('/home/dubeya/extrapolated_votes/safety/comparisons_2', 'w')
        for pair in out_pairs:
            f1.write(out_pairs[0]+" 0\n")
            f2.write(out_pairs[1]+" 0\n")




