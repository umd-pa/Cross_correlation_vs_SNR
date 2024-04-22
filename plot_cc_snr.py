import os, sys, shutil, glob
import argparse
import math
import numpy as np
import ROOT
import pickle
import scipy
import matplotlib.pyplot as plt
import csv
import pandas as pd
from ROOT import gStyle, gPad, kRed


parser = argparse.ArgumentParser(description='cc vs snr plot')
parser.add_argument('--ch1', type=float, required=True)
parser.add_argument('--ch2', type=float, required=True)
args = parser.parse_args()
ch1 = args.ch1
ch2 = args.ch2

# Stuff to make plots nicer
plt.rc('font', size=16)
plt.rcParams.update({
    "text.usetex": False,
    #"font.family": "sans-serif",
    #"font.sans-serif": ["Helvetica"]
    })
plt.rcParams['axes.facecolor']='w'
plt.rcParams['savefig.facecolor']='w'


# load the RNO-G library
ROOT.gSystem.Load(os.environ.get('RNO_G_INSTALL_DIR')+"/lib/libmattak.so")

#path to files with snr arrays for each attenuation 
#found as part of trig efficiency vs snr study 

indir = "/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/snr_npy_23_mod"


files = sorted(glob.glob(os.path.join(indir, "*")))


#calculating mean snr value in each attenuation bin 

snr_means = []
snr_std = []
atts = []
atts_12 = []
snr_means_12 = []
for f in files:
    att_one = f.split("/")[-1].split("_")[-1].split(".")[0]
    att_two = f.split("/")[-1].split("_")[-1].split(".")[1]
    att = int(att_one) + 0.1*int(att_two)

    snr_arr = np.load(f)

    if (len(snr_arr) != 0):
        atts.append(att)
        snr_means.append(np.average(snr_arr))
        snr_std.append(np.std(snr_arr))
        if (att >= 6 and att <= 13):
            atts_12.append(att)
            snr_means_12.append(np.average(snr_arr))


#exponential fit for attenuation between 6-15 dB

fit = scipy.optimize.curve_fit(lambda t,a,b: a*np.exp(b*t),  atts_12, snr_means_12,  p0=(17.5, -0.2))

x_vals = np.arange(0,32, 0.5)
y_vals = dict()

for x in x_vals:
    y_vals[x] = fit[0][0]*np.exp(fit[0][1]*x)

#path to files with cross_correlation arrays for each attenuation 

indir2 = "/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/cross_corr_all"


files2 = sorted(glob.glob(os.path.join(indir2, "*")))


#calculating median cross_correlation value in each attenuation bin 
#finding 68th, 95th and 99th percentiles

cross_corrs = []
atts_cc = []
cc_means = []
cc_std = []
cc_rms = []
cc_meds = []


err_68_low = []
err_68_high = []
err_99_low = []
err_99_high = []
err_68_size = dict()
err_99_size = dict()
err_95_low = []
err_95_high = []
err_95_size = dict()



for f in files2:
    name = f.split("/")[-1].split("_")
    att = int(name[2].split(".")[0]) + 0.1*int(name[2].split(".")[1])
    ch1_file = int(name[3].split(".")[0])
    ch2_file = int(name[-1].split(".")[0])

    if (ch1_file == ch1 and ch2_file == ch2):


        cross_corr = np.load(f)


        if (len(cross_corr) > 0):

            cc_mean = np.average(cross_corr)
            std = np.std(cross_corr)
            rms = np.sqrt(np.average(cross_corr**2))
            med = np.median(cross_corr)
        
            atts_cc.append(att)
            cc_means.append(cc_mean)
            cc_std.append(std)
            cc_rms.append(rms)
            cc_meds.append(med)

            #np.quantile calculates percentile
            #median unbiased -> best for unknown distributions

            err_68 = np.quantile(cross_corr, 0.68, method = "median_unbiased")
            err_32 = np.quantile(cross_corr, 0.32, method = "median_unbiased")

            err_68_size[att] = err_68 - err_32


            err_99 = np.quantile(cross_corr, 0.99, method = "median_unbiased")
            err_1 = np.quantile(cross_corr, 0.01, method = "median_unbiased")

            err_99_size[att] = err_99 - err_1

        
            err_95 = np.quantile(cross_corr, 0.95, method = "median_unbiased")
            err_5 = np.quantile(cross_corr, 0.05, method = "median_unbiased")

            err_95_size[att] = err_95 - err_5
        
        
            err_68_low.append(med - err_32)
            err_68_high.append(err_68 - med)

            err_99_low.append(med - err_1)
            err_99_high.append(err_99 - med)

            err_95_low.append(med - err_5)
            err_95_high.append(err_95 - med)


x_vals = []
y_vals_68 = []
y_vals_95 = []
y_vals_99 = []
for att in atts_cc:
    x_vals.append(y_vals[att])
    y_vals_68.append(err_68_size[att])
    y_vals_95.append(err_95_size[att])
    y_vals_99.append(err_99_size[att])


#export data to csv 

df = pd.DataFrame({'a':range(len(x_vals))})
df['SNR'] = x_vals
df['68%'] = y_vals_68
df['95%'] = y_vals_95
df['99%'] = y_vals_99

df.to_csv("/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/instrument_ppr_2/data.csv")


#plot data

plt.figure()
plt.scatter(x_vals, y_vals_68, label = "68%", marker = "o", c = "red")
plt.scatter(x_vals, y_vals_95, label = "95%", marker = "v", c = "green")
plt.scatter(x_vals, y_vals_99, label = "99%", marker = "s", c = "blue")
plt.legend()
plt.xlabel("SNR")
plt.ylabel("dT error bar size (ns)")
plt.ylim(0,0.5)
plt.xlim(4,32)
plt.savefig(f'/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/crosscorrelation_plots/error_bars_all_chs/cc_vs_snr_errbar_{ch1}{ch2}.png')
plt.close()

