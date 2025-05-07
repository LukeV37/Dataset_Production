#!/bin/bash
dir=$PWD
rm -f dataset.root
cd ../submodules/delphes-v3.5.0/ 
./DelphesHepMC2 ./cards/delphes_card_ATLAS.tcl ../../delphes/dataset.root ../../pythia/shower.hepmc
cd $dir
