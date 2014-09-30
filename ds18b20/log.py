# Logger script for DS18B20 digital temperature sensor array.
#
# Notes:
#	Change the variables below to customise your logging.
#
#	Attached sensors are detected automatically.
#
#	Bad temperature readings are shown as -273.
#
#	If the program seems to hang, it's probably because it's waiting for a temperature
#	sensor to give it a reading. This indicates a problem with the sensor or the Raspberry
#	Pi's ability to read it.
#
# Sean Leavey
# s.leavey.1@research.gla.ac.uk
# http://www.astro.gla.ac.uk/~sleavey/
#
# July 2013

import os
import glob
import time

# load required kernel modules
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

####################################################################
####################### settings for logging #######################
####################################################################

# sleep time between readings
sleep_time = 10

# log file name
log_file = "~/temperature_log"

# number of decimal places to round temperatures to
rounding = 3

####################################################################
###### below are some variables you probably shouldn't modify ######
####################################################################

# base sensor directory (without trailing slash)
base_directory = "/sys/bus/w1/devices"

# temperature file name
temperature_file_name = "w1_slave"

####################################################################
########## get a list of sensors in the sensor directory ###########
####################################################################

# go to sensor directory
os.chdir(base_directory)

# keep count of sensors found
sensors_found = 0

# define the list of sensors
sensors = list()

# iterate over folders
for folder in os.listdir("."):
	# look to see if the folder starts with 28 - a sensor serial number
	if folder.startswith("28"):
		# add sensor to list
		sensors.append(folder)

		# increment counter
		sensors_found = sensors_found + 1

if sensors_found == 0:
	print "No sensors found. Exiting."
	exit()
else:
	print "Found " + str(sensors_found) + " sensor(s)."

####################################################################
##################### sensor reading function ######################
####################################################################
def read_sensor(sensor):
	device_file = os.path.join(base_directory, sensor, temperature_file_name)

	# get contents of file
	file_handler = open(device_file, 'r')
	lines = file_handler.readlines()
	file_handler.close()

	return lines

####################################################################
################# temperature extraction function ##################
####################################################################
def read_temperature(sensor):
	lines = read_sensor(sensor)

	# loop until the sensor is ready to give a reading
	while lines[0].strip()[-3:] != 'YES':
		# sleep for a little while
		time.sleep(0.2)

		# try again
		lines = read_sensor(sensor)

	# find the position of the 't=' text - the temperature is next
	equals_position = lines[1].find('t=')

	# get the temperature
	if equals_position != -1:
		# get the temperature string from the position of 't='
		temperature_string = lines[1][equals_position + 2 :]

		# get temperature
		temperature = float(temperature_string) / 1000.0

		# round the temperature
		temperature = round(temperature, rounding)
	else:
		# default option for when temperature cannot be read
		temperature = -273

        return temperature

####################################################################
######################## main program loop #########################
####################################################################
while True:
	temperatures = list()

	# read sensors
	for sensor in sensors:
		temperatures.append(str(read_temperature(sensor)))

	# create tab delimeted line
	message = str(time.time()) + "\t" + "\t".join(temperatures)

	# log to file
	log = open(log_file, "a")
	log.write(message + "\n")
	log.close()

	# print message
	print message

	# sleep
	time.sleep(sleep_time)
