#!/bin/bash
source /c/Users/zarif_vfgx7yn/miniconda3/etc/profile.d/conda.sh
conda activate torqueenv

python program_main.py &
sleep 1

python admin_control.py &
sleep 1

python main_data_streamer.py &
sleep 1

python plotter.py &

wait %1 %2 %3 %4