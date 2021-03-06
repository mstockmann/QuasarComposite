# -*- coding: utf-8 -*-
"""
Short script to plot the accuracy of the optimal template for the telluric correction
"""
# from matplotlib import rc_file
# rc_file('/Users/jselsing/Pythonlibs/plotting/matplotlibstyle.rc')
# import matplotlib
# matplotlib.use('cairo')

import numpy as np
import glob
import matplotlib.pylab as pl
import seaborn as sns; sns.set_style('ticks')
# cmap = sns.cubehelix_palette(n_colors=6, start=0.0, rot=1.5, gamma=1.0, hue=1.0, light=0.85, dark=0.15, reverse=True, as_cmap=False)
cmap = sns.color_palette("cubehelix", 3)

import matplotlib

from methods import latexify, format_axes, gauss

from gen_methods import medfilt, smooth
def hist(rawData,xRange,nBins=10,mode='lin'):

    """histogram using linear binning of supplied data

    Input:
    rawData	-- list containing data to be binned
    xRange  -- lower(incl)/upper(excl) boundary for numerical values
    nBin    -- desired number of bins (default =10)
    mode	-- binning type (possible choices: lin, log)

    Returns: (nothing)
    """
    from math   import sqrt,floor,log,exp
    h = [0]*nBins
    xMin=float(xRange[0])
    xMax=float(xRange[1])

    if mode == 'lin':
        dx = (xMax-xMin)/nBins
        def binId(val):   return int(floor((val-xMin)/dx))
        def bdry(bin):	  return xMin+bin*dx, xMin+(bin+1)*dx
        def GErr(q,n,dx): return sqrt(q*(1-q)/(N-1))/dx

    elif mode == 'log':
        dx = log(xMax/xMin)/nBins
        def binId(val):   return int(floor(log(val/xMin)/dx))
        def bdry(bin):	  return xMin*exp(bin*dx), xMin*exp((bin+1)*dx)
        def GErr(q,n,dx): return "##"

    for value in rawData:
        if 0<=binId(value)<nBins:
          h[binId(value)] += 1

    N=sum(h)
    binned = []
    for bin in range(nBins):
        hRel   = float(h[bin])/N
        low,up = bdry(bin)
        binned.append(low)
        width  = up-low
        # print(low, up, hRel/width, GErr(hRel,N,width))
    return binned






def inter_arm_cut(wl_arr = [] ,flux_arr = [], fluxerr_arr=[], transmission_arr=[], i_arr= []):
    wl = 0
    flux = 0
    fluxerr = 0
    transmission = 0

    #Reformat
    if i_arr == 'UVB':
        wl = wl_arr[(3100 < wl_arr) & (wl_arr < 5550)]
        flux = flux_arr[(3100 < wl_arr) & (wl_arr < 5550)]
        fluxerr = fluxerr_arr[(3100 < wl_arr) & (wl_arr < 5550)]
        transmission = transmission_arr[(3100 < wl_arr) & (wl_arr < 5550)]
    
    if i_arr == 'VIS':
        wl = wl_arr[(5550 < wl_arr) & (wl_arr < 10100)]
        flux = flux_arr[(5550 < wl_arr) & (wl_arr < 10100)]
        fluxerr = fluxerr_arr[(5550 < wl_arr) & (wl_arr < 10100)]
        transmission = transmission_arr[(5550 < wl_arr) & (wl_arr < 10100)]
        
    if i_arr == 'NIR':
        upper = 30700
        lower = 10100
        wl = wl_arr[(lower< wl_arr) & (wl_arr < upper)]
        flux = flux_arr[(lower < wl_arr) & (wl_arr < upper)]
        fluxerr = fluxerr_arr[(lower < wl_arr) & (wl_arr < upper)]
        transmission = transmission_arr[(lower < wl_arr) & (wl_arr < upper)]
        
    return wl, flux, fluxerr, transmission








if __name__ == '__main__':
    ratio = (1.0 + np.sqrt(5.0))/2.0
    # latexify(figsize=(5*ratio, 5))
    # latexify(fig_width=5*ratio, fig_height=5)
    latexify(columns=2)
    fig, ax = pl.subplots()

    # fig.subplots_adjust(left=0.1, right=0.95, bottom=0.1, top=0.95)
    # ax = fig.add_subplot(111)


    root_dir = '/Users/jselsing/Work/X-Shooter/CompositeRedQuasar/processed_data/'
    sdssobjects = glob.glob(root_dir+'*SDSS1431*/')
        # obj_list =   [ 'SDSS0820+1306', 'SDSS1150-0023', 'SDSS1219-0100', 'SDSS1236-0331' , 'SDSS1354-0013',
        #            'SDSS1431+0535', 'SDSS1437-0147']
    print(sdssobjects)
    arms = ['UVB', 'VIS', 'NIR']
    arms = ['fdg']
    for i in sdssobjects:
        # print(i)
        obs = glob.glob(i+'*corrected*')
        obs_check = glob.glob((i + '*uncorrected_science*'))
        # print(obs)
        obj_name = i[-14:-1]

        # fig = None

        if obs != []:
            for n in arms:
#                print 'In arm: '+n
#                 ob = [k for k in obs if n in k]
                ob = [k for k in obs]
                # print(ob)

                dat = np.genfromtxt(str(ob[0]), dtype = np.float64)
                wave = dat[:,0]
                flux = dat[:,1]
                nbins = len(wave)
                log_binned_wl = np.array(hist(wave,[min(wave),max(wave)], int(nbins/2.0),'log'))
                from scipy.interpolate import InterpolatedUnivariateSpline
                sps = InterpolatedUnivariateSpline(wave, flux)
                flux = medfilt(sps(log_binned_wl) , 35)
                wave = log_binned_wl
                ax.plot(wave, flux/1e-16, label='Corrected', zorder=5, lw = 1.25, color = cmap[0], linestyle='steps-mid', rasterized=True)



                dat = np.genfromtxt(str(ob[0]), dtype = np.float64)
                wave = dat[:,0]
                flux = dat[:,1]
                nbins = len(wave)
                log_binned_wl = np.array(hist(wave,[min(wave),max(wave)], int(2.0*nbins),'log'))
                from scipy.interpolate import InterpolatedUnivariateSpline
                sps = InterpolatedUnivariateSpline(wave, flux)
                flux = medfilt(sps(log_binned_wl) , 5)
                wave = log_binned_wl
                ax.plot(wave, flux/1e-16, label='Corrected', zorder=3, lw = 0.25, color = cmap[2], linestyle='steps-mid', rasterized=True)



                dat = np.genfromtxt(str(obs_check[0]), dtype = np.float64)
                wave = dat[:,0]
                flux = dat[:,1] #/ np.median(dat_check[:,1])

                log_binned_wl = np.array(hist(wave,[min(wave),max(wave)], int(2.0*nbins),'log'))
                from scipy.interpolate import InterpolatedUnivariateSpline
                sps = InterpolatedUnivariateSpline(wave, flux)
                flux = medfilt(sps(log_binned_wl) , 5)
                wave = log_binned_wl


                ax.plot(wave, flux/1e-16, label = 'Uncorrected', zorder=4, lw = 0.25, alpha = 1.0, color = cmap[1], linestyle='steps-mid', rasterized=True)




                ax.set_xlabel(r'Wavelength [$\AA$]')
                ax.set_ylabel(r'Flux density [10$^{-16}$ erg s$^{-1}$ cm$^{-2}$ $\AA^{-1}$]')



                # ax.loglog()
                # ax.semilogy()

                # # Formatting axes
                # import matplotlib as mpl
                # ax.xaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
                # ax.set_xticks([1000, 2000, 3000, 5000, 10000])
                # ax.get_xaxis().tick_bottom()
                # # ax.xaxis.set_minor_locator(mpl.ticker.NullLocator())
                #
                # ax.yaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
                # # ax.set_yticks([0.5, 1, 2, 5, 10, 20, 50])



                ax.set_xlim((7000, 22000))
                ax.set_ylim((-1.5e-16/1e-16, 6e-16/1e-16))


                import matplotlib as mpl
                # ax.xaxis.set_major_formatter(mpl.ticker.ScalarFormatter())
                ax.set_xticks([9000, 12000, 15000, 18000, 21000])


                for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                             ax.get_xticklabels() + ax.get_yticklabels()):
                    item.set_fontsize(16)

                format_axes(ax)
                pl.tight_layout()

                fig.savefig("../documents/figs/tell_corr_QC.pdf", clobber=True,bbox_inches='tight')
                pl.show(block=True)
            # print fig.axes
                
