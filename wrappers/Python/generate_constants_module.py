from __future__ import print_function
import os,shutil

"""
A little module to wrap the params enum for use in Cython code

Ian Bell, May 2014
"""


def params_constants(enum_key):
    fName = os.path.join('..','..','include','DataStructures.h')

    contents = open(fName,'r').read()

    left = contents.find('{', contents.find('enum '+enum_key));
    right = contents.find('}', left)
    entries = contents[left+1:right]

    if entries.find('/*') > -1: raise ValueError('/* */ style comments are not allowed, replace them with // style comments')
    if not entries: raise ValueError('Unable to find '+enum_key)

    lines = entries.split('\n')
    lines = [line for line in lines if not line.strip().startswith('//')]

    for i,line in enumerate(lines):
        if line.find('/'):
            lines[i] = line.split('/')[0]
        if '=' in lines[i]:
            lines[i] = lines[i].split('=')[0].strip() + ','

    # Chomp all the whitespace, split at commas
    keys = ''.join(lines).replace(' ','').split(',')

    keys = [k for k in keys if k]

    return keys


def config_constants():
    fName = os.path.join('..','..','include','Configuration.h')
    contents = open(fName,'r').readlines()

    matching_lines = [i for i,line in enumerate(contents) if "#define CONFIGURATION_KEYS_ENUM" in line]
    assert(len(matching_lines)==1)
    iline = matching_lines[0] + 1
    keys = []
    while iline < 1000 and contents[iline].strip().startswith('X('):
        line = contents[iline].strip()[2::]
        key = line.split(',')[0]
        keys.append(key)
        iline += 1
    return ('configuration_keys',keys)


def generate_cython(data, config_data):

    print('****** Writing the constants module ******')

    # Write the PXD definition file
    pxd_output_file = open('CoolProp/constants_header.pxd','w')

    pxd_output_file.write('# This file is automatically generated by the generate_constants_module.py script in wrappers/Python.\n# DO NOT MODIFY THE CONTENTS OF THIS FILE!\n\ncdef extern from "DataStructures.h" namespace "CoolProp":\n')
    for enum_key, entries in data:
        pxd_output_file.write('\tctypedef enum '+enum_key+':\n')
        for param in entries:
            param = param.strip()
            pxd_output_file.write('\t\t'+param+'\n')
    pxd_output_file.write('\n\ncdef extern from "Configuration.h":\n')
    enum_key, entries = config_data
    pxd_output_file.write('\tctypedef enum '+enum_key+':\n')
    for param in entries:
        param = param.strip()
        pxd_output_file.write('\t\t'+param+'\n')
    pxd_output_file.close()

    # Write the PYX implementation file
    pyx_output_file = open('CoolProp/_constants.pyx','w')
    pyx_output_file.write('# This file is automatically generated by the generate_constants_module.py script in wrappers/Python.\n')
    pyx_output_file.write('# DO NOT MODIFY THE CONTENTS OF THIS FILE!\n')
    pyx_output_file.write('cimport constants_header\n\n')
    for enum_key, entries in data:
        for param in entries:
            param = param.strip()
            pyx_output_file.write(param+' = '+'constants_header.'+param+'\n')
    enum_key, entries = config_data
    for param in entries:
        param = param.strip()
        pyx_output_file.write(param+' = '+'constants_header.'+param+'\n')
    pyx_output_file.close()

    # Write the PY implementation file
    py_output_file = open('CoolProp/constants.py','w')
    py_output_file.write('# This file is automatically generated by the generate_constants_module.py script in wrappers/Python.\n# DO NOT MODIFY THE CONTENTS OF THIS FILE!\nfrom __future__ import absolute_import\n\nfrom . import _constants\n\n')
    for enum_key, entries in data:
        for param in entries:
            param = param.strip()
            py_output_file.write(param+' = '+'_constants.'+param+'\n')
    enum_key, entries = config_data
    for param in entries:
        param = param.strip()
        py_output_file.write(param+' = '+'_constants.'+param+'\n')
    py_output_file.close()


def generate():
    data = [(enum,params_constants(enum)) for enum in ['parameters', 'input_pairs', 'fluid_types', 'phases']]
    generate_cython(data,config_constants())


if __name__=='__main__':
    generate()
