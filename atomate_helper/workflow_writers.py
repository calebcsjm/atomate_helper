from helper_core import get_material_ids
from fireworks import LaunchPad
from pymatgen.ext.matproj import MPRester
import numpy as np

#import prebuilt workflows
from atomate.vasp.workflows.presets.core import wf_dielectric_constant
from atomate.vasp.workflows.presets.core import wf_elastic_constant
from atomate.vasp.workflows.presets.core import wf_gibbs_free_energy
from atomate.vasp.workflows.presets.core import wf_bandstructure


def print_launchpad_error():
    '''Function to print error, to save space in code'''
    
    print("Error: Workflow was not added to the database. Please confirm that you have created the launchpad in the form:",
                'lp = LaunchPad(host="your_hostname", port=27017, name="db_name", username="your_username", password="your_password", ssl="true", authsource="admin")')
    

def added_workflow_string_converter(task_ids_map, workflow_name, mp_id, formula=""):
    ''' Creates a string containing the task ids, workflow name, mp-id, and the formula of the material (if provided)
    
    Parameters:
        task_ids_map (dict): the value returned by the launchpad.add_wf() command
        workflow_name (str): the name of the workflow. Ex: 'dielectric', 'gibbs', 'elastic'
        mp_id (str): the mp-id. Ex. 'mp-594'
        formula (str): if the pretty formula is available, include it. Ex: 'NiS'
        
    Returns:
        added_info (str): a formated string containing the information stripped from the variables provided
        
    '''
    
    added_info = ''
    
    #get the firetask ids
    task_ids = list(task_ids_map.values())
    for count, value in enumerate(task_ids):
        added_info += str(value)
        if count < (len(task_ids) - 1):
            added_info += "/"
        else: 
            added_info += ": " + formula + " " + mp_id + "  " + workflow_name
            
    return added_info


def add_dielectric_mpid(mp_ids, launchpad):
    '''Adds dielectric workflows for each mp-id in a list of inputs, and then returns a list with pertinant information
    
    Parameters:
        mp_ids (str lst): list of mp-ids. Ex: ['mp-594', 'mp-1547']
        launchpad (object): A launchpad (link to MongoDB) created by the user
        
    Returns:
        added_run_info(str list): contains the firetask id and material_id for each workflow added
        
    '''
    
    added_run_info = []
    
    for mp_id in mp_ids:
        #import the structure from the materials database
        with MPRester() as mpr:
            struct = mpr.get_structure_by_material_id(mp_id)

        # create and add the Workflow
        wf = wf_dielectric_constant(struct)
        try:
            task_ids_map = launchpad.add_wf(wf)
        except:
            print_launchpad_error()
            return

        #create the info string for this workflow
        added_info = added_workflow_string_converter(task_ids_map, 'dielectric', mp_id)
        added_run_info.append(added_info)
        
    return added_run_info
    
    
def add_dielectric_prettyform(pretty_formulas, launchpad, workflow_cap=100):
    """ Adds dielectric workflows for each material in a list of inputs, and then returns a list with pertinant information

    Parameters:
        pretty_formulas (list): a list of compounds with their pretty formulas. Ex: ['NiS', 'MgO']
        launchpad (object): A launchpad (link to MongoDB) created by the user
        workflow_cap (int): Too many connections can cause mongo to crash, so a cap has been added to help users avoid that

    Returns:
        added_run_info(str list): contains the firetask id, name, and material_id for each workflow added

    """

    total_wflows_added = 0
    added_run_info = []

    #gets all the material ids for the given pretty formulas
    for formula in pretty_formulas:
        mp_ids = get_material_ids(formula)

        #first, test to ensure we haven't added too many at once
        if (total_wflows_added + len(mp_ids)) > workflow_cap:
            print('''Max number of workflows ({}) exceeded. To avoid crashing MongoDB, please wait for these to finish before adding any more. Resume with formula: {}'''.format(workflow_cap, formula))
            return

        for mp_id in mp_ids:
            #import the structure from the materials database
            with MPRester() as mpr:
                struct = mpr.get_structure_by_material_id(mp_id)

            # create and add the Workflow
            wf = wf_dielectric_constant(struct)
            try:
                task_ids_map = launchpad.add_wf(wf)
            except:
                print_launchpad_error()
                return

            total_wflows_added += 1
            
            #create the info string for this workflow
            added_info = added_workflow_string_converter(task_ids_map, 'dielectric', mp_id, formula)
            added_run_info.append(added_info)

    return added_run_info


def add_gibbs_mpid(mp_ids, launchpad):
    '''Adds gibbs workflows for each mp-id in a list of inputs, and then returns a list with pertinant information
    
    Parameters:
        mp_ids (str lst): list of mp-ids. Ex: ['mp-594', 'mp-1547']
        launchpad (object): A launchpad (link to MongoDB) created by the user
        
    Returns:
        added_run_info(str list): contains the firetask id and material_id for each workflow added
        
    '''
    
    added_run_info = []
    
    for mp_id in mp_ids:
        #import the structure from the materials database
        with MPRester() as mpr:
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
             "DEFORMATIONS": deformations}
        
        #create workflow and add to mongodb
        wf = wf_gibbs_free_energy(struct, c)
        try:
            task_ids_map = launchpad.add_wf(wf)
        except:
            print_launchpad_error()
            return

        #create the info string for this workflow
        added_info = added_workflow_string_converter(task_ids_map, 'gibbs', mp_id)
        added_run_info.append(added_info)
        
    return added_run_info

def add_bandstucture_mpid(mp_ids, launchpad):
    '''Adds bandstructure workflows for each mp-id in a list of inputs, and then returns a list with pertinant information
    
    Parameters:
        mp_ids (str lst): list of mp-ids. Ex: ['mp-594', 'mp-1547']
        launchpad (object): A launchpad (link to MongoDB) created by the user
        
    Returns:
        added_run_info(str list): contains the firetask id and material_id for each workflow added
        
    '''
    
    added_run_info = []
    
    for mp_id in mp_ids:
        #import the structure from the materials database
        with MPRester() as mpr:
            struct = mpr.get_structure_by_material_id(mp_id)

        # create and add the Workflow
        wf = wf_bandstructure(struct)
        try:
            task_ids_map = launchpad.add_wf(wf)
        except:
            print_launchpad_error()
            return

        #create the info string for this workflow
        added_info = added_workflow_string_converter(task_ids_map, 'bandstructure', mp_id)
        added_run_info.append(added_info)
        
    return added_run_info

def add_elastic_mpid(mp_ids, launchpad):
    '''Adds elastic workflows for each mp-id in a list of inputs, and then returns a list with pertinant information
    
    Parameters:
        mp_ids (str lst): list of mp-ids. Ex: ['mp-594', 'mp-1547']
        launchpad (object): A launchpad (link to MongoDB) created by the user
        
    Returns:
        added_run_info(str list): contains the firetask id and material_id for each workflow added
        
    '''
    
    added_run_info = []
    
    for mp_id in mp_ids:
        #import the structure from the materials database
        with MPRester() as mpr:
            struct = mpr.get_structure_by_material_id(mp_id)

        # create and add the Workflow
        wf = wf_elastic_constant(struct)
        try:
            task_ids_map = launchpad.add_wf(wf)
        except:
            print_launchpad_error()
            return

        #create the info string for this workflow
        added_info = added_workflow_string_converter(task_ids_map, 'elastic', mp_id)
        added_run_info.append(added_info)
        
    return added_run_info

