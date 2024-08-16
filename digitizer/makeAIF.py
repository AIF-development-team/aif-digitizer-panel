# -*- coding: utf-8 -*-
from gemmi import cif

def makeAIF(data_dict):
    """
    Uses data dictionary to create AIF file for download
    """
    d = cif.Document()
    d.add_new_block('data2aif')
    block = d.sole_block()
    
    keys = list(data_dict.keys())
    
    #CIF cant read datetime.datetime
    # data_dict['_digitizer_date'] = str(data_dict['_digitizer_date']) 
    
    for item in data_dict:
        if item != 'loops':
            data_dict[item] = str(data_dict[item])
            #print(item, data_dict[item], type(data_dict[item]))
            block.set_pair(item, data_dict[item])

    loopkeys = []
    for item in data_dict['loops']:
        loopkeys.append(list(item.keys()))
    loopkeys = sum(loopkeys, [])

    loopvals = []
    for x in range(0,len(loopkeys)):
        loopvals += (list(data_dict['loops'][x].values()))

    
    # for x in range(0,len(loopkeys)):
    #     block.init_loop('', loopkeys[x]).set_all_values([(loopvals[x])])

    block.init_loop('', loopkeys).set_all_values(loopvals)
       
    # d.write_file('data.aif')
    return d.as_string()