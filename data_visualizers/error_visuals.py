import csv
import pandas as pd

import matplotlib
import matplotlib.pyplot as plt

inp = input("Enter filepath")

if inp != "":
	filename = inp.strip()
else:
	print("No file input!")
	quit()

data = pd.read_csv(filename)

data['error'] = (data['calibrated_torqueL'] / data['MVT_L']) - (data['calibrated_torqueR'] / data['MVT_R'])

first_time = data['Time'].values[0]
data['calc time'] = data['Time'] - first_time

length = data.shape[0]
elapsed_time = data['calc time'].values[-1]

print(f"{length} datapoints in {elapsed_time} seconds")
avg_hz = length/elapsed_time
print(f"Avg. hZ = {avg_hz}")


data.plot(x='calc time', y=['calibrated_torqueL', 'calibrated_torqueR', 'error'])

plt.show()
