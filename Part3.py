import numpy as np
import itertools
import Part2
import codecs


def mle_transition(file):
    f = codecs.open(file, 'r', "UTF-8")
    labels = ['START']
    for line in f.readlines():
        if line != '\n':
            labels.append(line.split()[1])
        else:
            labels.append('STOP')
            labels.append('START')

    labels = labels[:-1] # drop last 'START'

    label_dic = {}
    for i in labels:
        if i in label_dic:
            label_dic[i] += 1
        else:
            label_dic[i] = 1

    trans = {}
    for i in range(len(labels)-1):
        pair = labels[i]+labels[i+1]
        if pair != 'STOPSTART':
            if pair in trans:
                trans[pair] += 1
            else:
                trans[pair] = 1
    y_list = ['O', 'B-positive', 'I-positive', 'B-negative', 'I-negative',
              'B-neutral', 'I-neutral', 'START', 'STOP']
    pairs = list(itertools.permutations(y_list, 2))

    mle_trans = {}
    for i in range(len(pairs)):
        pair = pairs[i][0]+pairs[i][1]
        if pair in trans:
            mle_trans[pair] = trans[pair]/label_dic[pairs[i][0]]
        else:
            mle_trans[pair] = 0
    for i in y_list:
        if i+i in trans:
            mle_trans[i+i] = trans[i+i]/label_dic[i]
        else:
            mle_trans[i+i] = 0
    return mle_trans


def viterbi(trans, emmis, obs, labels):
    matrix = np.zeros((len(labels), len(obs)))
    path_mat = []
    for i in range(matrix.shape[1]):
        path = []
        if i == 0:
            for j in range(matrix.shape[0]):
                if labels[j]+'-->'+obs[i] in emmis:
                    matrix[j][i] = trans['START'+labels[j]]*emmis[labels[j]+'-->'+obs[i]]
                else:
                    matrix[j][i] = trans['START'+labels[j]]*emmis[labels[j]+'-->#UNK#']
                path.append(j)
        else:
            for j in range(matrix.shape[0]):
                score = []
                for k in range(matrix.shape[0]):
                    score.append(np.multiply(trans[labels[k]+labels[j]], matrix[k][i-1]))
                if labels[j]+'-->'+obs[i] in emmis:
                    score = np.multiply(score, emmis[labels[j]+'-->'+obs[i]])
                else:
                    score = np.multiply(score, emmis[labels[j] + '-->' + '#UNK#'])
                matrix[j][i] = max(score)
                path.append(np.argmax(score))
        path_mat.append(path)
    last_score = []
    path_mat = np.transpose(path_mat)
    for i in range(len(labels)):
        last_score.append(np.multiply(matrix[i][-1], trans[labels[i]+'STOP']))
    best_path_rev = [np.argmax(last_score)]

    # retrieve the reversed best path from path_mat
    for i in range(len(obs)-1):
        i = i+1
        best_path_rev.append(path_mat[best_path_rev[i-1]][-i])
    best_path = best_path_rev[::-1]
    best_label = []
    for i in best_path:
        best_label.append(labels[i])
    return best_label


trans = mle_transition('train_fixed')
emmis = Part2.mle_emission('train_fixed')
labels = ['O', 'B-positive', 'I-positive', 'B-negative', 'I-negative',
               'B-neutral', 'I-neutral']

out = codecs.open('EN_Part3.out', 'w', "UTF-8")
f = codecs.open('dev.in', 'r', "UTF-8")
data = []
post = []

for x in f.readlines():
    if x != '\n':
        post.append(x.replace('\n', ''))
    else:
        data.append(post)
        post = []

for post in data:
    v = viterbi(trans, emmis, post, labels)
    for l in range(len(v)):
        out.write(post[l]+' '+v[l]+'\n')
    out.write('\n')
f.close()
out.close()