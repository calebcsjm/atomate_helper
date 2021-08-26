This is meant as a supplement to the instructions found on the [Atomate Installation page](https://atomate.org/installation.html), based on errors I encountered and ways that I found around them. Some of these errors may have been unique to me, as I am not yet an experienced programmer. I will provide the final setup of my files at the end. 

**MongoDB Section:**
1. Set up the MongoDB - see the mongodb_setup file in this folder.

**Create a Python 3 virtual environment Section:**

2. Virtual Env - Modules:
   - Instead of using the default modules on the supercomputer, purge the modules and then load python/3.8 and gcc/9 before creating the virtual environment for Atomate (you can run `module list` to see which modules are currently installed, `module purge` to remove them, `module avail` to see which ones are available, and then `module load <<module_name>>` to load new ones) 
   - Make sure pip is up to date, if not run `pip install --upgrade pip`

**Configure database connections and computing center parameters Section:**

3. Db.json file:
   - The port is just 27017
   - Add the following line to the end `"authsource":"admin"`. Note: This is the line for setting up a MongoDb Cloud connnection - it may be different for running a server on Superhomer or a personal computer
   - The hostname can be somewhat particular. I found this explanation on another site - "Use this connection string format: `mongodb+srv://<cluster_name>.mongodb.net`. If you have a cluster's connection string with servers' names like: cluster0-shard-00-00-jxeqq.mongodb.net, modify your server's name by removing shards' info so your <cluster_name> looks like this: cluster0.jxeqq.mongodb.net"
    - ***NOTE:*** The system administrators for the supercomputer will have to add the IP address of the cluster to their whitelist in order for it to connect while running jobs
      - For my server, what I ended up putting in the db.json file was `mongodb+srv://cluster0.9esxz.mongodb.net`
      - What we sent to the RC Office were actually just the following web addresses: `cluster0-shard-00-00.9esxz.mongodb.net`,`cluster0-shard-00-01.9esxz.mongodb.net`, and `cluster0-shard-00-02.9esxz.mongodb.net`. We got those from error messages on the terminal when it failed to connect to the database.
4. My_fireworker.yaml
    - The vasp_cmd line can be tricky. What ended up working was `srun /fslhome/glh43/fsl_groups/fslg_msg_code/bin/vasp6_mpi` (srun is the command to run it in parallel, and then the second part is the path to the executable). Consequently, that line is NOT needed in the my_qadapter.yaml file, or in the template file if you choose to set one of those up. 
5. My_launchpad.yaml
    - Add the following two lines to the end: 
      - `ssl: True`
      - `authsource: admin`
    - If you don’t, you will likely get a connection error that says “pymongo.errors.ServerSelectionTimeoutError: connection closed”
6. My_qadapter.yaml
   - In order to include more specifics in the SLURM script that launches VASP, add the SLURM_template.txt to your config directory. Reference it as a template (see below), and then add the information for mem or memory per cpu. The SLURM_template.txt can copied from Github: [SLURM Template](https://github.com/materialsproject/fireworks/blob/main/fireworks/user_objects/queue_adapters/SLURM_template.txt). However, several lines needed to be added, so please see the examples below for full details. 
   - The exact specifications for the runs may depend on the size of job you are using. I would recommend using “nodes: 1,” “ntasks: 8,” “mem: 32G,” and “walltime: 24:00:00,” as a starting point, but feel free to adjust as needed. You can view the resources available on each computing node (including memory per cpu) here: [Computing Resources](https://rc.byu.edu/documentation/resources)

**Configure pymatgen Section:**

7. Pymatgen and Potcars: I recommend viewing the pymatgen instructions at [POTCAR Setup](https://pymatgen.org/installation.html#potcar-setup), which are more detailed than those at on the atomate website. Note: if you copy the potpaw_PBE file, you will have to run the `pmg config` command on the directory ABOVE potpaw_PBE, or it won't do it properly. For example, if you copy the potpaw_PBE folder in a folder called potcarTempStorage, you would run `pmg config -p potcarTempStorage <MY_PSP>`. POTCARs are legally protected, so you will need to access them through your research advisor's VASP license. 
8. Materials API Key: See the following instructions from the bottom of the pymatgen docs Usage section:  [API Setup](https://pymatgen.org/usage.html#setting-the-pmg-mapi-key-in-the-config-file)  This personal key can be generated on the Materials project website.

**Additional Notes:**

9. Bash Profile:
    - If you don’t have one already, in your home directory create a file `.bash_profile`
    - Add `ulimit -s unlimited` to it – that prevents VASP from having segmentation errors
    - Also add `export FW_CONFIG_FILE=/<path>/atomate/config/FW_config.yaml,` or you will get connection errors with the mongo database
10. [Errno 101] Network is unreachable: 
    - If you are getting this in the FW_job<<number>>.error file, then the system administrators have not yet enabled access to the cloud database – see the db.json section
11. See the crontab_setup file on how to set up a crontab to launch your jobs automatically


**Full text for Files:**  
I bolded lines that are added or altered from those suggested in the installation guide. Replace the values with the information for you database - if your database is named *dielectric_runs*, then replace *database_name* in the db.json file with *dielectric_runs* (preserving quotation marks where appropriate). 

db.json:
<pre><code>{
	"host":"mongodb+srv://cluster0.9esxz.mongodb.net",
	"port":27017,
	"database":"database_name",
	"collection":"collection_name",
	"admin_user":"admin_username",
	"admin_password":"admin_password",
	"readonly_user":"read_user_name",
	"readonly_password":"user_password",
	"aliases":{},
	<b><i>"authsource":"admin"</i></b>
}
</code></pre>

my_fireworker.yaml:
<pre><code>name: worker_name
category: ''
query: '{}'
env:
    db_file: /<<path>>/atomate/config/db.json
    <b><i>vasp_cmd: srun /fslhome/glh43/fsl_groups/fslg_msg_code/bin/vasp6_mpi</i></b>
scratch_dir: null
</code></pre>

my_launchpad.yaml:
<pre><code>host: mongodb+srv://cluster0.9esxz.mongodb.net
port: 27017
name: database_name
username: admin_username
password: admin_password
ssl_ca_file: null
logdir: null
strm_lvl: INFO
user_indices: []
wf_user_indices: []
<b><i>ssl: True
authsource: admin</i></b>
</code></pre>

my_qadapter.yaml: 
<pre><code>_fw_name: CommonAdapter
_fw_q_type: SLURM
<b><i>_fw_template_file: /path/atomate/config/SLURM_template.txt</i></b>
rocket_launch: rlaunch -c /path/atomate/config rapidfire
<b><i>nodes: 1
ntasks: 8
mem: 32G</i></b>
walltime: 24:00:00
queue: null
account: null
job_name: null
pre_rocket: null
post_rocket: null
logdir: /path/atomate/logs
</code></pre>

	
SLURM_template.txt:
<pre><code>#!/bin/bash -l

#SBATCH --nodes=$${nodes}
#SBATCH --ntasks=$${ntasks}
#SBATCH --ntasks-per-node=$${ntasks_per_node}
#SBATCH --ntasks-per-core=$${ntasks_per_core}
#SBATCH --core-spec=$${core_spec}
#SBATCH --exclude=$${exclude_nodes}
#SBATCH --cpus-per-task=$${cpus_per_task}
#SBATCH --gpus-per-task=$${gpus_per_task}
#SBATCH --gres=$${gres}
#SBATCH --qos=$${qos}
#SBATCH --time=$${walltime}
#SBATCH --time-min=$${time_min}
#SBATCH --partition=$${queue}
#SBATCH --account=$${account}
#SBATCH --job-name=$${job_name}
#SBATCH --license=$${license}
#SBATCH --output=$${job_name}-%j.out
#SBATCH --error=$${job_name}-%j.error
#SBATCH --constraint=$${constraint}
#SBATCH --signal=$${signal}
#SBATCH --mem=$${mem}
#SBATCH --mem-per-cpu=$${mem_per_cpu}
#SBATCH --mail-type=$${mail_type}
#SBATCH --mail-user=$${mail_user}
<b><i>#SBATCH -C 'avx2'

module purge </i></b>
$${pre_rocket}
cd $${launch_dir}
$${rocket_launch}
$${post_rocket} </code></pre>
