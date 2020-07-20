'''
	time_diff_checker.py is a basic program to calculate the amount of time between saved 
	datapoints, and export in an easy to visualize format via matplotlib/ seaborn
'''

import csv
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

inp = input("Enter filepath")
print(inp)

if inp != "":
	filename = inp.strip()
else:
	print("No file input!")
	quit()

times = []

with open(filename, 'r') as file:
	reader = csv.reader(file, delimiter=",")
	for row in reader:
		# Change the index to the index in the csv of the time value. As of last test,
		# time value was value 4 in each csv row
		try:
			times.append(float(row[6]))
		except:
			continue


deltas = []
for i in range(1,len(times)):
	d = times[i]-times[i-1]
	deltas.append(d)

print(max(deltas), min(deltas))

# First plot is the total range of datapoints for a given file
fig, ax = plt.subplots(3)
ax[0].plot(deltas)
ax[0].set(xlabel="time(ms)", ylabel="time between datapoints")

# Second plot is the first 1000 data points (1 second assuming 1KHZ optimal data write)
# Used to ensure that there's not a regularly occuring lapse
ax[1].plot(deltas[:1000])
ax[1].set(xlabel="time(ms)", ylabel="time between datapoints")

sns.set()

# Third plot is a histogram of the time differences, to ensure that there's not a second
# peak. The only peak should be at .001 (assuming 1KHZ optimal)
sns.distplot(deltas, ax=ax[2])
ax[2].set(xlabel="time between datapoints", ylabel="frequency")
# ax[2].set(yscale='log')

plt.show()
