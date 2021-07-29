# Crontab Setup

As mentioned in the atomate errors notes, if you close the terminal while the `qlaunch rapidfire` is still running, it will cause any incompleted workflows to fail, and always appear in the "RUNNING" state. Setting up a crontab is one way to run the jobs without having to have the terminal open. Crontab can automatically run commands at given time intervals. 

## Simple Version:
1. Run `crontab -e` in the terminal
2. Paste the following code into the file, then save (adjust the paths to match your setup):
```
PATH=/usr/bin:/bin:/usr/local/bin
0 */4 * * * bash -l -c "cd /fslhome/<absolute path>/atomate/scratch; module purge; source /fslhome/<absolute path>/atomate/atomate_env/bin/activate; qlaunch rapidfire -m 10 --nlaunches 0 &>> /fslhome/<absolute path>/atomate/logs/cron_postprocess.txt"
```
3. Do a happy dance

## More detailed explanation:
1. In the bash terminal, run `crontab -e`. If this is your first time setting up a crontab, it will open a blank file.
2. On the supercomputer, it defaults to opening the file with the vi text editor. If you prefer to use nano, simply run `export EDITOR="nano"` in the terminal before editing the crontab.
   - Some basic vi commands: type `i` to enter insert mode (where you can type into the document), press esc to exit insert mode, and then type `:wq` and hit return to save and exit. 
4. `squeue` is not found on the PATH for cron (it only has `/usr/bin` and `/bin`, where we need `/usr/local/bin` as well), so we edit the path for cron by putting `PATH=/usr/bin:/bin:/usr/local/bin` as the first line.
5. The values placed in `* * * * *` determine when/how often a given command runs. See [here](https://crontab.guru/examples.html) for detailed examples on how to set it up for the time you want.
6. We can run a series of commands in between the "" as if they were being run on the bash terminal. Cron is beautifully dumb, so you have to spell everything out. Separate commands with `;`
7. Cron hides the output that would be printed to the terminal from the commands. To store that output somewhere (which is extremely helpful in debugging), put `&>>` and then the file name that you with the ouput to be saved to. 
