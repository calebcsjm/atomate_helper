from helper_core import get_material_ids

def add_keywords_by_id(material_ids, keywords, path_to_my_db_json):
    ''' Adds keywords to mongodb docs in the materials collection (a summary doc created by builders)
    
    Parameters: 
        material_id (str list): the mp-ids of the substances you want to update, e.g. ["mp-123", "mp-234"]
        keywords (str list): the keywords you would like added to the document, e.g. ["09/2021", "battery material"]
        path_to_my_db_json (str): the path to your db.sjon file, eg. '/home/calebh27/atomate/config/db.json'
        
    Returns: 
        missing_ids (str list): mp-ids that were not found in the database
    
    '''

    from atomate.vasp.database import VaspCalcDb
    atomate_db = VaspCalcDb.from_db_file(PATH_TO_MY_DB_JSON)
    materials_collection = atomate_db.db['materials']
    
    missing_ids = []
    for mp_id in material_ids: 
        #tests to see if the id is in the database 
        found = materials_collection.find_one({'mpids': mp_id})
        if found is not None:
            materials_collection.update_one({'mpids': mp_id}, { "$set": { "keywords": keywords } })
        else:
            missing_ids.append(mp_id)
    
    return missing_ids

'''
Mongodb update_one() notes:
The object using the dot notation needs to be a collection in the database. The first dictionary is the query,
or which document it looks for to update. Then the second dictionary contains the new field(s) to add, and the
contents of that field. 
'''

def add_keywords_by_formula(pretty_formulas, keywords):
    ''' Written as a companion to the add dielectric workflows function, it adds the keywords to all the variations of a 
    given pretty forumla for which we have results in the mongodb (see also add_keywords_by_id function)
    
    Parameters:
        pretty_formulas (str list): a list of compounds with their pretty formulas. Ex: ['NiS', 'MgO']
        keywords (str list): the keywords you would like added to the document, e.g. ["09/2021", "battery material"]
        
    Returns: 
        None 
    '''
    missing_ids = []
    for formula in pretty_formulas:
        ids = get_material_ids(formula)
        missing = add_keywords_by_id(ids, keywords)
        missing_ids.extend(missing)
        
    print("The following ids were not found in the database: ", missing_ids)
