#!/bin/bash

if [ -z "$6" ]; then
    echo "Must enter 6 agruments"
    echo -e "\t1: Input Dataset Tag (from MadGraph)"
    echo -e "\t2: Output Dataset Tag"
    echo -e "\t3: Number of runs"
    echo -e "\t4: Average Amount of Pileup, mu"
    echo -e "\t5: Min Jet pT (GeV)"
    echo -e "\t6: Max num cpu cores"
    exit 1
fi

in_tag=$1
out_tag=$2
runs=$3
mu=$4
minJetpT=$5
max_cpu_cores=$6

mkdir -p "WS_${out_tag}"
mkdir -p "WS_${out_tag}/logs"
mkdir -p "WS_${out_tag}/data"

cd src
make generate_dataset

echo "Please be patient while Pythia performs hadronization..."

job=0
batch=1
for (( i=0 ; i<$runs ; i++ ));
do
    echo -e "\t\tSubmitting job to shower run $i"
    outfile="../WS_${out_tag}/data/dataset_showered_run_$i.root"
    { ./shower_dataset $in_tag $out_tag $i $mu $minJetpT; root -q -l -b scripts/add_JVT.cpp\(\""$outfile"\"\); root -q -l -b scripts/add_true_EMfrac.cpp\(\""$outfile"\"\);} > "../WS_${out_tag}/logs/${out_tag}_${i}.log" 2>&1 &
    job=$((job+1))
    if [ $job == $max_cpu_cores ]; then
        echo -e "\tStopping jobs submissions! Please wait for batch $batch to finish..."
        wait
        job=0
        batch=$((batch+1))

    fi
done
wait
make clean
cd ..

echo -e "\tPythia Showering Done!"
