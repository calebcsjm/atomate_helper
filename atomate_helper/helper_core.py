from pymatgen.ext.matproj import MPRester

# get the API Key
with open("api_key.txt",'r') as filename:
    API_KEY = filename.readlines()[0]

def get_pretty_formula(mp_id):
    '''Given a mp-id (str), queries the MP Database and returns the corresponding pretty formula (str)'''

    with MPRester(API_KEY) as m:
        structure = m.query(criteria={"task_id": mp_id}, properties=["pretty_formula"])

    return structure[0]["pretty_formula"]

def get_material_ids(pretty_formula):
    """ Function that queries the materials project database for all the materials ids matching a given pretty formula

    Parameters:
        pretty_formula (str): The pretty formula for the compound, for example 'NiS'

    Returns:
        material_ids (list): a string list of the material ids for the compound, for example ['mp-594', 'mp-1547']

    """

    material_ids = []

    with MPRester(API_KEY) as m:
        #gets all the materials id's (mp-___) from the MP for the given compound
        material_data = m.query(criteria={"pretty_formula": pretty_formula}, properties=["task_id"])

        #extracts all the materials id's from the dictionary returned by the query
        for entry in material_data:
            material_ids.append(entry['task_id'])

    return material_ids

def get_material_id_count(pretty_formulas):
    """ Function that determines the number of structures in the materials database for a given pretty formula,
    and prints the number for each. 
    
    Parameters:
        pretty_formulas (str list): a list of pretty formulas. Ex. ['NiS', 'ZrO2']
    Returns:
        None
    
    """
    
    structure_count = {}

    for pretty_formula in pretty_formulas:
        material_ids = []

        with MPRester(API_KEY) as m:
            #gets all the materials id's (mp-___) from the MP for the given compound
            material_data = m.query(criteria={"pretty_formula": pretty_formula}, properties=["task_id"])

            #extracts all the materials id's from the dictionary returned by the query
            for entry in material_data:
                material_ids.append(entry['task_id'])

            structure_count[pretty_formula] = len(material_ids)
    
    print(structure_count)