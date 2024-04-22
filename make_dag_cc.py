#!/usr/env python 
import numpy as np

#run cross_correlation.py for specified attenuations (att_unique) and cross-correlated channel pairs (ch_combo)

att_unique  = np.arange(0, 32, 0.5)

ch_combo = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3), (9,10), (22,23)]

dag = ""
for att in att_unique:
    for combo in ch_combo:
        ch1 = combo[0] 
        ch2 = combo[1]
        job_name = f"{att}_{ch1}_{ch2}_sim"
        cmd = f"JOB {job_name} cc.sub\n"
        cmd += f"VARS {job_name} job_name=\"{job_name}\""
        cmd += f" cmd=\"'python3 /data/condor_builds/users/avijai/RNO/tutorials-rnog/get_daqstatus/cross_correlation.py "
        cmd += f"--file /data/i3store/users/avijai/rnog_tutorials/station23/run3400/combined.root "
        cmd += f"--att {att} "
        cmd += f"--ch1 {ch1} "
        cmd += f"--ch2 {ch2} "
        cmd += "'"
        cmd += f"\"\n"
        dag += cmd

open("cc.dag", 'w').write(dag)

