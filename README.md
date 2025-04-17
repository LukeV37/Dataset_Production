## Quick Start
Clone the repo:
```
git clone --recursive git@github.com:LukeV37/Dataset_Production.git
```

Ensure dependencies are met, and install the submodules using the command below. \
This only needs to be done once. Please be patient while submodules build...
```
./build_submodules.sh
```

Install python virtual environment using the command below. \
This needs to be done once every login.
```
source setup.sh
```

## How To Generate Datasets

### Modify Job Options
Modify the job options in the `job.config` file.

### Generate Dataset
Simply execute the command:
```
./run_job.sh
```

## Dependencies
Runs on most linux environments with [ROOT](https://root.cern/install/) installed. Developed on Ubuntu 22.04.

Required Dependencies:
<ul>
  <li>python3</li>
  <li>ROOT</li>
  <li>g++</li>
  <li>gfortran</li>
  <li>gzip</li>
  <li>automake</li>
  <li>libtool</li>
  <li>autoconf</li>
</ul>
