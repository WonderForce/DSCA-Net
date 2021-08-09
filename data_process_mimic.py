import pandas as pd
import numpy as np
import random
from sklearn.model_selection import train_test_split
# import impyute as impy
from fancyimpute import KNN, SimpleFill
# import keras.backend as K
import gc
#version 2.0 knn impute
for days in list([100]):
    seq1 = []
    seq2 = []
    dualseqs = []
    x = []
    y = []
    dualseq_demographic = []
    dualseq_without_demographic = []

    # onehot
    dfd = pd.read_csv('/home/xxx/drug_data/lw_dataset_%d.csv' % days)
    dfd = dfd.drop(columns=['startdate'])
    dfd = pd.get_dummies(dfd, columns=['gender', 'religion', 'language_', 'marital_status', 'ethnicity'])
    dfd.to_csv('/home/xxx/drug_data/lw_dataset_onehot_%d.csv' % days, index=False)


    #impute
    dfd = pd.read_csv('/home/xxx/drug_data/lw_dataset_onehot_%d.csv' % days)
    for i in range(dfd.columns.shape[0]):
        print(days, 'days:', i, dfd.columns[i])
    dfdv = np.array(dfd.values, dtype=float)
    dfdcolumns = dfd.columns
    partsize = 5000
    partsnum = int(dfdv.shape[0]/partsize)
    dfdshape = dfdv.shape
    dfdimp = []
    dfdfinal = []
    del dfd
    gc.collect()
    print('sum %d parts' % partsnum)
    for i in range(partsnum):
        part = []
        if i+1 == partsnum:
            part = dfdv[i*partsize:]
            # print(i*partsize, 'end')
        else:
            part = dfdv[i*partsize:(i+1)*partsize]
            # print(i*partsize, (i+1)*partsize)
        part = KNN(k=10, verbose=False).fit_transform(part)
        # part = impy.fast_knn(part, k=10)
        for row in part:
            dfdimp.append(row)
        dfdfinal = dfdimp
        dfdfinal = np.array(dfdfinal)
        dfdimpute = pd.DataFrame(dfdfinal, columns=dfdcolumns)
        for col in dfdimpute.columns:
            if dfdimpute[col].isnull().sum() != 0:
                print('error', col, dfdimpute[col].isnull().sum())
        np.save('/home/xxx/drug_data/knnimpute_dfdfinal_%d.npy' % days, dfdfinal)
        dfdimpute.to_csv('/home/xxx/drug_data/lw_dataset_onehot_knnimpute_%d.csv' % days, index=False)
        print('part %d done' % (i+1))
        print('current shape:',dfdfinal.shape)
    print('impute finish!!!')


    # make dataset seqsdown
    dfhd = pd.read_csv('/home/xxx/drug_data/hadm_days_%s.csv' % days)
    dfdimpute = pd.read_csv('/home/xxx/drug_data/lw_dataset_onehot_knnimpute_%d.csv' % days)
    print(days, dfhd.values.shape)
    print(days, dfdimpute.values.shape)
    for i in range(dfdimpute.columns.shape[0]):
        print(i, dfdimpute.columns[i])
    for hid in dfhd.values[:, 0]:
        tem = dfdimpute[dfdimpute['hadm_id'] == hid].values
        hdays = tem.shape[0]
        # print(tem.shape, hdays)
        if tem.shape[0] != hdays:
            print('error')
        # print(hid, len)
        hy = tem[:, 1:401]
        for i in hy:
            if sum(i) == 0:
                print('all 0')
        y_ = []
        for j in range(hdays):
            if j + 1 == hdays:
                y_.append(np.zeros(hy.shape[1], dtype=int))
            else:
                y_.append(hy[j + 1])
        y.append(np.array(y_[:-1]))
        # seq1.append(tem[:-1, 401:])
        # seq2.append(tem[:-1, 1:401])
        dualseqs.append(tem[:-1, 1:])
        # dualseq_demographic.append(tem[:-1, 431:])
        # dualseq_without_demographic.append(tem[:-1, 1:431])
    # seq1 = np.array(seq1)
    # seq2 = np.array(seq2)
    dualseqs = np.array(dualseqs)
    y = np.array(y)
    # dualseq_demographic = np.array(dualseq_demographic)
    # dualseq_without_demographic = np.array(dualseq_without_demographic)
    print(y[0].shape)
    # print(seq1[0].shape)
    # print(seq2[0].shape)
    print(dualseqs[0].shape)
    # print(dualseq_demographic[0].shape)
    # print(dualseq_without_demographic[0].shape)
    # print(seq2.shape)
    sumdays = 0
    for p in y:
        print(p.shape)
        sumdays += p.shape[0]
        for d in p:
            if sum(d) == 0:
                print('all 0')
    print('sumdays:', sumdays)
    np.save('/home/xxx/drug_data/dualseqs_down_%d.npy' % days, dualseqs)
    np.save('/home/xxx/drug_data/seqy_down_%d.npy' % days, y)
    print(days, 'save!')
