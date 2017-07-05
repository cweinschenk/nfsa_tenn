# **************************** Run Notes **************************** #
# Script used to plot data following NFSA Tennesse Burns              #
# ******************************************************************* #

# -------------- #
# Import Modules #
# -------------- #
import os
import glob
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
from pylab import * 
from scipy.signal import butter, filtfilt
from itertools import cycle
import datetime as datetime

# ------------------- #
# Set Plot Parameters #
# ------------------- #
# Flag to plot only the most recently saved data file
plot_newest = True

# Define 20 color pallet using RGB values
tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),
(44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),
(148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),
(227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),
(188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]

for i in range(len(tableau20)):
		r, g, b = tableau20[i]
		tableau20[i] = (r / 255., g / 255., b / 255.)

label_size = 18
tick_size = 16
line_width = 1.5
event_font = 8
legend_font = 10

# ----------------------- #
# Define Custom Functions #
# ----------------------- #
# Data filtering function & variables
cutoff = 50
fs = 700
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filtfilt(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = filtfilt(b, a, data)
    return y

# ---------------------------------- #
# Define Subdirectories & Info Files #
# ---------------------------------- #
info_dir = '../1_Info/'
data_dir = '../2_Data/'
save_dir = '../4_Plots/'

channel_list = pd.read_csv(info_dir + 'channel_list.csv').set_index('channel')
chart_list = pd.read_csv(info_dir + 'charts.csv').set_index('chart')
events = pd.read_csv(info_dir + 'events.csv').set_index('Burn')

# ---------------------------------- #
# Initialize Data Structures 		 #
# ---------------------------------- #
all_burn_data = {}

# -------------------- #
# Start Code Execution #
# -------------------- #

#Read in data file
burns = [x[0] for x in os.walk(data_dir)]
burns.remove(data_dir)

for burn in burns:
	print('Reading ' + burn)

	for f in os.listdir(burn):
		if f.endswith('.csv'):
			data = pd.read_csv(burn + '/' + f, header=2, skipfooter=1, engine='python').set_index('Time:')
			
			if f[-5] == 'a':
				names = data.columns.tolist()
				for x in range(len(names)):
					if names[x][:7] == 'Channel':
						names[x] = names[x] + 'a'
				data.columns=names
			
			if f[-5] == 'b':
				names = data.columns.tolist()
				for x in range(len(names)):
					if names[x][:7] == 'Channel':
						names[x] = names[x] + 'b'
				data.columns=names

			if f[:-5] in list(all_burn_data.keys()):
				all_burn_data[f[:-5]] = pd.concat([all_burn_data[f[:-5]], data], axis=1)
			else:
				all_burn_data[f[:-5]] = data

	# # all_burn_data[burn].reset_index(inplace=True)
	all_burn_data[f[:-5]].dropna(inplace=True)

	Time = all_burn_data[f[:-5]].index.values

	Ignition = datetime.datetime.strptime(events['Ignition'][f[:-5]], '%H:%M:%S')

	Time = [(datetime.datetime.strptime(t, '%H:%M:%S')-Ignition).total_seconds() for t in Time]

	all_burn_data[f[:-5]].index = Time

for burn in list(all_burn_data.keys()):
	
	print ('Plotting ' + burn.replace('_', ' '))

	for chart in chart_list.index.dropna(): 

        # Define figure for the plot
		fig = plt.figure()

		# Plot style - cycle through 20 color pallet & define marker order
		plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
		plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])

		for channel in chart_list.ix[chart].dropna().tolist():
			if channel not in all_burn_data[burn].columns.dropna():
				continue

			plot_data = all_burn_data[burn][channel]

			# scale = np.float(channel_list['scale'][channel])
			# offset = np.float(channel_list['offset'][channel])

			# plot_data = plot_data * scale + offset

			# Plot channel data
			plt.plot(plot_data, lw=line_width, marker=next(plot_markers), markevery=int(len(plot_data)/20),
				mew=3, mec='none', ms=7, label=channel_list[burn + ' title'][channel])

        # Set axis options, legend, tickmarks, etc.
		ax1 = plt.gca()
		handles1, labels1 = ax1.get_legend_handles_labels()
		ax1.xaxis.set_major_locator(plt.MaxNLocator(8))

		plt.xlabel('Time (sec)', fontsize=label_size)
		plt.ylabel('Temperature $^{\circ}$F', fontsize=label_size)
		plt.xticks(fontsize=tick_size)
		plt.yticks(fontsize=tick_size)

		# Secondary y-axis parameters
		# ax2 = ax1.twinx()
		# ax2.set_ylabel('Temperature $^{\circ}$C', fontsize=label_size)
		# ax2.set_yticks(fontsize=tick_size)

		#Need to get Y Limits and Scale
		#ax2.set_ylim([0, secondary_axis_scale])

				# Set figure size
		fig.set_size_inches(10,8)

		plt.legend(handles1, labels1, loc='upper left', fontsize=legend_font, handlelength=3)

		# Save plot to file
		if not os.path.exists(save_dir + burn + '/'):
			os.makedirs(save_dir + burn + '/')
		plt.savefig(save_dir + burn + '/' + chart + '.pdf')
		plt.close('all')

#Plot Burn 1 and Burn 2 Compare
compare_charts = {'Livingroom':[('Burn_1','Channel 1a','Sprinkler 7ft'),('Burn_1','Channel 2a','Sprinkler 3ft'),
				('Burn_2','Channel 1b','Non-Sprinkler 7ft'),('Burn_2','Channel 2b', 'Non-Sprinkler 3')],
				'Bedroom':[('Burn_1','Channel 3a','Sprinkler 7ft'),('Burn_1','Channel 4a','Sprinkler 3ft'),
				('Burn_2','Channel 3b','Non-Sprinkler 7ft'),('Burn_2','Channel 4b', 'Non-Sprinkler 3')],
				'Open_Closed_Bed':[('Burn_2','Channel 3b','Open Broom 7ft'),('Burn_2','Channel 4b','Open Bedroom 3ft'),
				('Burn_2','Channel 3a','Closed Bedroom 7ft'),('Burn_2','Channel 4a','Closed Bedroom 3ft')]}

for chart in list(compare_charts.keys()):

	print('Plotting ' + chart + ' Compare')
	# Define figure for the plot
	fig = plt.figure()

	# Plot style - cycle through 20 color pallet & define marker order
	plt.rcParams['axes.prop_cycle'] = (cycler('color',tableau20))
	plot_markers = cycle(['s', 'o', '^', 'd', 'h', 'p','v','8','D','*','<','>','H'])

	for burn,channel,chan_label in compare_charts[chart]:
		
		plt.plot(all_burn_data[burn][channel], lw=line_width, marker=next(plot_markers), markevery=int(len(plot_data)/20),
			mew=3, mec='none', ms=7, label=chan_label)

	# Set axis options, legend, tickmarks, etc.
	ax1 = plt.gca()
	handles1, labels1 = ax1.get_legend_handles_labels()
	ax1.xaxis.set_major_locator(plt.MaxNLocator(8))

	plt.xlabel('Time (sec)', fontsize=label_size)
	plt.ylabel('Temperature $^{\circ}$F', fontsize=label_size)
	plt.xticks(fontsize=tick_size)
	plt.yticks(fontsize=tick_size)
	plt.xlim([0,490])
	
	if chart == 'Livingroom':
		plt.ylim([0,1750])
	if chart == 'Bedroom':
		plt.ylim([0,400])

	# # Secondary y-axis parameters
	# ax2 = ax1.twinx()
	# ax2.set_ylabel('Temperature $^{\circ}$C', fontsize=label_size)
	# ax2.set_yticks(fontsize=tick_size)

	#Need to get Y Limits and Scale
	#ax2.set_ylim([0, secondary_axis_scale])

	# Set figure size
	fig.set_size_inches(10,8)

	plt.legend(handles1, labels1, loc='upper left', fontsize=legend_font, handlelength=3)

	# Save plot to file
	if not os.path.exists(save_dir):
		os.makedirs(save_dir)
	plt.savefig(save_dir + chart + '.pdf')
	plt.close('all')