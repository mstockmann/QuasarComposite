#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SYNOPSIS

    TODO helloworld [-h,--help] [-v,--verbose] [--version]

DESCRIPTION

    TODO This describes how to use this script. This docstring
    will be printed by the script if there is an error or
    if the user requests help (-h or --help).

EXAMPLES

    TODO: Show some examples of how to use this script.

EXIT STATUS

    TODO: List exit codes

AUTHOR

    TODO: Name <name@example.org>

LICENSE

    This script is in the public domain, free from copyrights or restrictions.

VERSION

    $
"""

from __future__ import division, print_function

__all__ = ["Module Name"]
__version__ = "0.0.0"
__author__ = "Jonatan Selsing (jselsing@dark-cosmology.dk)"
__copyright__ = "Copyright 2014 Jonatan Selsing"


def main():
    """Main script to prepare x-shooter observations for combination"""
    from matplotlib import rc_file
    rc_file('/Users/jselsing/Pythonlibs/plotting/matplotlibstyle.rc')
    from astropy.io import fits
    import glob
    import matplotlib.pyplot as pl
    import numpy as np
    import plotting.plotting as plot
    from xshoo.combine import inter_arm_cut
    from scipy.interpolate import splrep,splev

    #Files
    obj_name = 'SDSS0043+0114'
    root_dir = '/Users/jselsing/Work/X-Shooter/CompositeRedQuasar/processed_data/'+obj_name
    object_files = glob.glob(root_dir+'/OBJECT/*IDP*.fits')
    respose_files = glob.glob(root_dir+'/M.X*.fits')
    transmission_files = glob.glob(root_dir+'/transmission*.fits')
    arms = ['UVB', 'VIS', 'NIR']
    wl_out = []
    flux_out = []
    flux_uncorr = []
    err_out = []
    start = []
    end = []

    for n in arms:
        print('In arm: '+n)


        #Read in object spectrum
        obser = [k for k in object_files if n in k]
        ob = fits.open(obser[0])
        wl = 10.0*ob[1].data.field('WAVE')[0]
        flux = ob[1].data.field('FLUX')[0]
        err = ob[1].data.field('ERR')[0]


        #Read in master response curve
        master_response = [k for k in respose_files if n in fits.open(k)[0].header['HIERARCH ESO SEQ ARM']]
        resp = fits.open(master_response[0])
        response_wl = resp[1].data.field('LAMBDA')*10.0
        response = (resp[1].data.field('RESPONSE'))
        response_wl = response_wl
        interp = splrep(response_wl,response)

        #Apply master response function
        flux *= splev(wl,interp)
        err *= splev(wl,interp)
        flux
        if n== 'VIS' or n== 'NIR':
            transmission = fits.open([k for k in transmission_files if n in k][0])[0].data

            for j, k in enumerate(transmission):
                if k <= 1e-10:
                    transmission[j] = 1

            flux /= transmission
            err /= transmission

        wl, flux, err, start, end = inter_arm_cut(wl, flux, err, n, start, end)


        wl_out.append(wl)
        flux_out.append(flux)
        err_out.append(err)


    wl_out = np.hstack(wl_out)
    flux_out = np.hstack(flux_out)
    err_out = np.hstack(err_out)


    bp_map = []
    for j , (k, l) in enumerate(zip(flux_out[:-1],err_out[:-1])):
        if k > 1.1 * flux_out[j-1] or k < 0:
           bp_map.append(1)
        elif k < 0.90 * flux_out[j-1] or k < 0:
           bp_map.append(1)
        else:
           bp_map.append(0)
    bp_map.append(1)


    #Get SDSS spectrum
    # imageSDSS= glob.glob(root_dir+i+'*spec*.fits')
    # data1SDSS= fits.open(imageSDSS[0])


    import json
    import urllib2

    query_terms = dict()
    query_terms["ra"] = str(ob[0].header['RA'])+'d' #"185.1d"
    query_terms["dec"] = str(ob[0].header['DEC'])  #"56.78"
    query_terms["radius"] = "10.0"
    # query_terms["redshift"] = "0.1-0.2"

    url = "http://api.sdss3.org/spectrumQuery?" + '&'.join(["{0}={1}".format(key, value) for key, value in query_terms.items()])
    print(url)
    # make call to API
    response = urllib2.urlopen(url)

    # read response, converting JSON format to Python list
    matching_ids = json.loads(response.read())
    print(json.dumps(matching_ids, indent=4))

    # get the first id
    spec_id = matching_ids[0]

    url = "http://api.sdss3.org/spectrum?id={0}&format=json".format(spec_id)

    response = urllib2.urlopen(url)
    result = json.loads(response.read())
    SDSS_spectrum = result[spec_id]

    wl_sdss = np.array(SDSS_spectrum["wavelengths"])
    flux_sdss =  np.array(SDSS_spectrum["flux"])
    z_sdss = (np.array(SDSS_spectrum["z"]))


    wl_sdss = np.concatenate([wl_sdss,np.zeros(len(wl_out) - len(wl_sdss))])
    flux_sdss = np.concatenate([flux_sdss,np.zeros(len(flux_out) - len(flux_sdss))])



    # Load linelist
    fit_line_positions = np.genfromtxt('data/fitlinelist.txt', dtype=None)
    linelist = []
    for n in fit_line_positions:
        linelist.append(n[1])
    linelist = np.array(linelist)


    from methods import wavelength_conversion
    linelist = wavelength_conversion(linelist, conversion='vacuum_to_air')


    #Cut out fitting region
    mask = np.logical_and(wl > 11350, (wl < 11750))
    wl_fit = wl[mask]
    flux_fit = flux[mask]
    fluxerr_fit = fluxerr[mask]


    #Fit continuum and subtract
    from methods import continuum_fit
    cont, chebfit = continuum_fit(wl_fit, flux_fit, fluxerr_fit, edge_mask_len=20)
    chebfitval = chebyshev.chebval(wl, chebfit)


    #Define models to use
    from methods import voigt,gauss
    def model1(t,  amp2, sig22g, sig22l, z):
            tmp = voigt(t, abs(amp2), (1+z)*linelist[2], sig22g, sig22l)
            return tmp

    def model2(t, amp2, sig22g, z):
            tmp = gauss(t, abs(amp2), (1+z)*linelist[2], sig22g)
            return tmp


    #Initial parameters
    init_vals = [6e-17,10, redshifts]
    y_fit_guess = model2(wl_fit, *init_vals) + cont


    #Fit
    import scipy.optimize as op
    best_vals, covar = op.curve_fit(model2, wl_fit, flux_fit - cont, sigma=fluxerr_fit, absolute_sigma=True, p0=init_vals)
    print(best_vals)
    z_op = best_vals[-1]
    print("""Curve_fit results:
        Redshift = {0} +- {1} (SDSS: {2})
    """.format(z_op, np.sqrt(covar[-1,-1]), redshifts))






    #Saving to .dat file
    dt = [("wl", np.float64), ("flux", np.float64), ("error", np.float64), ("bp map", np.float64), ("wl sdss", np.float64), ("flux sdss", np.float64) ]
    data = np.array(zip(wl_out, flux_uncorr, err_out, bp_map, wl_sdss, flux_sdss), dtype=dt)
    file_name = "Telluric_uncorrected_science"
    print(root_dir+"/"+file_name+".dat")
    np.savetxt(root_dir+"/"+file_name+".dat", data, header="wl flux fluxerror bp_map sdss_wl, sdss_flux")#, fmt = ['%5.1f', '%2.15E'] )


    #Saving to .dat file
    dt = [("wl", np.float64), ("flux", np.float64), ("error", np.float64), ("bp map", np.float64), ("wl sdss", np.float64), ("flux sdss", np.float64) ]
    data = np.array(zip(wl_out, flux_out, err_out, bp_map, wl_sdss, flux_sdss), dtype=dt)
    file_name = "Telluric_corrected_science"
    np.savetxt(root_dir+"/"+file_name+".dat", data, header="wl flux fluxerror bp_map sdss_wl, sdss_flux")#, fmt = ['%5.1f', '%2.15E'] )






if __name__ == '__main__':
    main()