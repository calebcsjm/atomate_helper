def get_material_ids(pretty_formula):
    """ Function that queries the materials project database for all the materials ids matching a given pretty formula

    Parameters:
        pretty_formula (str): The pretty formula for the compound, for example 'NiS'

    Returns:
        material_ids (list): a string list of the material ids for the compound, for example ['mp-594', 'mp-1547']

    """
    from pymatgen.ext.matproj import MPRester
    m = MPRester()

    material_ids = []

    #gets all the materials id's (mp-___) from the MP for the given compound
    material_data = m.query(criteria={"pretty_formula": pretty_formula}, properties=["task_id"])

    #extracts all the materials id's from the dictionary returned by the query
    for entry in material_data:
        material_ids.append(entry['task_id'])

    return material_ids
