#coding:utf-8
import numpy as np
import os
import h5py
import sys
from sklearn.ensemble import RandomForestClassifier
from HDFProcess import *
from sklearn import preprocessing
from sklearn.feature_selection import SelectFromModel


def JustForTest():
    from sklearn.datasets import make_classification
    x, y = make_classification(n_samples=1000, n_features=10,
                              n_informative=2, n_redundant=0,
                               random_state=0, shuffle=False)
    print x, y
    clf = RandomForestClassifier()
    clf.fit(x, y)
    #data = clf.predict([[1,2,1,2]])

    print clf.n_outputs_
    print clf.classes_
    print clf.n_classes_
    print 'n_features_:',clf.n_features_
    print 'feature_importances_:',clf.feature_importances_
    print 'oob_score:', clf.oob_score
    # print clf.oob_decision_function_


def DecTreeClass(Data_r, Data_a):
    Data_Train = Data_r[0:200]
    Data_Target = Data_a[0:200]

    Data_Test= Data_r[200:]
    clf = RandomForestClassifier(n_estimators=50,
                               # warm_start=True,
                                oob_score=True,
                               max_features="sqrt")
    clf = clf.fit(Data_Train, Data_Target)

    model = SelectFromModel(clf, prefit=True)
    x = model.transform(Data_Train)

    pre = clf.predict(Data_Test)
    print 'x.shape:',x.shape

    print 'n_outputs_',clf.n_outputs_
    print 'classes_',clf.classes_
    print 'n_classes_:',clf.n_classes_
    print 'n_features_:',clf.n_features_
    print 'feature_importances_:',clf.feature_importances_
    print 'oob_score:', clf.oob_score
    print 'oob_score:', clf.oob_score_
    print clf.score(Data_Test, pre)
    print pre
    print Data_a[200:] - pre

def Run(filename=None):
    Data_radiance_o2 = ReadHDF(filename, '/SoundingMeasurements/radiance_o2')

    Data_radiance_o2 = np.array(Data_radiance_o2)

    print(Data_radiance_o2.shape)

    nScan =Data_radiance_o2.shape[0]
    nPix = Data_radiance_o2.shape[1]
    nChan = Data_radiance_o2.shape[2]

    # Data_Train = Data_radiance_o2.reshape((nScan*nPix, nChan))

    Data_Train = []
    Data_Target = []
    for iscan in range(500,600):
        for ipix in range(3,7):
            data1= []
            tempdata = np.array(Data_radiance_o2[iscan, ipix, :])
            # tempdata = preprocessing.scale(tempdata)
            flag = (tempdata<=0)
            if True in flag:
                continue

            data1.extend(tempdata[19:59])
            data1.extend(tempdata[ 79:109])
            data1.extend(tempdata[ 749:769])
            data1.extend(tempdata[899:979])
            data1.extend(tempdata[1054:1119])
            Data_Train.append(data1)
            Data_Target.append(ipix)
    # Data_Train = preprocessing.scale(Data_Train)
    # poly = preprocessing.PolynomialFeatures(interaction_only=True)
    # Data_Train = poly.fit_transform(Data_Train)
    Data_Train = np.array(Data_Train)
    print Data_Train.shape

    # Data_Target = np.zeros(Data_Train.shape[0])

    DecTreeClass(Data_Train, Data_Target)

if __name__ == '__main__':
    # JustForTest()
    filename = r'G:\PythonPro\TanSat\python\Data\L1\TanSat_ACGS_1B_SCI_TG_2X2KM_ORBT_07649_20180531_0441_V02_170419.h5'

    Run(filename)


