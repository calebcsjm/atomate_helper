from helper.core import get_material_ids
from fireworks import LaunchPad
from atomate.vasp.workflows.presets.core import wf_dielectric_constant

def add_dielectric_wflows(pretty_formulas, launchpad, workflow_cap=100):
    """ Adds dielectric workflows for each material in a list of inputs, and then returns a list with pertinant information

    Parameters:
        pretty_formulas (list): a list of compounds with their pretty formulas. Ex: ['NiS', 'MgO']
        launchpad (object): A launchpad (link to MongoDB) created by the user
        workflow_cap (int): To many connections can cause mongo to crash, so a cap has been added to help users avoid that

    Returns:
        added_run_info(str list): contains the firetask id, name, and material_id for each workflow added

    """

    total_wflows_added = 0
    added_run_info = []

    #gets all the material ids for the given pretty formulas
    for formula in pretty_formulas:
        material_ids = get_material_ids(formula)

        #first, test to ensure we haven't added to many at once
        if (total_wflows_added + len(material_ids)) > workflow_cap:
            print('''Max number of workflows ({}) exceeded. To avoid crashing MongoDB, please wait for these to finish before adding any more. Resume with formula: {}'''.format(workflow_cap, formula))
            return

        for material_id in material_ids:
            #import the structure from the materials database
            with MPRester() as mpr:
                struct = mpr.get_structure_by_material_id(material_id)

            # create and add the Workflow
            wf = wf_dielectric_constant(struct)
            try:
                task_ids_map = launchpad.add_wf(wf)
            except:
                print("Workflow was not added to the workflow. Please confirm that you have created the launpad in the form:",
                'lp = LaunchPad(host="your_hostname", port=27017, \
                name="db_name", username="your_username", \
                password="your_password", ssl="true", authsource="admin")')

            total_wflows_added += 1

            #get the firetask ids
            task_ids = list(task_ids_map.values())

            #creates a string with the task_ids, material id, and workflow
            temp_string = ''
            workflow_name = 'dielectric'
            for count, value in enumerate(task_ids):
                temp_string += str(value)
                if count < (len(task_ids) - 1):
                    temp_string += "/"
                else:
                    temp_string += ": " + formula + " " + material_id + "  " + workflow_name

            #add the text string to the end of the list
            added_run_info.append(temp_string)

    return added_run_info
