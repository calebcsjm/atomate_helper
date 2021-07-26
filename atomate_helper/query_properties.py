'''
This file contains an example function to query the database for a given property - the function can easily
be modified to get any other property simply by changing the 'the_material['dielectric']['epsilon_static']' portion
'''

from helper_core import get_material_ids
from atomate.vasp.database import VaspCalcDb
from pymatgen.core import Structure
import numpy as np

def get_epsilon_staticM_mpid(mp_ids, dbjson_path):
    ''' Returns the epsilon static matrices from a list of materials (mp-ids) in the materials collection of the mongodb
    
    Parameters:
        mp_id (str list): The mp_ids of the material in quesiton. Ex. ['mp-594', 'mp-91']
        dbjson_path (str): The path to your db.json file (which should be in the atomate/config folder). Ex. '/home/user/atomate/config/db.json'
        
    Returns:
        matrices (dict): A dictionary containing the mp-ids as keys and the epsilon static matrix as the value
        
    '''
    
    #connect to the materials collection
    atomate_db = VaspCalcDb.from_db_file(dbjson_path)
    materials_collection = atomate_db.db['materials']
    
    matrices = {}
    
    for mp_id in mp_ids:
        #find the material document with matching mp-id and extract the matrix
        the_material = materials_collection.find_one({'mpids': mp_id})
        try:
            epsilon_static_matrix = np.array(the_material['dielectric']['epsilon_static'])
            matrices[mp_id] = epsilon_static_matrix
        except:
            print(" KeyError: {} does not have the results of a dielectric run. If you believe this is an error, you may need to run the builder again.".format(mp_id))
                          
    return matrices

def get_epsilon_staticM_prettyform(pretty_formulas, dbjson_path):
    ''' Returns the epsilon static matrices from a list of materials (pretty formulas) in the materials collection of the mongodb
    
    Parameters:
        pretty_formulas (str list): The pretty formulas of the material in quesiton. Ex. ['NiS', 'ZrO2']
        dbjson_path (str): The path to your db.json file (which should be in the atomate/config folder). Ex. '/home/user/atomate/config/db.json'
        
    Returns:
        matrices (dict): A dictionary containing the mp-ids as keys and the epsilon static matrix as the value
        
    '''
    
    #get all the mp-ids
    mp_ids = []
    for pretty_formula in pretty_formulas:
        mp_ids.extend(get_material_ids(pretty_formula))
    
    return get_epsilon_staticM_mpid(mp_ids, dbjson_path)