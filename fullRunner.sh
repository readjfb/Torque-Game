source activate torqueenv

python program_main.py &
sleep 1

python admin_control.py &
sleep 1

python main_data_streamer.py &

wait %1 %2 %3