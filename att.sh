#!/bin/bash
  
cmd=$1

source /data/condor_builds/users/avijai/RNO/rno_dep/setup.sh
export PYTHONPATH=/data/condor_builds/users/avijai/RNO/NuRadioMC/NuRadioMC:$PYTHONPATH

echo $LD_LIBRARY_PATH

$cmd


