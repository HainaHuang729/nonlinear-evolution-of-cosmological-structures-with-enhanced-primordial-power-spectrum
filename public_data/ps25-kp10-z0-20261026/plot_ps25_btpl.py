"""Selected thin-line PS25 layout; all released samples retained, no smoothing."""
import argparse
import csv
from pathlib import Path
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator,FuncFormatter,NullFormatter,LogLocator

DATA=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,default=DATA.parents[1]/'power-spectrum-btpl.png')
OUT=parser.parse_args().output
OUT.parent.mkdir(parents=True,exist_ok=True)
zs=[0,1.0717968600643704,3.4410805658271204,8.519850605215494]
spec=defaultdict(list);rat=defaultdict(list)
for row in csv.DictReader((DATA/'spectra.csv').open()):
    if int(row['displayed']):spec[row['model'],round(float(row['redshift']),3)].append((float(row['k_hMpc']),float(row['P_sim'])))
for row in csv.DictReader((DATA/'ratios.csv').open()):
    rat[row['model'],round(float(row['redshift']),3)].append((float(row['k_hMpc']),float(row['BT_over_PL'])))
plt.rcParams.update({'font.family':'STIXGeneral','mathtext.fontset':'stix',
                     'font.size':10,'axes.labelsize':11,'axes.linewidth':.85,
                     'xtick.labelsize':9,'ytick.labelsize':9,
                     'xtick.direction':'in','ytick.direction':'in','pdf.fonttype':42})
models=['pl','kp1','kp10']; markers=['o','^','s']
labels=['PL',r'BT $k_p=1$',r'BT $k_p=10$']
limits=[(.97,1.28),(.97,1.60),(.97,2.12),(.9,5.5)]
ticks=[[1,1.1,1.2],[1,1.2,1.4,1.6],[1,1.5,2],[1,2,3,4,5]]

colors=['#000000','#0072B2','#009E73']
fig=plt.figure(figsize=(7.8,6.45))
outer=fig.add_gridspec(2,2,left=.095,right=.982,bottom=.083,top=.925,
                      hspace=.27,wspace=.23)
pairs=[]
for i,z in enumerate(zs):
    sub=outer[i//2,i%2].subgridspec(2,1,height_ratios=[2.7,1],hspace=.045)
    p=fig.add_subplot(sub[0]);r=fig.add_subplot(sub[1],sharex=p);pairs.append((p,r))
    for ax in (p,r):
        ax.set_xscale('log');ax.set_xlim(2.4,33.5)
        ax.xaxis.set_major_locator(FixedLocator([3,5,10,20,30]))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v,_:f'{v:g}'))
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.tick_params(which='both',top=True,right=True)
        ax.tick_params(which='major',length=4,width=.85,pad=3)
        ax.tick_params(which='minor',length=2,width=.65)
    p.set_yscale('log');p.yaxis.set_minor_formatter(NullFormatter())
    for j,m in enumerate(models):
        xy=np.array(sorted(spec[m,round(z,3)]))
        p.plot(xy[:,0],xy[:,1],color=colors[j],lw=1.25,
               ls=['-','-','--'][j],marker=markers[j],markevery=(j*2,11),
               ms=3,mfc='white',mew=.7,zorder=3-j*.1)
        if m!='pl':
            xy=np.array(sorted(rat[m,round(z,3)]))
            r.plot(xy[:,0],xy[:,1],color=colors[j],lw=1.05,
                   ls='-' if j==1 else '--',marker=markers[j],
                   markevery=(j*2,12),ms=2.5,mfc='white',mew=.65)
    allp=[v for m in models for k,v in spec[m,round(z,3)]]
    p.set_ylim(min(allp)/1.3,max(allp)*1.55)
    p.text(.94,.90,rf'$z={z:.2f}$',transform=p.transAxes,ha='right',va='top',fontsize=12)
    p.tick_params(labelbottom=False)
    r.set_ylim(*limits[i]);r.yaxis.set_major_locator(FixedLocator(ticks[i]))
    r.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f'{v:g}'))
    r.axhline(1,color='.50',lw=.65,ls=':',zorder=0)
    r.set_xlabel(r'$k\ [h\,\mathrm{Mpc}^{-1}]$',labelpad=3)
    if i%2==0:p.set_ylabel(r'$P(k)\ [h^{-3}\,\mathrm{Mpc}^{3}]$',labelpad=5)
    r.set_ylabel('BT / PL',labelpad=5)
    # Keep every local ratio scale visible: ranges differ between epochs.
    r.grid(axis='y',color='#E5E7EA',lw=.45,zorder=0)
handles=[Line2D([],[],color=c,marker=m,ls=['-','-','--'][j],
                lw=1.25,ms=4,mfc='white',mew=.8,label=l)
         for j,(c,m,l) in enumerate(zip(colors,markers,labels))]
fig.legend(handles=handles,loc='upper center',ncol=3,frameon=False,
           bbox_to_anchor=(.54,.991),fontsize=10.5,columnspacing=2.8,handlelength=2)
fig.savefig(OUT,dpi=300)
plt.close(fig)
print('saved',OUT)
