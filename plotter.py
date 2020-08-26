'''
    Custom plotting framework made by Jackson

    Plot object holds the axis and data on the plot
'''
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import time
from multiprocessing.connection import Client

class plot(object):
    def __init__(self, ax, floor, ceiling, num_pts_display=2000, show_ticks=False):
        self.ax = ax
        self.floor = floor
        self.ceiling = ceiling
        self.num_pts_display = num_pts_display

        self.show_ticks = show_ticks

        self.line, = self.ax.plot([0], [0])

        if not show_ticks:
            self.ax.set_xticks([])

        self.ymin, self.ymax = 0, 1

        self.ax.set_ylim([self.ymin, self.ymax])
        self.ax.set_xlim([0, num_pts_display])

        self.x_data = [0]
        self.y_data = [0]

        self.prev_time = time.time()

    def add_data(self, x_val, y_val):
        '''
            Adds data to the inner cache
        '''
        if len(self.x_data) < self.num_pts_display:
            self.x_data.append(self.x_data[-1]+1)

        self.y_data.append(y_val)

    def update_line(self):
        '''
            Truncates the data, and updates the line object
        '''

        # self.x_data = self.x_data[-self.num_pts_display:]
        self.y_data = self.y_data[-self.num_pts_display:]

        self.line.set_data(self.x_data[::5], self.y_data[::5])

        # self.ax.set_xlim([self.x_data[0], self.x_data[-1]])

        update = False

        if min(self.floor, min(self.y_data)) != self.ymin:
            update = True
            self.ymin = min(self.floor, min(self.y_data))

        elif max(self.ceiling, max(self.y_data)) != self.ymax:
            update = True
            self.ymax = max(self.ceiling, max(self.y_data))

        if update:
            self.ax.set_ylim([self.ymin, self.ymax])

class plotter(object):
    def __init__(self, port_num, num_plots):
        self.port_num = port_num
        self.num_plots = num_plots

        address = ('localhost', port_num)
        self.conn = Client(address)
        print("plotter connection established")

        self.fig, axes = plt.subplots(num_plots, 1)

        self.plots = []

        for ax in axes:
            self.plots.append(plot(ax, 0, 1))

        self.prev_time = time.time()

    def animate(self, i):
        '''
            takes in data in the form ((data1, data2...), time) in the socket

            the two :params: are input by matplotlib.animation
        '''

        while self.conn.poll():
            # Expects data coming in to be in the form 
            try:
                data = self.conn.recv()
            except EOFError:
                self.conn.close()
                quit()

            # Cycle through the plots/ data and add and update the data
            for i in range(self.num_plots):
                self.plots[i].add_data(data[1], data[0][i])

        # Cycle through the plots and update the line objects
        for plot in self.plots:
            plot.update_line()

        # print(f"FPS: {1/(time.time()-self.prev_time)}")
        self.prev_time = time.time()

    def plot(self):
        ani = animation.FuncAnimation(self.fig, self.animate, interval = 40)
        plt.show()
        self.conn.close()

if __name__ == '__main__':
    p = plotter(6008, 2)
    p.plot()

"""
Basic plotting legacy code

import numpy as np
from matplotlib import pyplot as plt
import matplotlib.animation as animation
import time
from multiprocessing.connection import Client

port_number = 6008
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
"""