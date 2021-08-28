"""
Use this as the command you use to launch the qlaunch singleshot (see the crontab_setup.md file). It confirms that
you have not exceeded the number of jobs that you would like to have running in the que
before launching another rocket.
NOTE:
- You will need to change the path to your username
- Put this script in your home directory
"""

MAX_IN_QUE = 24

import os
import subprocess

# set the starting directory to home
os.chdir("/zhome/calebh27")

# activate the atomate_env
os.system("source /zhome/calebh27/atomate/atomate_env/bin/activate")

# change the directory to be atomate/scratch
os.chdir("/fslhome/calebh27/atomate/scratch")

# get the number of lines that are returned by the squeue command, which effectively
# tells you how many things are currently running.
queue_info = subprocess.run(['squeue', '-u', 'calebh27'], capture_output=True, text=True).stdout
jobs_running = queue_info.count('\n') - 1 # first line is the column headers

if jobs_running <= MAX_IN_QUE:
    # runs command to launch a rocket
    launch_info = subprocess.run(['qlaunch', 'singleshot'], capture_output=True, text=True).stdout
    print(launch_info)
else:
    print("There are already", MAX_IN_QUE, "jobs running")

