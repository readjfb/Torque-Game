import numpy as np
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import time
from multiprocessing.connection import Client

port_number = 6010
display_num_pts = 2000


'''
    Establish a socket connection
'''
address = ('localhost', port_number)
conn = Client(address)
print("plotter connection established")

'''
    Create Matplotlib subplots and lineplots
'''
fig, (ax1, ax2) = plt.subplots(2,1)

line1, = ax1.plot([0], [0])
line2, = ax2.plot([0], [0])

ax1.set_xticks([])

# These lists will hold the data. The values in the lists are just random initial values
times = [0,.1]
left_datapoints, right_datapoints = [0, .1], [0, .1]


'''
    Cache the limits; done for performance boost
'''
ax1_ymin, ax1_ymax = 0, 1
ax2_ymin, ax2_ymax = 0, 1

update1, update2 = False, False

ax1.set_ylim([ax1_ymin, ax1_ymax])  
ax2.set_ylim([ax2_ymin, ax2_ymax])  

def animate(i, xs, ys1, ys2):
    global ax1_ymax, ax1_ymin, ax2_ymin, ax2_ymax, update1, update2

    while conn.poll():
        # Expects data coming in to be in the form ((data1, data2...), time)
        try:
            data = conn.recv() 
        except EOFError:
            conn.close()
            quit()
        
        ys1.append(data[0][0])
        ys2.append(data[0][1])
        xs.append(data[1])

    xs = xs[-display_num_pts:]
    ys1 = ys1[-display_num_pts:]
    ys2 = ys2[-display_num_pts:]

    line1.set_data(xs, ys1)
    line2.set_data(xs, ys2)

    ax1.set_xlim([xs[0], xs[-1]])  
    ax2.set_xlim([xs[0], xs[-1]])

    # Ensuring that the window doesn't change axis more than is neccesary. Speeds up performance. 
    if min(0, min(ys1)) != ax1_ymin:
        update1 = True
        ax1_ymin = min(0, min(ys1))

    if max(1, max(ys1)) != ax1_ymax:
        update1 = True
        ax1_ymax = max(1, max(ys1))

    if min(0, min(ys2)) != ax2_ymin:
        update2 = True
        ax2_ymin = min(0, min(ys2))

    if max(1, max(ys2)) != ax2_ymax:
        update2 = True
        ax2_ymax = max(1, max(ys2))

    if update1: 
        ax1.set_ylim([ax1_ymin, ax1_ymax])  
    
    if update2: 
        ax2.set_ylim([ax2_ymin, ax2_ymax])  


ani = animation.FuncAnimation(fig, animate, fargs=(times, left_datapoints, right_datapoints), interval=30)
plt.show()
conn.close()
