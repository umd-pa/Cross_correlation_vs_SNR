Obtaining the time of max cross-correlations between channels as a function of the SNR 

1) Run python3 make_dag_cc.py to get cc.dag 
2) Run condor_submit_dag cc.dag
3) Run python3 make_dag_ccnsr.py to get ccsnr.dag
4) Run condor_submit_dag ccsnr.dag

   *This uses the SNR as obtained from the trigger efficiency vs SNR study
