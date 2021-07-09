Some errors encountered with atomate:

- `Validation failed: VasprunXMLValidator`
  - If the .error file for the workflow contains the above error, then that means the vasp run failed. Check the std_err.txt or vasp.out files in the Launcher to see more details and address how to solve it

- Workflows always in state: RUNNING (even after walltime has been exceeded)
  - you can run `lpad detect_lostruns`, and it will report all the workflows that are running without having any activity in the last 4 hours
  - You can mark these as FIZZLED using `lpad detect_lostruns --fizzle` (which marks them all as FIZZLED) or `lpad detect_lostruns --rerun` (which marks them as FIZZLED and then reruns them)
  - Based on my current understanding, this happens when the terminal is closed or times out before the workflows are complete. Consequently, after you run `qlaunch rapidfire`, you can't close the terminal (see "3.3.3 Running the workflows" at [this site](https://github.com/quanshengwu/MPWorks))
  - See the [Dealing With Failures and Crashes](https://materialsproject.github.io/fireworks/failures_tutorial.html#) tutorial in the FireWorks documentation for more information