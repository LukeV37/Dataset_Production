#!/bin/bash

# Read options from config
if [[ -z $1 ]]; then
  source job.config
else
  source $1
fi

# Get current directory
WORKING_DIR=$(pwd)

# Setup python venv
source setup.sh

# Run MadGraph Generation
if [ "$bypass_madgraph" = false ]; then
  start=`date +%s`
  cd madgraph
  ./run.sh $madgraph_out_tag $process $num_runs_madgraph $num_events_per_run $max_cpu_cores
  cd $WORKING_DIR
  end=`date +%s`
  runtime=$((end-start))
  echo -e "\tTime (sec): $runtime"
fi

# Run Pythia Showering
if [ "$bypass_pythia" = false ]; then
  start=`date +%s`
  cd pythia
  ./run.sh $pythia_in_tag $pythia_out_tag $num_runs_pythia $mu $minJetpT $max_cpu_cores
  cd $WORKING_DIR
  end=`date +%s`
  runtime=$((end-start))
  echo -e "\tTime (sec): $runtime"
fi

# Run preprocessing to match fat jets to top quarks
if [ "$bypass_preprocessing" = false ]; then
  echo "Please be patient for Preprocessing..."
  start=`date +%s`
  cd preprocessing
  dir_preprocessing="WS_${preproc_out_tag}/logs"
  dir_datasets="WS_${preproc_out_tag}/data"
  mkdir -p "${dir_datasets}"

  job=0
  batch=1
  for (( i=0 ; i<$num_runs_preproc; i++ ));
  do
    echo -e "\t\tSubmitting job to preprocess run $i"
    mkdir -p "${dir_preprocessing}/run_$i"
    python -u preprocessing.py "../pythia/WS_${preproc_in_tag}/data/dataset_showered_run_${i}.root" "${dir_datasets}/dataset_preprocessed_run_$i.pkl" "$dir_preprocessing/run_$i" > "${dir_preprocessing}/run_$i/preprocessing.log" &
    job=$((job+1))
    if [ $job == $max_cpu_cores ]; then
      echo -e "\tStopping jobs submissions! Please wait for batch $batch to finish..."
      wait
      job=0
      batch=$((batch+1))
    fi
  done
  wait

  cd $WORKING_DIR
  end=`date +%s`
  runtime=$((end-start))
  echo -e "\tPreprocessing Done!"
  echo -e "\tTime (sec): $runtime"
fi
