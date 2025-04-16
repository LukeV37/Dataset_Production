#!/bin/bash
dir=$(git rev-parse --show-toplevel) 
cd "$dir/submodules/torch"
ls | grep -v "pip_requirements.txt" | xargs rm -rf
cd $dir
