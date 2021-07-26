This is meant as a supplement to the instructions found on the Atomate Installation page, based on errors I encountered and ways that I found around them. Some of these errors may have been unique to me, as I am not yet an experienced programmer. I will provide the final setup of my files at the end. 

1. Virtual Env - Modules:
   - Instead of using the default modules on the supercomputer, purge the modules and then load python/3.8 and gcc/9 before creating the virtual environment for Atomate (you can run `module list` to see which modules are currently installed, `module purge` to remove them, `module avail` to see which ones are available, and then `module load <<module_name>>` to load new ones)
3. Pip install the maggma package – it is a dependent package that does not get downloaded as part of atomate. 
4. Db.json file:
   - The port is just 27017
   - Add the following line to the end `"authsource":"admin"`
   - The hostname can be somewhat particular. I found this explanation on another site: Use this connection string format:mongodb+srv://:@<cluster_name>.mongodb.net/. If you have a cluster's connection string with servers' names like:cluster0-_shard-00-00-_jxeqq.mongodb.net, modify your server's name by removing shards' info so your <cluster_name> looks like this: cluster0-jxeqq.mongodb.net
    - ***NOTE:*** The system administrators for the supercomputer will have to add the IP address of the cluster to their whitelist in order for it to connect while running jobs
4. My_fireworker.yaml
    - The vasp_cmd line was somewhat confusing. What ended up working was providing the path to the executable for vasp, which in my case was /fslhome/glh43/fsl_groups/fslg_msg_code/bin/vasp6_mpi. Consequently, that line is NOT needed in the my_qadapter.yaml file, or in the template file if you choose to set one of those up. 
5. My_launchpad.yaml
    - Add the following two lines to the end: 
      - `ssl: True`
      - `authsource: admin`
    - If you don’t, you will likely get a connection error that says “pymongo.errors.ServerSelectionTimeoutError: connection closed”
6. My_qadapter.yaml
   - The default file in the installation tutorial does not contain the amount of memory requested per cpu, which is a requirement for submission on the BYU system (and it also may have needed ntasks and nodes). 
   - One way to get around that is to add the SLURM_template.txt to your config directory, reference it as a template, and then add the information for the memory per cpu. The SLURM_template.txt can copied from Github: [SLURM Template](https://github.com/materialsproject/fireworks/blob/main/fireworks/user_objects/queue_adapters/SLURM_template.txt)
   - For further clarification, see the full text below. 
   - The exact specifications for the runs may depend on the size of job you are using. I typically use “nodes: 1,” “ntasks: 4,” “mem-per-cpu: 8G,” and “walltime: 24:00:00,” but feel free to adjust as needed. You can view the resources available on each computing node (including memory per cpu) here: [Computing Resources](https://rc.byu.edu/documentation/resources)
7. Pymatgen and Potcars: I recommend viewing the pymatgen instructions at [POTCAR Setup](https://pymatgen.org/installation.html#potcar-setup), which are more detailed than those at on the atomate website. Note: if you copy the potpaw_PBE file, you will have to run the `pmg config` command on the directory ABOVE potpaw_PBE, or it won't do it properly. For example, if you copy the potpaw_PBE folder in a folder called potcarTempStorage, you would run `pmg config -p potcarTempStorage <MY_PSP>`
8. Materials API Key: See the following instructions from the bottom of the pymatgen docs Usage section:  [API Setup](https://pymatgen.org/usage.html#setting-the-pmg-mapi-key-in-the-config-file)  This personal key can be generated on the Materials project website.
9. Bash Profile:
    - If you don’t have one already, in your home directory create a file `.bash_profile`
    - Add `ulimit -s unlimited` to it – that prevents VASP from having segmentation errors
    - Also add `export FW_CONFIG_FILE=/<path>/atomate/config/FW_config.yaml,` or you will get connection errors with the mongo database
10. [Errno 101] Network is unreachable: 
    - If you are getting this in the FW_job<<number>>.error file, then the system administrators have not yet enabled access to the cloud database – see the db.json section


**Full text for Files:**  
I bolded lines that are added or altered from those suggested in the installation guide. Replace the values with the information for you database - if your database is named *dielectric_runs*, then replace *database_name* in the db.json file with *dielectric_runs* (preserving quotation marks where appropriate). 

Db.json:
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

My_fireworker.yaml:
<pre><code>name: worker_name
category: ''
query: '{}'
env:
    db_file: /<<path>>/atomate/config/db.json
    <b><i>vasp_cmd: srun /fslhome/glh43/fsl_groups/fslg_msg_code/bin/vasp6_mpi</i></b>
scratch_dir: null
</code></pre>

My_launchpad.yaml:
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

My_qadapter.yaml: 
<pre><code>_fw_name: CommonAdapter
_fw_q_type: SLURM
<b><i>_fw_template_file: /path/atomate/config/SLURM_template.txt</i></b>
rocket_launch: rlaunch -c /path/atomate/config rapidfire
<b><i>nodes: 1
ntasks: 4
mem_per_cpu: 8G</i></b>
walltime: 24:00:00
queue: null
account: null
job_name: null
pre_rocket: null
post_rocket: null
logdir: /path/atomate/logs
</code></pre>
