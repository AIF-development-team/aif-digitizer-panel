# -*- coding: utf-8 -*-
"""Prepare JSON output."""
from io import StringIO
import re
import datetime
import pandas as pd
import panel as pn
import json
import checkAIF
import os
import warnings

from .config import AIF_REQUIRED, LABEL_TO_NAME_REQ, LABEL_TO_NAME_OPT, AIF_VERSION, AIF_LOOP_NAMES
from .data2aif import data2aif
from .makeAIF import makeAIF
from . import ValidationError


def prepare_isotherm_dict(form):
    """Validate form contents and prepare JSON.

    :param form: Instance of IsothermForm
    :raises ValidationError: If validation fails.
    :returns: python dictionary with isotherm data
    """
    data = {}

    # Required fields provided?
    valid = True
    msg = ''

    for inp in form.required_inputs:
        if not inp.value or inp.value == 'Select':
            msg += 'Please provide ' + inp.name + '\n'
            valid = False
    if not valid:
        raise ValidationError(msg)

    # for inp in form.inp_keynames.column:
    #     if not inp[:][1].value or inp.value[:][1] == 'value here':
    #         msg += 'Please fill in all keyname/keyvalue pairs or remove the empty row\n'
    #         valid = False
    #     if not valid:
    #         raise ValidationError(msg)

    form_type = 'single-component' if form.__class__.__name__ == 'IsothermSingleComponentForm' else 'multi-component'

    data['_exptl_comment'] = form.inp_comment.value
    data['_audit_aif_version'] = AIF_VERSION

    # Log entry date
    data['_aif_date'] = datetime.date.today().strftime('%Y-%m-%d')
    # strftime is not strictly necessary but ensures correct YYYY-MM-DD format

    # Remakes required inputs lists then appends to data dict using the new list indexes
    required_inputs = []
    required_inputs2 = []
    required_inputs3 = []
    required_inputs4 = []
    x = 0
    for item in AIF_REQUIRED:
        if x == 0:
            x = x + 1
            required_inputs.append(item)

        elif x == 1:
            x = x + 1
            required_inputs2.append(item)

        elif x == 2:
            x = x + 1
            required_inputs3.append(item)

        elif x == 3:
            x = 0
            required_inputs4.append(item)

    for item in required_inputs:
        index = required_inputs.index(item)
        name = LABEL_TO_NAME_REQ[item]
        data[name] = form.req_column[index].value

    for item in required_inputs2:
        index = required_inputs2.index(item)
        name = LABEL_TO_NAME_REQ[item]
        data[name] = form.req_column2[index].value

    for item in required_inputs3:
        index = required_inputs3.index(item)
        name = LABEL_TO_NAME_REQ[item]
        data[name] = form.req_column3[index].value

    for item in required_inputs4:
        index = required_inputs4.index(item)
        name = LABEL_TO_NAME_REQ[item]
        data[name] = form.req_column4[index].value

    #AIF Optional fields
    numb = len(list(form.inp_optkeynames.column))
    for x in range(0, numb):
        label = form.inp_optkeynames.column[x][0].value
        name = LABEL_TO_NAME_OPT[label]
        #name = form.inp_optkeynames.column[x][0].value
        if form.inp_optkeynames.column[x][1].value == '':
            pass
        else:
            data[name] = form.inp_optkeynames.column[x][1].value
        # if name == '':#'keyname here as _stub_stub2':
        #     msg += 'Please fill in all keyname/keyvalue pairs or remove the empty row\n'
        #     valid = False
        # if not valid:
        #     raise ValidationError(msg)

        # if form.inp_optkeynames.column[x][1].value == '':#'value here':
        #     msg += 'Please fill in all keyname/keyvalue pairs or remove the empty row\n'
        #     valid = False
        # if not valid:
        #     raise ValidationError(msg)

    numb2 = len(list(form.inp_keynames.column))
    for x in range(0, numb2):
        name = form.inp_keynames.column[x][0].value
        #name = form.inp_keynames.column[x][0].value

        if name or form.inp_keynames.column[x][1].value == '':
            pass
        else:
            data[name] = form.inp_keynames.column[x][1].value

        #     msg += 'Please fill in all keyname/keyvalue pairs or remove the empty row\n'
        #     valid = False
        # if not valid:
        #     raise ValidationError(msg)

        # if form.inp_keynames.column[x][1].value == '':#'value here':
        #     msg += 'Please fill in all keyname/keyvalue pairs or remove the empty row\n'
        #     valid = False
        # if not valid:
        #     raise ValidationError(msg)

    #### Parse data loops here?
    #print(AIF_LOOP_NAMES)
    iso_data = []
    iso_data2 = []
    names = []
    numb3 = len(list(form.inp_loopnames.row))
    data_dict = {}
    data_dict['loops'] = []

    #print(numb3)
    for x in range(0, numb3):
        names.append(AIF_LOOP_NAMES[form.inp_loopnames.row[x][0].value])

    iso_data = form.inp_isotherm_data.value.split('\n')
    for item in iso_data:
        iso_data2.append(item.split(','))
    # print(iso_data2[0][0])
    # print(iso_data2[0][1])
    # print(iso_data2[1][0])

    for y in range(0, numb3):
        temp_list = []
        temp_dict = {}
        for x in range(0, len(iso_data2)):
            try:
                float(iso_data2[x][y])
                temp_list.append(iso_data2[x][y])
                temp_dict = {names[y]: temp_list}
            except:
                pass
        # print(temp_dict)
        data_dict['loops'].append(temp_dict)
        #data[names[y]] = temp_list

    # Sanitize keys from optional menus
    for key in data:  # pylint: disable=consider-using-dict-items
        if data[key] == 'Select':
            data[key] = None

    # with open("sample.json", "w") as outfile:
    #     json.dump(data, outfile)
    #data2aif(data, names)
    errors = ''

    for item in data:
        if not isinstance(data[item], list):
            keyname, keyvalue, san_errors = checkAIF.sanitizer(item, data[item])
        data_dict[keyname] = keyvalue
    #print(data_dict)
    errors += san_errors
    errors += checkAIF.loop_name_check(data_dict)
    #print(errors)
    input_file = './aifdictionary.json'
    json_dict, errors_json = checkAIF.json_to_dict(input_file)
    errors += errors_json
    errors += checkAIF.required_keynames(data_dict, json_dict)
    errors += checkAIF.var_type_checker(data_dict, json_dict)
    print(errors)

    if 'WARNING' and not 'ERROR' in errors:
        msg += errors

    if 'ERROR' in errors:
        msg += errors
        raise ValidationError(msg)
        #warnings.warn(msg, error)
        #raise Warning(msg)

    # a = makeAIF(data_dict)
    #print(a)

    #UNCOMMENT TO ALLOW AIF errors for form
    # if errors != '':
    #    msg += errors
    #    raise ValidationError(msg)

    #return data
    @property
    def AIF(data_dict):
        """returns aif file as a string"""
        return StringIO(makeAIF(data_dict))

    return data_dict, msg


def parse_isotherm_data(measurements, adorbates, form_type='single-component'):
    """Parse text from isotherm data field.

    :param measurements: Data from text field
    :param adsorbates: Adsorbates dictionary
    :param form_type: 'single-component' or 'multi-component'
    :returns: python dictionary with isotherm data

    """
    for delimiter in ['\t', ';', '|', ',']:
        measurements = measurements.replace(delimiter, ' ')  # convert all delimiters to spaces
    measurements = re.sub(' +', ' ', measurements)  # collapse whitespace
    measurements = pd.read_table(
        StringIO(measurements),
        sep=',| ',
        #sep=' ',
        # for some reason, leaving only the space delimiter is causing a problem
        #  when lines have trailing whitespace. Need to check pandas documentation
        comment='#',
        header=None,
        engine='python')
    measurements = measurements.to_numpy(dtype=float)
    #return measurements
    return [parse_pressure_row(pressure, adorbates, form_type) for pressure in measurements]


def parse_pressure_row(pressure, adsorbates, form_type):
    """Parse single pressure row.

    This can handle the following formats:
     * pressure,adsorption  (single-component form)
     * pressure,composition1,adsorption1,... (multi-component form)
     * pressure,composition1,adsorption1,...total_adsorption (multi-component form)
    """
    n_adsorbates = len(adsorbates)

    measurement = {
        'pressure': pressure[0],
        'species_data': [{
            'InChIKey': adsorbates[0]['InChIKey'],
            'composition': 1.0,
            'adsorption': pressure[1],
        }],
        'total_adsorption': pressure[1]
    }

    # TODO  # pylint: disable=fixme
    return measurement


class FigureImage:  # pylint: disable=too-few-public-methods
    """Representation of digitized image."""
    def __init__(self, data=None, filename=None):
        self.data = data
        self.filename = filename

    def _repr_png_(self):
        """Return png representation.

        Needed for display in "check" tab.
        """
        if self.data:
            return self.data
        return ''

    @property
    def pane(self):
        """Return PNG pane."""
        return pn.pane.PNG(object=self, width=400)
