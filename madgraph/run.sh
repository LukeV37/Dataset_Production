#!/bin/bash

######################
### Initialization ###
######################
if [ -z "$4" ]; then
    echo "Must enter 4 agruments"
    echo -e "\t1: Dataset Tag e.g. MyDataset"
    echo -e "\t2: Physics Process e.g. HHbbbb"
    echo -e "\t3: Number of Runs e.g. 10"
    echo -e "\t4: Number of Events per Run e.g. 10k,1M"
    exit 1
fi
dataset_tag=$1
process=$2
num_runs=$3
num_events_per_run=$4

###########################
### MadGraph Generation ###
###########################

# Edit process card
sed "s/output pp_tt_semi_full/output pp_tt_semi_full_${dataset_tag}/" include/proc_card_mg5.dat > proc_card.tmp
if [ "$polarization" = "L" ]; then
  sed -i "s/generate p p > t t~, t > b j j, t~ > b~ l- vl~/generate p p > t{L} t~, t > b j j, t~ > b~ l- vl~/" proc_card.tmp
fi
if [ "$polarization" = "R" ]; then
  sed -i "s/generate p p > t t~, t > b j j, t~ > b~ l- vl~/generate p p > t{R} t~, t > b j j, t~ > b~ l- vl~/" proc_card.tmp
fi
if [ "$polarization" = "down" ]; then
  sed -i "s/generate p p > t t~, t > b j j, t~ > b~ l- vl~/generate p p > t t~, t > b u d~, t~ > b~ l- vl~/" proc_card.tmp
fi
if [ "$polarization" = "charm" ]; then
  sed -i "s/generate p p > t t~, t > b j j, t~ > b~ l- vl~/generate p p > t t~, t > b c s~, t~ > b~ l- vl~/" proc_card.tmp
fi

# Edit run card
#sed "s/\(.*\)= nevents\(.*\)/ $num_events = nevents\2/" include/run_card.dat > run_card.tmp
sed "s/multi_run.*/multi_run $num_runs/" include/multi_run.config > multi_run.tmp
sed -i "s/set nevents.*/set nevents $num_events_per_run/" multi_run.tmp

# Run mg5_aMC binary on the process card
../submodules/mg5amcnlo-v3.5.5/bin/mg5_aMC proc_card.tmp

# Copy the cuts.f card to the SubProcesses folder
cp ./include/cuts.f "./pp_tt_semi_full_${dataset_tag}/SubProcesses/"

# Copy the cards to the Cards folder
#cp run_card.tmp "./pp_tt_semi_full_${dataset_tag}/Cards/run_card.dat"

# Generate the Events!
#"./pp_tt_semi_full_${dataset_tag}/bin/generate_events" -f
echo "Please be patient while MadGraph generates processes..."
"./pp_tt_semi_full_${dataset_tag}/bin/madevent" multi_run.tmp | tee "MadGraph_${dataset_tag}.log"

# Clean up workspace (generated automatically by madgraph binary)
rm -f py.py
rm -f MG5_debug
rm -f ME5_debug
rm *.tmp

echo
echo -e "\tMadGraph Generation Done!"
