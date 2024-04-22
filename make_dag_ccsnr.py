#!/usr/env python 
import numpy as np

#run plot_cc_snr.py for cross-correlated channels 

ch_combo = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3), (9,10), (22,23)]

dag = ""
for combo in ch_combo:
    ch1 = combo[0]
    ch2 = combo[1]
    job_name = f"{ch1}_{ch2}_sim"
    cmd = f"JOB {job_name} cc.sub\n"
    cmd += f"VARS {job_name} job_name=\"{job_name}\""
    cmd += f" cmd=\"'python3 /data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/plot_cc_snr.py "
    cmd += f"--ch1 {ch1} "
    cmd += f"--ch2 {ch2} "
    cmd += "'"
    cmd += f"\"\n"
    dag += cmd

open("ccsnr.dag", 'w').write(dag)

