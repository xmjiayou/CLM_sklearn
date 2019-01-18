#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import numpy as np
import sys
import getopt
import h5py as h5
import re
import multiprocessing  
from multiprocessing import Pool
from glob import glob
import time
import os
import imlib




execpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(execpath+os.sep+'ini')
sys.path.append(execpath+os.sep+'server')
from sysinfo import (sys_ini)
from tools import *

FillValue=-1
T=0
B=0
L=0
W=0
H=0
dpp=0

def getcldtime(mersifile):
    reg_l1='.*FY3D_MERSI_ORBT_L2_CLM_MLT_NUL_(\d{8}_\d{4})_.*'
    l1_pattern=re.compile(reg_l1)
    match=l1_pattern.match(mersifile)
    if match:
        tm=match.group(1)
        dt=datetime.strptime(tm,'%Y%m%d_%H%M')
        dt=np.datetime64(dt)
    else:
        print 'mersi file not match time'
    return dt

def clmtogeo(cldfile):
	#geopath='/PRDDATA_NFS/D1BDATA/FY3D/MERSI_bak'
	geopath='/TANPGS/TanOnLine/D1BDATA/FY3D/MERSI'
	geofile=os.path.basename(cldfile)
	geofile=geofile.replace('_ORBT_L2_CLM_MLT_NUL_','_GBAL_L1_')
	geofile=geofile.replace('_1000M_','_GEO1K_')
	return geopath+os.sep+geofile



def findcldfile(l1file,cldpath):
	l1time=getl1time(l1file)
	if l1time==None:
		return l1time
	reg_cld='FY3D_MERSI_ORBT_L2_CLM_MLT_NUL_'+l1time.strftime('%Y%m%d')+'_*HDF'
	cld_lst=[]
	for file in glob(cldpath+reg_cld):
		cld_lst.append(file)

	return cld_lst

def CYL_UV(x, y):
    f = x > -180
    f &= x < 360
    x -= L  # left
    x[x < 0] += 360
    y -= B  # bottom
    f &= y >= 0
    f &= y < H  # height
    f &= x < W  # width
    y = H - y  # for basemap-imshow disable this line
    x *= dpp
    y *= dpp
    return x.astype('u2'), y.astype('u2'), f

def mkGird(dpp):
    pp = np.empty((int(H * dpp), int(W * dpp)), "f4")
    pp.fill(FillValue)
    return pp

l1time=0
def comp(file):
	cld_tm=getcldtime(file)
	tansat_mersi_tm=cld_tm-l1time
	tansat_mersi_tm=abs(tansat_mersi_tm.item().total_seconds())
	return tansat_mersi_tm

	

def main():
	global T,B,L,W,H,dpp,l1time
	time_start = time.time()
	argv=None

	extend=2
	resolve=0.01
	try:
		if argv is None:
			argv=sys.argv

		opts,arg = getopt.getopt(argv[1:], "h",
								   ["tanl1=","argv="])


		# 检测参数是否完整
		args=dict(opts)
		print "\033[32m*-*-*-*-*-*-*-*-*-\n>Options:"
		for key,value in args.iteritems():
			print '%10s: %s'  % (key.strip('-').upper(),value)
		print ">ARGS:"
		for i in arg:
			print i
		print "*-*-*-*-*-*-*-*-*-\033[0m"

		if '--tanl1' in args :  
			l1file=args['--tanl1'].strip()

		if '--argv' in args:
			l1file=getl1file(args['--argv'],)

		#configure file
		sys_ini_file=execpath+'/conf/SYS.ini'
		sys_ini(sys_ini_file)

		l1time=getl1time(l1file)
		ymd=l1time.strftime('%Y%m%d')
		l1time=np.datetime64(l1time)
		cldpath=sys_ini().sys['MERSI_CLOUD']+os.sep
		clmpath=sys_ini().sys['CLM_ROOT']+os.sep+ymd
		if not os.path.exists(clmpath):
			os.makedirs(clmpath,0777)
		clmname=os.path.basename(l1file).split('.')[0]+'.cld'
		output=clmpath+os.sep+clmname
		print '+'*100
		print 'l1=',l1file
		print 'clm=',output
		print '-'*100
		#find cld file
		cld_lst=findcldfile(l1file,cldpath)
		print cld_lst
		cld_lst=sorted(cld_lst,reverse=True,key=lambda file:comp(file))
		if len(cld_lst)==0:
			print 'l1=',l1file,'not find cloud file'
			os._exit(0)
		print cld_lst
		#open L1 file
		l1=h5.File(l1file,'r')
		soundings=l1['SoundingGeometry/sounding_id'].value
		l1_lat=l1['SoundingGeometry/sounding_latitude'].value
		clr_lat=l1_lat[l1_lat<9999.9]
		l1_lat_max=clr_lat.max()+extend
		l1_lat_min=clr_lat.min()-extend
		l1_lon=l1['SoundingGeometry/sounding_longitude'].value
		clr_lon=l1_lon[l1_lon<9999.9]
		l1_lon_max=clr_lon.max()+extend
		l1_lon_min=clr_lon.min()-extend
		w=int(abs(l1_lon_max-l1_lon_min))
		h=int(abs(l1_lat_max-l1_lat_min))
		print '++++++++ w=',w,'++++++++ h=',h
		T=l1_lat_max
		L=l1_lon_min
		W=w
		H=h
		B=T-H
		dpp=1/resolve
		x,y=l1_lat.shape
		l1_time=l1['SoundingGeometry/sounding_time_J2012'].value
		l1_time=l1_time[l1_time>0]
		stime=l1_time[0].astype(int)
		etime=l1_time[-1].astype(int)
		t1970_2012=np.datetime64('2012-01-01','s').astype(int)-np.datetime64('1970-01-01','s').astype(int)
		stime=np.datetime64(stime+t1970_2012,'s')
		etime=np.datetime64(etime+t1970_2012,'s')
		l1_mask=np.zeros([x,y],dtype=int)
		grid_mask=mkGird(1/resolve)
		grid_cur=mkGird(1/resolve)
		time_start = time.time()
		find=0
		nofind=0
		for cldfile in cld_lst:
			#get mersi tm
			cld_tm=getcldtime(cldfile)
			#stime-cld_tm
			tansat_mersi_tm=cld_tm-stime
			tansat_mersi_tm=abs(tansat_mersi_tm.item().total_seconds())
			#etime-cld_tm
			if tansat_mersi_tm>3600:
				continue
			tansat_mersi_tm=cld_tm-etime
			tansat_mersi_tm=abs(tansat_mersi_tm.item().total_seconds())
			if tansat_mersi_tm>3600:
				continue
			cld=h5.File(cldfile,'r')
			cld_mask=cld['Cloud_Mask'].value
			cld_mask=cld_mask[0]
			cld_mask=cld_mask & 0x06
			cld_mask=cld_mask/2

			cld_geo_file=clmtogeo(cldfile)
			cld_geo=h5.File(cld_geo_file,'r')
			#find mersi 1km geo
			cld_lat=cld_geo['Geolocation/Latitude'].value
			cld_lon=cld_geo['Geolocation/Longitude'].value
			u,v,f=CYL_UV(cld_lon,cld_lat)
			imlib.lproj(cld_mask.astype('f4')[f],u[f],v[f],grid_mask)
			
			cld.close()
			cld_geo.close()
			find=find+1
			cld_end = time.time()
		if find>1:
			imlib.Nfill(grid_mask, 3, -1)

			x,y=l1_lat.shape 
			u,v,f=CYL_UV(l1_lon.copy(),l1_lat.copy())
			for i in range(0,x):
				for j in range(0,y):
					if f[i,j]:
						l1_mask[i,j]=int(grid_mask[v[i,j],u[i,j]])


			np.savetxt(output,l1_mask)
			l1.close()
			clmpath=sys_ini().sys['CLM_ROOT']+os.sep+ymd
			clmname=os.path.basename(l1file).split('.')[0]+'.hdf'
			output=clmpath+os.sep+clmname
			print 'out clm=',output
			h=h5.File(output,'w')
			h['lat']=l1_lat
			h['lon']=l1_lon
			h['mask']=l1_mask
			h.close()
		time_end = time.time()
		print time_end - time_start," s"
	except BaseException,err:
		logging.exception(err)
	finally:
		pass
	return 0

if __name__=='__main__':
    main()
	