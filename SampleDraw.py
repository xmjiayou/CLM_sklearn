#coding:utf-8
import h5py
import os
import numpy as np
import matplotlib.pyplot as plt
from HDFProcess import *

wavefile = r'G:\PythonPro\TanSat\CLMofMachinLearn\wavelength.HDF'

color = ['#6495ed', '#006400', '#f0e68c', '#ff0000', '#cd5c5c', '#ff4500', '#ee82ee', '#3cb371', '#ffd700']

def Draw():
    fig = plt.figure(figsize=(8,6))


def Main(filename):
    # get O2 channel center wave length
    # 9*1242
    o2wavelength = ReadHDF(wavefile, 'o2')

    # get file O2 radiace
    radiance_o2 = ReadHDF(filename, 'radiance_o2')
    sounding_id = ReadHDF(filename, 'sounding_id')

    index = sounding_id % 10

    return radiance_o2, o2wavelength[index-1], index

landmask = ['lake', 'city', 'beach', 'ice', 'vegetation', 'desert', 'sea']
CLMtype = ['clear', 'cloud']
handletype = ['all', 'point']

def clearAndcloud(fils):

    for itype in handletype:
        print itype
        flag = 0

        for iland in landmask:
            fig = plt.figure(figsize=(8,4))
            flag += 1
            for filename in fils:
                for iclm in CLMtype:
                    if iland in filename and iclm in filename:
                        print(filename)
                        guangpu, wave, index = Main(os.path.join(pathin, filename))
                        if itype == 'all':
                            for i in range(wave.shape[0]):
                                if iclm == 'clear':
                                    plt.plot(wave[i], guangpu[i], 'b-', lw=0.7, label= '%s_%s_%d' %(iland, iclm, flag))
                                    #pass
                                else:
                                    plt.plot(wave[i], guangpu[i], 'g-', lw=0.7, label= '%s_%s_%d' %(iland, iclm, flag))
                        else:
                            for i in range(1):
                                if iclm == 'clear':
                                    plt.plot(wave[i], guangpu[i], 'b-', lw=0.7, label= '%s_%s_%d' %(iland, iclm, flag))
                                    #pass
                                else:
                                    plt.plot(wave[i], guangpu[i], 'g-', lw=0.7, label= '%s_%s_%d' %(iland, iclm, flag))

            if itype == 'all':
                # plt.legend()
                plt.title(iland)
                plt.grid(linestyle='-.')
                plt.xlim(755, 780)
                plt.savefig(os.path.join(r'G:\PythonPro\TanSat\DATA\sample\IMAGE', iland + itype +'name.png'), dpi = 200, bbox_inches = 'tight')
                # plt.show()
                plt.close()
            else:
                plt.title(iland)
                plt.legend()
                plt.grid(linestyle='-.')
                plt.xlim(755, 780)
                plt.savefig(os.path.join(r'G:\PythonPro\TanSat\DATA\sample\IMAGE', iland + itype +'name.png'), dpi = 200, bbox_inches = 'tight')
                # plt.show()
                plt.close()
        fig.clear()

def singletype(fils):
    for iclm in CLMtype:
        flag = 0
        for iland in landmask:
            fig = plt.figure(figsize=(8,4))
            flag += 1
            for filename in fils:
                if iland in filename and iclm in filename:
                    print(filename)
                    guangpu, wave, index = Main(os.path.join(pathin, filename))
                    for i in range(wave.shape[0]):
                        # if index[i] != 4:
                        #     continue

                        if iclm == 'clear':
                            plt.plot(wave[i], guangpu[i], linestyle='-', color=color[index[i]-1], lw=0.7, label= '%s_%s_%d' %(iland, iclm, flag))
                        else:
                            plt.plot(wave[i], guangpu[i], linestyle='-', color=color[index[i]-1], lw=0.7, label= '%s_%s_%d' %(iland, iclm, flag))

        plt.title(iclm)
        plt.grid(linestyle='-.')
        plt.xlim(755, 780)
        plt.savefig(os.path.join(r'G:\PythonPro\TanSat\DATA\sample\IMAGE', iclm +'.png'), dpi = 200, bbox_inches = 'tight')
        # plt.show()
        plt.close()
        fig.clear()

if __name__ == '__main__':
    pathin = r'G:\PythonPro\TanSat\DATA\sample'

    fils = os.listdir(pathin)

    # clearAndcloud(fils)
    singletype(fils)












