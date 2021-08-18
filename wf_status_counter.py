"""This is a short script I wrote for the supercomputer, which quickly gives you a count of how many workflows are in each of the various states. You will need to alter the path."""

import os
import subprocess

# activate the atomate_env
os.system("source /zhome/calebh27/atomate/atomate_env/bin/activate")

print("Workflow Status Counts:")

# Get the info on the status of all the various states
completed_count = subprocess.run(['lpad', 'get_wflows', '-s', 'COMPLETED','-d','count'], capture_output=True, text=True).stdout
print('Completed:', completed_count)
running_count = subprocess.run(['lpad', 'get_wflows', '-s', 'RUNNING','-d','count'], capture_output=True, text=True).stdout
print('Running:', running_count)
ready_count = subprocess.run(['lpad', 'get_wflows', '-s', 'READY','-d','count'], capture_output=True, text=True).stdout
print('Ready:', ready_count)
fizzled_count = subprocess.run(['lpad', 'get_wflows', '-s', 'FIZZLED','-d','count'], capture_output=True, text=True).stdout
print('Fizzled:', fizzled_count)
paused_count = subprocess.run(['lpad', 'get_wflows', '-s', 'PAUSED','-d','count'], capture_output=True, text=True).stdout
print('Paused:', paused_count)
reserved_count = subprocess.run(['lpad', 'get_wflows', '-s', 'RESERVED','-d','count'], capture_output=True, text=True).stdout
print('Reserved:', reserved_count)
