#coding:utf-8
import numpy as np
import os
import sys
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm, metrics
from sklearn.neighbors import KNeighborsClassifier

from HDFProcess import *

def SVMClass(Data_Train, Data_Target, Data_Test, expected= None):

    clf = svm.SVC(gamma=0.001)
    clf = clf.fit(Data_Train, Data_Target)

    # model = SelectFromModel(clf, prefit=True)
    # x = model.transform(Data_Train)

    pre = clf.predict(Data_Test)

    if not expected is None:
        print("Classification report for classifier %s:\n%s\n"
          % (clf, metrics.classification_report(expected, pre)))

    print 'clf.score:',clf.score(Data_Test, pre)
    print 'n_outputs_',clf.n_outputs_
    print 'classes_',clf.classes_
    print 'n_classes_:',clf.n_classes_
    print 'n_features_:',clf.n_features_
    print 'feature_importances_:',clf.feature_importances_
    print 'oob_score:', clf.oob_score
    print 'oob_score:', clf.oob_score_
    print clf.score(Data_Test, pre)
    print pre

    return pre



def RFClass(Data_Train, Data_Target, Data_Test, expected= None):

    clf = RandomForestClassifier(#n_estimators=50,
                               # warm_start=True,
                                oob_score=True,
                               max_features="sqrt")
    clf = clf.fit(Data_Train, Data_Target)

    # model = SelectFromModel(clf, prefit=True)
    # x = model.transform(Data_Train)

    pre = clf.predict(Data_Test)

    if not expected is None:
        print("Classification report for classifier %s:\n%s\n"
          % (clf, metrics.classification_report(expected, pre)))

    print 'clf.score:',clf.score(Data_Test, pre)
    print 'n_outputs_',clf.n_outputs_
    print 'classes_',clf.classes_
    print 'n_classes_:',clf.n_classes_
    print 'n_features_:',clf.n_features_
    print 'feature_importances_:',clf.feature_importances_
    print 'oob_score:', clf.oob_score
    print 'oob_score:', clf.oob_score_
    print clf.score(Data_Test, pre)
    print pre

    return pre

if __name__ == '__main__':
    L1file = r'G:\PythonPro\TanSat\DATA\sample\L1\TanSat_ACGS_1B_SCI_ND_2X2KM_ORBT_07665_20180601_0704_V02_170419.h5'
    CLMfile = r'G:\PythonPro\TanSat\DATA\sample\L1\TanSat_ACGS_1B_SCI_ND_2X2KM_ORBT_07665_20180601_0704_V02_170419.hdf'
    outfile = r'G:\PythonPro\TanSat\DATA\sample\L1\pca.hdf'

    sounding_qual_flag = ReadHDF(L1file, '/SoundingMeasurements/sounding_qual_flag')
    radiance_o2 = ReadHDF(L1file, '/SoundingMeasurements/radiance_o2')
    sounding_id = ReadHDF(L1file, '/SoundingGeometry/sounding_id')
    sounding_latitude = ReadHDF(L1file, '/SoundingGeometry/sounding_latitude')
    sounding_longitude = ReadHDF(L1file, '/SoundingGeometry/sounding_longitude')

    CLM = ReadHDF(CLMfile, 'mask')

    nScan = sounding_id.shape[0]
    nPix = sounding_id.shape[1]

    # 剔除质量差的探元
    index = np.where(sounding_qual_flag == 0)

    sounding_qual_flag = sounding_qual_flag[index]
    radiance_o2 = radiance_o2[index]
    sounding_id = sounding_id[index]
    sounding_latitude = sounding_latitude[index]
    sounding_longitude = sounding_longitude[index]
    CLM = CLM[index]

    Data_Train = []
    Data_Target = []
    nScan = sounding_id.shape[0]
    for iscan in range(nScan):
        data1 = []
        tempdata = radiance_o2[iscan, :]
        data1.extend(tempdata[19:59])
        data1.extend(tempdata[ 79:109])
        data1.extend(tempdata[ 749:769])
        data1.extend(tempdata[899:979])
        data1.extend(tempdata[1054:1119])
        Data_Train.append(data1)
        Data_Target.append(CLM[iscan])

    Data_Train = np.array(Data_Train)
    # print(radiance_o2.shape)
    nScan = Data_Train.shape[0]
    nChan = Data_Train.shape[1]
    print(nScan, nChan)


    mypca = PCA()
    mypca.fit(Data_Train)
    data = mypca.transform(Data_Train)

    # pre_clm = RFClass(data[0:nScan*2/3], CLM[0:nScan*2/3], data[nScan*2/3:], CLM[nScan*2/3:])
    pre_clm = SVMClass(data[0:nScan*2/3], CLM[0:nScan*2/3], data[nScan*2/3:], CLM[nScan*2/3:])
    # pre = RFClass(Data_Train[0:nScan/2], CLM[0:nScan/2], Data_Train[nScan/2:])
    # pre_clm = RFClass(Data_Train[nScan/2:], CLM[nScan/2:], Data_Train[0:nScan/2])

    diff = pre_clm - CLM[nScan*2/3:]
    diff = list(diff)
    print diff.count(0)

    WriteHDF(outfile, 'pca', data, 1)
    WriteHDF(outfile, 'CLM_pre', pre_clm, 0)
    WriteHDF(outfile, 'diff', diff, 0)
    WriteHDF(outfile, 'CLM_MERSI', CLM[nScan*2/3:], 0)
    WriteHDF(outfile, 'Latitude', sounding_latitude[nScan*2/3:], 0)
    WriteHDF(outfile, 'Longitude', sounding_longitude[nScan*2/3:], 0)

    # for iscan in range(nScan):
    #     for ipix in range(nPix):
    #         if sounding_qual_flag[iscan] =









