"""
Use this as the command you use to launch the qlaunch singleshot in reservation mode (see the crontab_setup.md file).
It confirms that you have not exceeded the number of jobs that you would like to have running in the que, and then creates a file
folder for the documents needed for the run (If you don't use this, the vasp files from different runs will blend and create errors)
NOTE:
- You will need to change the path to your username
- Put this script in your home directory
"""

from datetime import datetime
import os
import subprocess

MAX_IN_QUE = 24

# change the directory to be atomate/reserve_scratch
os.chdir("/fslhome/calebh27/atomate/reserve_scratch")

# get datetime object, and format into string
now = datetime.now()
dt_string = now.strftime("%Y-%m-%d_%H:%M:%S")

# create new directory, named after the current datetime
os.mkdir(dt_string)

# move into the newly created directory
os.chdir(os.getcwd() + "/"+ dt_string)

# get the number of lines that are returned by the squeue command, which effectively
# tells you how many things are currently running.
queue_info = subprocess.run(['squeue', '-u', 'calebh27'], capture_output=True, text=True).stdout
jobs_running = queue_info.count('\n') - 1 # first line is the column headers

if jobs_running <= MAX_IN_QUE:
    # runs command to launch a rocket
    launch_info = subprocess.run(['qlaunch', '-r','singleshot'], capture_output=True, text=True).stdout
    print(launch_info)
else:
    print("There are already", MAX_IN_QUE, "jobs running")
