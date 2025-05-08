#!/bin/bash

echo "Generating HS Process..."
./run_job.sh configs/HS.config | tee HS_generation.log
echo "Showering Datasets..."
./run_job.sh configs/AE_input.config | tee AE_input.log
./run_job.sh configs/AE_output.config | tee AE_output.log
echo "Padding output to match input..."

