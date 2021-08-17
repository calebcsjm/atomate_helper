## Some atomate Errors:

- `Validation failed: VasprunXMLValidator`:
  - If the .error file for the workflow contains the above error, then that means the vasp run failed. Check the std_err.txt or vasp.out files in the Launcher to see more details and address how to solve it

- Workflows always in state "RUNNING" (even after walltime has been exceeded):
  - you can run `lpad detect_lostruns`, and it will report all the workflows that are running without having any activity in the last 4 hours
  - You can mark these as FIZZLED using `lpad detect_lostruns --fizzle` (which marks them all as FIZZLED) or `lpad detect_lostruns --rerun` (which marks them as FIZZLED and then reruns them)
  - Based on my current understanding, this happens when the terminal is closed or times out before the workflows are complete. Consequently, after you run `qlaunch rapidfire`, you can't close the terminal (see "3.3.3 Running the workflows" at [this site](https://github.com/quanshengwu/MPWorks))
  - See the [Dealing With Failures and Crashes](https://materialsproject.github.io/fireworks/failures_tutorial.html#) tutorial in the FireWorks documentation for more information
  - ***NOTE: See the crontab setup file for a partial workaround***

## Some Mongo Errors:

- "error=AutoReconnect('localhost:27017: [Errno 111] Connection refused')"
  - Add `"export FW_CONFIG_FILE=/<path>/atomate/config/FW_config.yaml"` to your `.bash_profile` in your home directory
  - If you already added it, you may need to open a new teminal window
- pymongo.errors.ServerSelectionTimeoutError: cluster0-shard-00-01.9esxz.mongodb.net:27017: [Errno 101] Network is unreachable 
  - Make sure the IP addresses were whitelisted by the computing administrators
- pymongo.errors.ServerSelectionTimeoutError: connection closed
  - Add “ssl: True” and “authsource: admin” to the end of the my_launch.yaml file

## Some Vasp Errors:

- forrtl: severe (174): SIGSEV, segmentation fault occurred
  - It had a memory error and overflowed the stack
  -   Run `ulimit -s unlimited` in the terminal, or add it to your `.bash_profile` (see atomate_installation_notes for more detais)
