'''
This file contains an example function to query the database for a given property - the function can easily
be modified to get any other property simply by changing the 'the_material['dielectric']['epsilon_static']' portion
'''

from helper_core import get_material_ids
from atomate.vasp.database import VaspCalcDb
from pymatgen.core import Structure
import numpy as np
import pandas as pd

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

def query_materials_with_keyword(keyword, path_to_my_db_json):
    '''Given a keyword, returns all the materials with that keyword.

    Parameters:
        keyword (str): The keyword you wish to find
        path_to_my_db_json (str): the path to your db.sjon file, eg. '/home/calebh27/atomate/config/db.json'
    Returns:
        df: a pandas DataFrame containing some basic info on the materials with the keyword
    
    '''

    # set up the connection to the collection
    atomate_db = VaspCalcDb.from_db_file(path_to_my_db_json)
    materials_collection = atomate_db.db['materials']
    
    data = []

    # Find all the docs with the keyword
    materials_found = materials_collection.find({'keywords': keyword})

    for material in materials_found:
        mp_id = material["mpids"]
        # add match data to a data set (more can be added, as desired)
        data.append([material["formula_pretty"], mp_id[0], material["sg_symbol"], material["keywords"]])
    
    # convert data to a dataframe
    df = pd.DataFrame(data, columns=["Pretty Formula", "mp-id", "Space Group", "Keywords"])

    return df

def query_materials_by_id(mp_ids, path_to_my_db_json):
    '''Given a list of mp-ids, returns basic info from the database on all of them.

    Parameters:
        mp_id (str list): The structures you want info on. eg. ["mp-594", "mp-1547"]
        path_to_my_db_json (str): the path to your db.sjon file, eg. '/home/calebh27/atomate/config/db.json'
    Returns:
        df: a pandas DataFrame containing some basic info on the materials
    
    '''

    # set up the connection to the collection
    atomate_db = VaspCalcDb.from_db_file(path_to_my_db_json)
    materials_collection = atomate_db.db['materials']
    
    data = []

    for mp_id in mp_ids:
        material = materials_collection.find_one({'mpids': mp_id})
        # add match data to a data set (more can be added, as desired)
        data.append([material["formula_pretty"], mp_id, material["sg_symbol"], material["keywords"]])
    
    # convert data to a dataframe
    df = pd.DataFrame(data, columns=["Pretty Formula", "mp-id", "Space Group", "Keywords"])

    return df
