"""PS25 figure using the shared journal style and selected two-tier layout."""
import argparse
import csv
import sys
from pathlib import Path
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator,FuncFormatter,NullFormatter,LogLocator

DATA=Path(__file__).resolve().parent
sys.path.insert(0, str(DATA.parent / 'scripts'))
from cosmology_plot_style import (
    JOURNAL_COLORS, apply_journal_style, format_axes, format_redshift, panel_label,
)

apply_journal_style()
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
models=['pl','kp1','kp10']; markers=['o','^','s']
labels=['PL',r'BT $k_p=1$',r'BT $k_p=10$']
limits=[(.97,1.28),(.97,1.60),(.97,2.12),(.9,5.5)]
ticks=[[1,1.1,1.2],[1,1.2,1.4,1.6],[1,1.5,2],[1,2,3,4,5]]

colors=[JOURNAL_COLORS[name] for name in ['black','blue','green']]
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
        format_axes(ax)
    p.set_yscale('log');p.yaxis.set_minor_formatter(NullFormatter())
    for j,m in enumerate(models):
        xy=np.array(sorted(spec[m,round(z,3)]))
        p.plot(xy[:,0],xy[:,1],color=colors[j],
               ls=['-','-','--'][j],marker=markers[j],markevery=(j*2,11),
               mfc='white',mew=.8,zorder=3-j*.1)
        if m!='pl':
            xy=np.array(sorted(rat[m,round(z,3)]))
            r.plot(xy[:,0],xy[:,1],color=colors[j],
                   ls='-' if j==1 else '--',marker=markers[j],
                   markevery=(j*2,12),mfc='white',mew=.8)
    allp=[v for m in models for k,v in spec[m,round(z,3)]]
    p.set_ylim(min(allp)/1.3,max(allp)*1.55)
    panel_label(p, rf'$z={format_redshift(z)}$', loc=(.94,.90),
                ha='right', fontsize=plt.rcParams['axes.titlesize'])
    p.tick_params(labelbottom=False)
    r.set_ylim(*limits[i]);r.yaxis.set_major_locator(FixedLocator(ticks[i]))
    r.yaxis.set_major_formatter(FuncFormatter(lambda v,_:f'{v:g}'))
    r.axhline(1,color='.45',lw=.9,ls=':',zorder=0)
    r.set_xlabel(r'$k\ [h\,\mathrm{Mpc}^{-1}]$',labelpad=3)
    if i%2==0:p.set_ylabel(r'$P(k)\ [h^{-3}\,\mathrm{Mpc}^{3}]$',labelpad=5)
    r.set_ylabel('BT / PL',labelpad=5)
    # Keep every local ratio scale visible: ranges differ between epochs.
    r.grid(axis='y',color='0.88',lw=.5,zorder=0)
handles=[Line2D([],[],color=c,marker=m,ls=['-','-','--'][j],
                mfc='white',mew=.8,label=l)
         for j,(c,m,l) in enumerate(zip(colors,markers,labels))]
fig.legend(handles=handles,loc='upper center',ncol=3,frameon=False,
           bbox_to_anchor=(.54,.991),columnspacing=2.8)
fig.savefig(OUT)
plt.close(fig)
print('saved',OUT)
