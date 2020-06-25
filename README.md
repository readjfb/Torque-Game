# Torque-Game

**Status** *Work in progress*

## Overview
The program relies on three separate Python scripts running in parallel communicating over `python.multiprocessing` sockets. 
- program_main.py
	- The main backbone of the program. Holds the various visualization tools. Takes in data from main_data_streamer.py via a socket, saves data, and routes the data into the various visualization tools. 
	- Stores program state, and conditionally calls the tools.
	- Takes data via the remote socket, and sets the program state, saves data, and quits the program when needed. 
- admin_control.py
	- GuiZero/ TKinter remote that sets the program state, as well as can transmit other signals such as `save` or `quit.` The remote should be used to quit the program, as it does safely.
	- Transmits the signals via a socket back to program_main
- main_data_streamer.py
	- Runs at precisely a given rate, normally 1 KHz. 

## How to run it
- **Shell script** `fullRunner.sh` runs all three scripts.
- **Manually** run all three scripts simulaneously. Using three separate tabs works, as does running three separate 

## Environment
The game is being developed on macOS Mojave 10.14.6, during which there are a number of issues with Python video drivers and TKinter. I'm not sure how this will work on other operating systems, but a Conda environment with python `3.6.3` that works for the game can be found in [`environment.yml`](environment/environment.yml). Simply create a Conda environment called `torqueenv` from that file, and it *should* work. [Conda guide](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file). 
If a wrong combination of Python version + TKinter + OS is used, the computer may crash. 

## To-Dos
- [X] Finish a prototype of the game
- [X] Get data saving to run stabily at 1KHZ.
- [X] Finish pymunk physics in main_game
- [X] Create bash script to run all of the scripts
- [ ] Finish prototype of main_game
- [ ] Finish calibration system + implementation into the program controller
- [ ] Add start button/ system for automation
- [ ] Add automated system for MVT Viewer
- [ ] Add audio cues for MVT Viewer
- [ ] Add automated system for main_game
