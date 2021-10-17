from helper_core import get_material_ids, get_pretty_formula
from pymatgen.ext.matproj import MPRester
import numpy as np
import pandas as pd

# import prebuilt workflows
from atomate.vasp.workflows.presets.core import wf_dielectric_constant
from atomate.vasp.workflows.presets.core import wf_elastic_constant
from atomate.vasp.workflows.presets.core import wf_gibbs_free_energy
from atomate.vasp.workflows.presets.core import wf_bandstructure

# import incar modifier
from atomate.vasp.powerups import add_modify_incar

# get API Key
with open("api_key.txt",'r') as filename:
    API_KEY = filename.readlines()[0]

def print_launchpad_error():
    '''Function to print error, to save space in code'''
    
    print("Error: Workflow was not added to the database. Please confirm that you have created the launchpad in the form:",
          'lp = LaunchPad(host="your_hostname", port=27017, name="db_name", username="your_admin_username", password="your_admin_password", ssl="true", authsource="admin")',
         "You will also need to include 'from fireworks import LaunchPad' above that.")
    

def added_workflow_list_converter(task_ids_map, workflow_name, mp_id, formula=""):
    ''' Creates a string containing the task ids, workflow name, mp-id, and the formula of the material (if provided)
    
    Parameters:
        task_ids_map (dict): the value returned by the launchpad.add_wf() command
        workflow_name (str): the name of the workflow. Ex: 'dielectric', 'gibbs', 'elastic'
        mp_id (str): the mp-id. Ex. 'mp-594'
        formula (str): if the pretty formula is available, include it. Ex: 'NiS'
        
    Returns:
        added_info (str list): a list containing the information stripped from the variables provided
        
    '''
    
    added_info = []
    
    #get the firetask ids
    task_ids = list(task_ids_map.values())
    task_range = str(task_ids[0]) + "-" + str(task_ids[-1])

    if formula == "":
        formula = get_pretty_formula(mp_id)

    added_info.extend([task_range, formula, mp_id, workflow_name])
            
    return added_info

def check_size_add_wf(structure, orig_wf, launchpad):
    ''''Checks if the given structure has fewer than 30 elements, if it does, changes the INCAR settings
    
    Parameters:
        structure - a pymatgen type structure
        orig_wf - The original workflow that was created for the structure
        launchpad - the launchpad
    Returns:
        task_ids_map - the map containing the task ids
        
    '''

    if len(structure) > 30:
        try:
            task_ids_map = launchpad.add_wf(orig_wf)
        except:
            print_launchpad_error()
            return
    else:
        # small structures should have lreal set to false: See  https://www.vasp.at/wiki/index.php/LREAL 
        modified_wf = add_modify_incar(orig_wf, modify_incar_params={'incar_update': {'LREAL': "False"}})
        try:
            task_ids_map = launchpad.add_wf(modified_wf)
        except:
            print_launchpad_error()
            return

    return task_ids_map

def add_dielectric_mpid(mp_ids, launchpad):
    '''Adds dielectric workflows for each mp-id in a list of inputs, and then returns a list with pertinant information
    
    Parameters:
        mp_ids (str lst): list of mp-ids. Ex: ['mp-594', 'mp-1547']
        launchpad (object): A launchpad (link to MongoDB) created by the user
        
    Returns:
        df: A pandas dataframe containing the firetask ids and material_id for each workflow added
        
    '''
    
    added_run_info = []
    
    for mp_id in mp_ids:
        #import the structure from the materials database
        with MPRester(API_KEY) as mpr:
            struct = mpr.get_structure_by_material_id(mp_id)

        # create the Workflow
        wf = wf_dielectric_constant(struct)
        # checks the size, then addds the workflow
        task_ids_map = check_size_add_wf(struct, wf, launchpad)
        # quits if it was not added successfully. 
        if task_ids_map is None:
            return

        #create the info list for this workflow
        added_info = added_workflow_list_converter(task_ids_map, 'dielectric', mp_id)
        added_run_info.append(added_info)

    df = pd.DataFrame(added_run_info, columns=["Task ID Range", "Formula", "mp-id", "Workflow Type"])
    print(df)

    return df
    
    
def add_dielectric_prettyform(pretty_formulas, launchpad, workflow_cap=100):
    """ Adds dielectric workflows for each material in a list of inputs, and then returns a list with pertinant information

    Parameters:
        pretty_formulas (list): a list of compounds with their pretty formulas. Ex: ['NiS', 'MgO']
        launchpad (object): A launchpad (link to MongoDB) created by the user
        workflow_cap (int): Too many connections can cause mongo to crash, so a cap has been added to help users avoid that

    Returns:
        df: A pandas dataframe containing the firetask ids, formula, and material_id for each workflow added

    """

    total_wflows_added = 0
    added_run_info = []

    #gets all the material ids for the given pretty formulas
    for formula in pretty_formulas:
        mp_ids = get_material_ids(formula)

        #first, test to ensure we haven't added too many at once
        if (total_wflows_added + len(mp_ids)) > workflow_cap:
            print('''Max number of workflows ({}) exceeded. To avoid crashing MongoDB, please wait for these to finish before adding any more. Resume with formula: {}'''.format(workflow_cap, formula))
            df = pd.DataFrame(added_run_info, columns=["Task ID Range", "Formula", "mp-id", "Workflow Type"])
            print(df)
            return df

        for mp_id in mp_ids:
            #import the structure from the materials database
            with MPRester(API_KEY) as mpr:
                struct = mpr.get_structure_by_material_id(mp_id)

            # create and add the Workflow
            wf = wf_dielectric_constant(struct)
            # checks the size, then addds the workflow
            task_ids_map = check_size_add_wf(struct, wf, launchpad)
            # quits if it was not added successfully. 
            if task_ids_map is None:
                return

            total_wflows_added += 1
            
            #create the info list for this workflow
            added_info = added_workflow_list_converter(task_ids_map, 'dielectric', mp_id, formula)
            added_run_info.append(added_info)

    df = pd.DataFrame(added_run_info, columns=["Task ID Range", "Formula", "mp-id", "Workflow Type"])
    print(df)

    return df


def add_gibbs_mpid(mp_ids, launchpad):
    '''Adds gibbs workflows for each mp-id in a list of inputs, and then returns a list with pertinant information
    
    Parameters:
        mp_ids (str lst): list of mp-ids. Ex: ['mp-594', 'mp-1547']
        launchpad (object): A launchpad (link to MongoDB) created by the user
        
    Returns:
        df: A pandas dataframe containing the firetask ids and material_id for each workflow added
        
    '''
    
    added_run_info = []
    
    for mp_id in mp_ids:
        #import the structure from the materials database
        with MPRester(API_KEY) as mpr:
            struct = mpr.get_structure_by_material_id(mp_id)

        # Set up the deformation matricies, where each deformation is a 3x3 list of strains.
        # There will be 7 structures between +/- 10% volume. Note that the 1/3 power is so
        # that we scale each direction by (x+1)^(1/3) and the total volume by (x+1).
        deformations = [(np.eye(3)*((1+x)**(1.0/3.0))).tolist() for x in np.linspace(-0.1, 0.1, 7)]

        # Create the configurations dictionary, defining the temperature range,
        # Poisson ratio (from experiments or the Materials Project), turning on consideration
        # of anharmonic contributions, and finally the deformation matrix describing points
        # on the energy vs. volume curve.
        c = {"T_MIN": 10, "T_STEP": 10, "T_MAX": 2000,
             "POISSON": 0.20, "ANHARMONIC_CONTRIBUTION": True,
             "DEFORMATIONS": deformations, "QHA_TYPE":"phonopy"}
        
        # I added the "qha_type" above - the default appears to be "debye_model" (see line 466 at https://github.com/hackingmaterials/atomate/blob/main/atomate/vasp/workflows/presets/core.py)
        
        #create workflow and add to mongodb
        wf = wf_gibbs_free_energy(struct, c)
        # checks the size, then addds the workflow
        task_ids_map = check_size_add_wf(struct, wf, launchpad)
        # quits if it was not added successfully. 
        if task_ids_map is None:
            return


        #create the info list for this workflow
        added_info = added_workflow_list_converter(task_ids_map, 'gibbs', mp_id)
        added_run_info.append(added_info)
        
    df = pd.DataFrame(added_run_info, columns=["Task ID Range", "Formula", "mp-id", "Workflow Type"])
    print(df)

    return df

def add_bandstucture_mpid(mp_ids, launchpad):
    '''Adds bandstructure workflows for each mp-id in a list of inputs, and then returns a list with pertinant information
    
    Parameters:
        mp_ids (str lst): list of mp-ids. Ex: ['mp-594', 'mp-1547']
        launchpad (object): A launchpad (link to MongoDB) created by the user
        
    Returns:
        df: A pandas dataframe containing the firetask ids and material_id for each workflow added
        
    '''
    
    added_run_info = []
    
    for mp_id in mp_ids:
        #import the structure from the materials database
        with MPRester(API_KEY) as mpr:
            struct = mpr.get_structure_by_material_id(mp_id)

        # create and add the Workflow
        wf = wf_bandstructure(struct)
        # checks the size, then addds the workflow
        task_ids_map = check_size_add_wf(struct, wf, launchpad)
        # quits if it was not added successfully. 
        if task_ids_map is None:
            return

        #create the info list for this workflow
        added_info = added_workflow_list_converter(task_ids_map, 'bandstructure', mp_id)
        added_run_info.append(added_info)
        
    df = pd.DataFrame(added_run_info, columns=["Task ID Range", "Formula", "mp-id", "Workflow Type"])
    print(df)

    return df

def add_elastic_mpid(mp_ids, launchpad):
    '''Adds elastic workflows for each mp-id in a list of inputs, and then returns a list with pertinant information
    
    Parameters:
        mp_ids (str lst): list of mp-ids. Ex: ['mp-594', 'mp-1547']
        launchpad (object): A launchpad (link to MongoDB) created by the user
        
    Returns:
        df: A pandas dataframe containing the firetask ids and material_id for each workflow added
        
    '''
    
    added_run_info = []
    
    for mp_id in mp_ids:
        #import the structure from the materials database
        with MPRester(API_KEY) as mpr:
            struct = mpr.get_structure_by_material_id(mp_id)

        # create and add the Workflow
        wf = wf_elastic_constant(struct)
        # checks the size, then addds the workflow
        task_ids_map = check_size_add_wf(struct, wf, launchpad)
        # quits if it was not added successfully. 
        if task_ids_map is None:
            return

        #create the info list for this workflow
        added_info = added_workflow_list_converter(task_ids_map, 'elastic', mp_id)
        added_run_info.append(added_info)
        
    df = pd.DataFrame(added_run_info, columns=["Task ID Range", "Formula", "mp-id", "Workflow Type"])
    print(df)

    return df


def mpids_from_fizzled_runs(df, fizzled_runs):
    '''This function was developed to deal with issues using the "lpad rerun_fws -s FIZZLED" command
    on the supercomputer. If that starts to work, this won't be necessary. Using the dataframe returned 
    when you initially added the workflows, and the fw_ids returned from running "lpad get_wflows -s FIZZLED -d ids"
    on the supercomputer, it returns the list of mp-ids of the fizzled workflows. Can also be used to 
    get the mpids for runs of any state, by using the "lpad get_wflows -s ____ -d ids" command to get the respective
    workflow ids. 
    
    Parameters:
        df (Pandas dataframe): Dataframe returned by add_dielectric_mpid function when you first added 
            the workflows
        fizzled_runs (int list): The list of fw_ids that failed on the supercomputer
    Returns:
        ids_to_rerun (str list): The mp-ids of the structures that need to be rerun
    
    '''
    
    ids_to_rerun = []

    for fw_id in fizzled_runs:
    # search for a matching fw_id in the dataframe of launched runs
        for range_interval in df["Task ID Range"].tolist():

            # get the high and low for the range
            range_list = range_interval.split("-")
            low = int(range_list[0])
            high = int(range_list[1])

            # add the mp-id to the list if it was fizzled
            if low <= fw_id <= high:
                # get the mp-id
                mp_id = df.loc[df['Task ID Range'] == range_interval]["mp-id"].tolist()[0]
                ids_to_rerun.append(mp_id)
            
    return ids_to_rerun
