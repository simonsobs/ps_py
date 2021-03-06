"""
    This script is used for producing the figure of the paper displaying the stacked correlation coefficient of the Planck data
    To run it: python plot_planck_results_stacked.py global.dict
"""

import numpy as np
import pylab as plt
from pspy import so_dict,so_spectra,pspy_utils
import os,sys
import planck_utils
import matplotlib as mpl
label_size = 14
mpl.rcParams['xtick.labelsize'] = label_size
mpl.rcParams['ytick.labelsize'] = label_size


d = so_dict.so_dict()
d.read_from_file(sys.argv[1])


figure_dir='figures'
pspy_utils.create_directory(figure_dir)


spectraDir='spectra'

if d['use_ffp10']==True:
    mc_dir='monteCarlo_ffp10'
    plot_name='all_cross_ffp10'
else:
    mc_dir='monteCarlo'
    plot_name='all_cross'


spectra=['TT','TE','TB','ET','BT','EE','EB','BE','BB']
binning_file=d['binning_file']
freqs=d['freqs']
lthmax=1500

freq_pairs=[]
for c1,freq1 in enumerate(freqs):
    for c2,freq2 in enumerate(freqs):
        if c1>c2: continue
        freq_pairs+=[[freq1,freq2]]


clth={}
fg={}

lth,cl_TT,cl_TE,cl_EE,cl_BB,cl_PP=np.loadtxt('theory_file/base_plikHM_TTTEEE_lowl_lowE_lensing.minimum.theory_cl',unpack=True)
clth['TT']=cl_TT[:lthmax]
clth['TE']=cl_TE[:lthmax]
clth['EE']=cl_EE[:lthmax]

lth,fg['TT','100x100'],fg['TT','143x143'],fg['TT','143x217'],fg['TT','217x217'],fg['EE','100x100'],fg['EE','100x143'],fg['EE','100x217'],fg['EE','143x143'],fg['EE','143x217'],fg['EE','217x217'],fg['TE','100x100'],fg['TE','100x143'],fg['TE','100x217'],fg['TE','143x143'],fg['TE','143x217'],fg['TE','217x217']=np.loadtxt('theory_file/base_plikHM_TTTEEE_lowl_lowE_lensing.minimum.plik_foregrounds',unpack=True)


lth=lth[:lthmax]

cl_th_and_fg={}
cb_th_and_fg={}
mean={}
std={}
bias_r_th={}

for f in freq_pairs:
    f0,f1=f[0],f[1]
    fname='%sx%s'%(f0,f1)
    lmin,lmax=d['lrange_%sx%s'%(f0,f1)]

    for spec in ['TT','EE','TE','r']:

        if spec != 'r':
            if (fname !='100x143') & (fname !='100x217'):
                cl_th_and_fg[spec,fname]=(clth[spec]+fg[spec,fname][:lthmax])*2*np.pi/(lth*(lth+1))
            else:
                cl_th_and_fg[spec,fname]=clth[spec]*2*np.pi/(lth*(lth+1))
            
            lb,cb_th_and_fg[spec,fname]= planck_utils.binning(lth, cl_th_and_fg[spec,fname],lthmax,binning_file=binning_file)
            id=np.where((lb>lmin) &(lb<lmax))

            cb_th_and_fg[spec,fname]=cb_th_and_fg[spec,fname][id]
        else:
            cl_th_and_fg[spec,fname]=cl_th_and_fg['TE',fname]/np.sqrt(cl_th_and_fg['TT',fname]*cl_th_and_fg['EE',fname])
            cb_th_and_fg[spec,fname]=cb_th_and_fg['TE',fname]/np.sqrt(cb_th_and_fg['TT',fname]*cb_th_and_fg['EE',fname])

        l,mean[spec,fname],std[spec,fname]=np.loadtxt('%s/spectra_%s_%s_hm1xhm2.dat'%(mc_dir,spec,fname),unpack=True)

    cov_TTTT=np.loadtxt('%s/diagonal_select_cov_mat_TT_%s_%s_TT_%s_%s.dat'%(mc_dir,fname,'hm1xhm2',fname,'hm1xhm2'))
    cov_EEEE=np.loadtxt('%s/diagonal_select_cov_mat_EE_%s_%s_EE_%s_%s.dat'%(mc_dir,fname,'hm1xhm2',fname,'hm1xhm2'))
    cov_TETE=np.loadtxt('%s/diagonal_select_cov_mat_TE_%s_%s_TE_%s_%s.dat'%(mc_dir,fname,'hm1xhm2',fname,'hm1xhm2'))

    cov_TTEE=np.loadtxt('%s/diagonal_select_cov_mat_TT_%s_%s_EE_%s_%s.dat'%(mc_dir,fname,'hm1xhm2',fname,'hm1xhm2'))
    cov_TTTE=np.loadtxt('%s/diagonal_select_cov_mat_TT_%s_%s_TE_%s_%s.dat'%(mc_dir,fname,'hm1xhm2',fname,'hm1xhm2'))
    cov_EETE=np.loadtxt('%s/diagonal_select_cov_mat_EE_%s_%s_TE_%s_%s.dat'%(mc_dir,fname,'hm1xhm2',fname,'hm1xhm2'))

    bias_r_th[fname]=3./8*(cov_EEEE/(mean['EE',fname])**2+ cov_TTTT/(mean['TT',fname])**2)
    bias_r_th[fname]+=1./4*cov_TTEE/(mean['EE',fname]*mean['TT',fname])
    bias_r_th[fname]-=1./2*(cov_TTTE/(mean['TE',fname]*mean['TT',fname])+ cov_EETE/(mean['TE',fname]*mean['EE',fname]))
    bias_r_th[fname]*=mean['r',fname]



color_array=['red','gray','orange','blue','green','purple']

plt.figure(figsize=(16,14))
count=0
for c,f in zip(color_array,freq_pairs):
    f0,f1=f[0],f[1]
    fname='%sx%s'%(f0,f1)

    lmin,lmax=d['lrange_%sx%s'%(f0,f1)]

    spec_name='Planck_%sxPlanck_%s-%sx%s'%(f0,f1,'hm1','hm2')
    file_name= '%s/spectra_%s.dat'%(spectraDir,spec_name)
    lb,Db_dict=so_spectra.read_ps(file_name,spectra=spectra)

    id=np.where((lb>lmin) &(lb<lmax))

    Db_dict['TE']=(Db_dict['TE']+Db_dict['ET'])/2
    if f0 != f1:
        spec_name2='Planck_%sxPlanck_%s-%sx%s'%(f0,f1,'hm2','hm1')
        file_name2= '%s/spectra_%s.dat'%(spectraDir,spec_name2)
        lb,Db_dict2=so_spectra.read_ps(file_name2,spectra=spectra)
        Db_dict2['TE']=(Db_dict2['TE']+Db_dict2['ET'])/2
        Db_dict['TE']=(Db_dict['TE']+Db_dict2['TE'])/2

    lb=lb[id]

    r=Db_dict['TE'][id]/np.sqrt(Db_dict['TT'][id]*Db_dict['EE'][id])
    r-= bias_r_th[fname]


#    plt.plot(lb,mean['r',fname],color='black')
    plt.ylabel(r'${\cal R}^{\rm TE, c}_{\ell}$',fontsize=30)
    plt.xlabel(r'$\ell$',fontsize=30)

    plt.errorbar(lb,r,std['r',fname],label='%s'%(fname),color=c,fmt='.')
    if (fname !='100x143') & (fname !='100x217'):
        plt.errorbar(lb,cb_th_and_fg['r',fname],color=c,alpha=0.3,label='Planck best fit (binned)')

plt.legend(frameon=False,fontsize=15)
plt.savefig('%s/%s.pdf'%(figure_dir,plot_name),bbox_inches='tight')
plt.clf()
plt.close()




color_array=['red','blue','green','purple']
freq_pairs=[[100,100],[143,143],[143,217],[217,217]]
plt.figure(figsize=(16,14))
count=0
for c,f in zip(color_array,freq_pairs):
    f0,f1=f[0],f[1]
    fname='%sx%s'%(f0,f1)
    
    lmin,lmax=d['lrange_%sx%s'%(f0,f1)]
    
    spec_name='Planck_%sxPlanck_%s-%sx%s'%(f0,f1,'hm1','hm2')
    file_name= '%s/spectra_%s.dat'%(spectraDir,spec_name)
    lb,Db_dict=so_spectra.read_ps(file_name,spectra=spectra)
    
    id=np.where((lb>lmin) &(lb<lmax))
    
    Db_dict['TE']=(Db_dict['TE']+Db_dict['ET'])/2
    if f0 != f1:
        spec_name2='Planck_%sxPlanck_%s-%sx%s'%(f0,f1,'hm2','hm1')
        file_name2= '%s/spectra_%s.dat'%(spectraDir,spec_name2)
        lb,Db_dict2=so_spectra.read_ps(file_name2,spectra=spectra)
        Db_dict2['TE']=(Db_dict2['TE']+Db_dict2['ET'])/2
        Db_dict['TE']=(Db_dict['TE']+Db_dict2['TE'])/2

    lb=lb[id]

    r=Db_dict['TE'][id]/np.sqrt(Db_dict['TT'][id]*Db_dict['EE'][id])
    r-= bias_r_th[fname]


#    plt.plot(lb,mean['r',fname],color='black')
    plt.ylabel(r'${\Delta \cal R}^{\rm TE, c}_{\ell}$',fontsize=30)
    plt.xlabel(r'$\ell$',fontsize=30)

    plt.errorbar(lb-6+count*3,r-cb_th_and_fg['r',fname],std['r',fname],label='%s'%(fname),color=c,fmt='.',alpha=0.3)
    plt.plot(lb,lb*0,color='grey')
    count+=1
plt.legend(frameon=False,fontsize=15)
plt.savefig('%s/test.pdf'%(figure_dir),bbox_inches='tight')
plt.clf()
plt.close()



