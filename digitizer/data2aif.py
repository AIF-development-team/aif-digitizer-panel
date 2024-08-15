# -*- coding: utf-8 -*-
import json
from gemmi import cif


def data2aif(data_dict, names):
    """
    This function attempts to covert the data dictionary from parse.py
    to aif format for checkAIF
    """
    d = cif.Document()
    d.add_new_block('data2aif')

    block = d.sole_block()

    meta_index = []
    meta_vals = []
    loop_names = []
    loop_vals = []
    for item in data_dict.keys():
        meta_index.append(item)
    #print(meta_index, "\n\n")
    loop_names = meta_index[len(meta_index) - len(names):]
    meta_index = meta_index[
        1:len(meta_index) -
        len(names)]  #removes loops from list (REMOVES FIRST VALUE BECAUSE OF OLD FUNCTIONALIY, MUST FIX)

    #print(meta_index)

    for item in data_dict.values():
        meta_vals.append(item)
    #print(meta_vals, '\n\n')
    loop_vals = meta_vals[len(meta_vals) - len(names):]
    meta_vals = meta_vals[1:len(meta_vals) - len(names)]
    #print(meta_vals)

    for x in range(0, len(meta_index)):
        block.set_pair(meta_index[x], meta_vals[x])  #creates metadata block

    #LOOPS
    #loops = list(range(0,int(len(loop_names)*.5)))
    loops = list(range(0, int(len(loop_names) / 3)))
    #print(loops)
    #print(len(loop_names))
    y = 0
    # for x in loops:
    #     loops[x] = block.init_loop('',[loop_names[y], loop_names[y+1]])
    #     loops[x].set_all_values([list(loop_vals[y]),list(loop_vals[y+1])])
    #     y = y+2
    for x in loops:
        loops[x] = block.init_loop('', [loop_names[y], loop_names[y + 1], loop_names[y + 2]])
        loops[x].set_all_values([list(loop_vals[y]), list(loop_vals[y + 1]), list(loop_vals[y + 2])])
        y = y + 3
    # loop0 = block.init_loop('',[loop_names[0], loop_names[1]])
    # loop0.set_all_values([list(loop_vals[0]),list(loop_vals[1])])

    d.write_file('data.aif')
