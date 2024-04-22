import os
import argparse
import math
import numpy as np
import ROOT
import pickle
import csv
import matplotlib.pyplot as plt
from ROOT import gStyle, gPad, kRed
import scipy
import scipy.optimize as opt
import pandas as pd
from scipy import signal
from scipy import interpolate
from scipy.interpolate import Akima1DInterpolator
from scipy.fft import fft, fftfreq, rfft, irfft
from array import array
from ROOT import gStyle, gPad, kRed, TMath
from NuRadioReco.utilities import bandpass_filter
from NuRadioReco.utilities import fft as fft_reco
from NuRadioReco.detector.RNO_G import analog_components
from NuRadioReco.utilities import units

# load the RNO-G library
ROOT.gSystem.Load(os.environ.get('RNO_G_INSTALL_DIR')+"/lib/libmattak.so")

# make sure we have enough arguments to proceed
parser = argparse.ArgumentParser(description='daqstatus example')
parser.add_argument('--file', dest='file', required=True)
parser.add_argument('--att', type=float, required=True)
parser.add_argument('--ch1', type=float, required=True)
parser.add_argument('--ch2', type=float, required=True)
args = parser.parse_args()
filename = args.file
att_lim = args.att
ch1 = args.ch1
ch2 = args.ch2


#voltage calibration coeffs

cal_path = "/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/volCalConsts_pol9_s23_1697181551-1697183024.root"
fIn = ROOT.TFile.Open(filename)
combinedTree = fIn.Get("combined")


volCalib = ROOT.mattak.VoltageCalibration()
volCalib.readFitCoeffsFromFile(cal_path)

d = ROOT.mattak.DAQStatus()
wf = ROOT.mattak.Waveforms()
hdr = ROOT.mattak.Header()

combinedTree.SetBranchAddress("daqstatus", ROOT.AddressOf(d))
combinedTree.SetBranchAddress("waveforms", ROOT.AddressOf(wf))
combinedTree.SetBranchAddress("header", ROOT.AddressOf(hdr))

num_events = combinedTree.GetEntries()

cc_times_all = []

for event in range(num_events):
    combinedTree.GetEntry(event)

    sysclk = hdr.sysclk
    sysclk_last_pps = hdr.sysclk_last_pps
    sys_diff = (sysclk - sysclk_last_pps)%(2**32)

    att = d.calinfo.attenuation

    #calculating cross correlation max time for each attenuation (att_lim)

    if att == att_lim:
        if (sys_diff <= 200*10**(3)):
            c = ROOT.mattak.CalibratedWaveforms(wf, hdr, volCalib, False)
            g0 = c.makeGraph(int(ch1))
            g1 = c.makeGraph(int(ch2))

            voltage0 = g0.GetY()
            time0 = g0.GetX()

            voltage1 = g1.GetY()
            time1 = g1.GetX()


            voltage_0 = []
            for v in voltage0:
                voltage_0.append(v - np.mean(voltage0))
            
            voltage_1 = []
            for v in voltage1:
                voltage_1.append(v - np.mean(voltage1))

            
            
            #interpolation, set both to timescale of channel 0 
            
            new_timescale = np.arange(time0[0], time0[-1], 0.01)
            
            voltage1_interp_akima = Akima1DInterpolator(time1, voltage_1)(new_timescale)
            voltage0_interp_akima = Akima1DInterpolator(time0, voltage_0)(new_timescale)
            
            
            #cross correlation

            corr = signal.correlate(voltage0_interp_akima, voltage1_interp_akima)
            lags = signal.correlation_lags(len(voltage0_interp_akima), len(voltage1_interp_akima))            
            total_time = max(new_timescale)

            conversion_factor = total_time/max(lags)
        
         
            #max correlation time

            max_corr = max(corr)
            
            max_corr_i = list(corr).index(max_corr)
            
            max_time = (lags*conversion_factor)[max_corr_i]
             
            cc_times_all.append(max_time)


np.save(f'/data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/cross_corr_all/cc_times_{att_lim}_{ch1}_{ch2}.npy', cc_times_all)
