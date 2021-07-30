'''These functions are only designed to query information from the materials collection in the mongodb,
which is created by running run_builder.py'''

from helper_core import get_material_ids
from atomate.vasp.database import VaspCalcDb
from pymatgen.core import Structure
import numpy as np
import pandas as pd

def get_all_structures(path_to_my_db_json, additional_properties = []):
    '''Returns basic info from the database on all structures in the materials collection, in addition to any user specified
    values from the metadata section

    Parameters:
        path_to_my_db_json (str): the path to your db.sjon file, eg. '/home/calebh27/atomate/config/db.json'
        additional_properties (str list): Any additional properties that you wish to query. These must be the
                                          names that are used in the metadata section of the mongodb. Use 
                                          print_available_properties() to see options. Ex. ['epsilon_ionic']
    Returns:
        df: a pandas DataFrame containing some basic info (formula, id, spacegroup, and keywords) on the materials
    
    '''

    # set up the connection to the collection
    atomate_db = VaspCalcDb.from_db_file(path_to_my_db_json)
    materials_collection = atomate_db.db['materials']

    # define the basic properties to query
    properties_to_query = ["formula_pretty", "mpids","sg_symbol","keywords"]
    property_names = ["Pretty Formula", "mp-id", "Space Group", "Keywords"]
    
    # include any user-specificed properties to query
    properties_to_query.extend(additional_properties)
    property_names.extend(additional_properties)
    
    data = []
    
    materials = materials_collection.find()
    
    for material in materials:
        current_material_properties = []
    
        for material_property in properties_to_query:
            try: # search for the property on the first level
                current_material_properties.append(material[material_property])
            except: # search in the metadata block
                    try:
                        current_material_properties.append(material["_tasksbuilder"]["prop_metadata"]["energies"][material_property])
                    except: # property not found
                        current_material_properties.append("N/A")
                        
        # add match data to a data set
        data.append(current_material_properties)
    
    # convert data to a dataframe
    df = pd.DataFrame(data, columns=property_names)

    return df

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

'''
These two function can easily be modified to get any other property simply by changing the 'the_material['dielectric']['epsilon_static']' portion
to match the path needed. To see all the possible data that could be queried, use the print_all_material_info() function below
'''
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


def query_materials_by_id(mp_ids, path_to_my_db_json, additional_properties = []):
    '''Given a list of mp-ids, returns basic info from the database on all of them. It can also return values from
    the metadata section. 

    Parameters:
        mp_id (str list): The structures you want info on. eg. ["mp-594", "mp-1547"]
        path_to_my_db_json (str): the path to your db.sjon file, eg. '/home/calebh27/atomate/config/db.json'
        additional_properties (str list): Any additional properties that you wish to query. These must be the
                                          names that are used in the metadata section of the mongodb. Use 
                                          print_available_properties() to see options. Ex. ['epsilon_ionic']
    Returns:
        df: a pandas DataFrame containing some basic info (formula, id, spacegroup, and keywords) on the materials
    
    '''

    # set up the connection to the collection
    atomate_db = VaspCalcDb.from_db_file(path_to_my_db_json)
    materials_collection = atomate_db.db['materials']
    
    # define the basic properties to query
    properties_to_query = ["formula_pretty", "mpids","sg_symbol","keywords"]
    property_names = ["Pretty Formula", "mp-id", "Space Group", "Keywords"]
    
    # include any user-specificed properties to query
    properties_to_query.extend(additional_properties)
    property_names.extend(additional_properties)
    
    data = []

    for mp_id in mp_ids:
        material = materials_collection.find_one({'mpids': mp_id})
        current_material_properties = []
    
        for material_property in properties_to_query:
            try: # search for the property on the first level
                current_material_properties.append(material[material_property])
            except: # search in the metadata block
                    try:
                        current_material_properties.append(material["_tasksbuilder"]["prop_metadata"]["energies"][material_property])
                    except: # property not found
                        current_material_properties.append("N/A")
                        
        # add match data to a data set
        data.append(current_material_properties)
    
    # convert data to a dataframe
    df = pd.DataFrame(data, columns=property_names)

    return df

def print_available_properties(path_to_my_db_json, mp_id='mp-594'):
    '''Prints out the properties that can be queried from the mongodb. It defaults to using NiS mp-594 as a 
    generic example, but you can modify for a specific material.
    
    Parameters: 
        path_to_my_db_json (str): the path to your db.sjon file, eg. '/home/calebh27/atomate/config/db.json'
        mp_id (str): The mp-id of the material for which you want to see available properties
    Returns:
        None
        
    '''
    
    # set up the connection to the collection
    atomate_db = VaspCalcDb.from_db_file(path_to_my_db_json)
    materials_collection = atomate_db.db['materials']
    
    material = materials_collection.find_one({'mpids': mp_id})
    
    print("Surface level properties: (some may be objects and not able to be queried)")
    for prop in material:
        print(" -", prop)
    print("Metadata properties:")
    for prop in material["_tasksbuilder"]["prop_metadata"]["energies"]:
        print(" -", prop)
    
def print_all_material_info(path_to_my_db_json, mp_id):
    '''Pretty prints the document for a structure in the materials collection of the mongodb
    
    Parameters: 
        path_to_my_db_json (str): the path to your db.sjon file, eg. '/home/calebh27/atomate/config/db.json'
        mp_id (str): The mp-id of the material for which you want to see available properties
    Returns: None
    
    '''
    
    from pprint import pprint
    
    atomate_db = VaspCalcDb.from_db_file(path_to_my_db_json)
    materials_collection = atomate_db.db['materials']
    
    material = materials_collection.find_one({'mpids': mp_id})
    pprint(material)

