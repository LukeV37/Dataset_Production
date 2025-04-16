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
  ./run.sh $madgraph_out_tag $process $num_runs $num_events_per_run $max_cpu_cores
  cd $WORKING_DIR
  end=`date +%s`
  runtime=$((end-start))
  echo -e "\tTime (sec): $runtime"
fi

# Run Pythia Showering
if [ "$bypass_pythia" = false ]; then
  start=`date +%s`
  cd pythia
  ./run.sh $pythia_in_tag $pythia_out_tag $num_runs $max_cpu_cores
  cd $WORKING_DIR
  end=`date +%s`
  runtime=$((end-start))
  echo -e "\tTime (sec): $runtime"
fi

# Run preprocessing to match fat jets to top quarks
if [ "$bypass_preprocessing" = false ]; then
  echo "Please be patient for Preprocessing..."
  start=`date +%s`
  cd model

  job=0
  batch=1
  for (( i=0 ; i<$num_runs ; i++ ));
  do
    echo -e "\t\tSubmitting job to preprocess run $i"
    mkdir -p "${dir_preprocessing}/run_$i"
    mkdir -p "${dir_datasets}/run_$i"
    python -u Preprocessing.py $tag $i $dir_preprocessing $dir_datasets $analysis_type > "${dir_preprocessing}/run_$i/preprocessing.log" &
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

# Run batching to pad dataset
if [ "$bypass_batch" = false ]; then
  echo "Please be patient for Batching..."
  start=`date +%s`
  cd model

  job=0
  batch=1
  for (( i=0 ; i<$num_runs ; i++ ));
  do
    echo -e "\t\tSubmitting job to pad and batch run $i"
    mkdir -p "${dir_datasets}/logs"
    python -u Batch_MSE.py $tag $i $dir_datasets > "${dir_datasets}/logs/batch.log" &
    job=$((job+1))
    if [ $job == $max_cpu_cores ]; then
      echo -e "\tStopping jobs submissions! Please wait for batch $batch to finish..."
      wait
      job=0
      batch=$((batch+1))
    fi
  done
  wait

  python -u Combine_Batches.py $tag $num_runs $dir_datasets
  cd $WORKING_DIR
  end=`date +%s`
  runtime=$((end-start))
  echo -e "\tBatching Done!"
  echo -e "\tTime (sec): $runtime"
fi
