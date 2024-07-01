# -*- coding: utf-8 -*-
"""Prepare JSON output."""
from io import StringIO
import re
import datetime
import pandas as pd
import panel as pn

from .config import find_by_name, QUANTITIES, AIF_REQUIRED
#from .forms import required_inputs
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

    # fill data
    #for 
    
    
    adsorbates_json = [find_by_name(a.inp_name.value, QUANTITIES['adsorbates']['json']) for a in form.inp_adsorbates]
    data['adsorbates'] = [{key: adsorbate[key] for key in ['name', 'InChIKey']} for adsorbate in adsorbates_json]
    form_type = 'single-component' if form.__class__.__name__ == 'IsothermSingleComponentForm' else 'multi-component'
    data['isotherm_data'] = parse_isotherm_data(form.inp_isotherm_data.value, data['adsorbates'], form_type=form_type)

    if form.__class__.__name__ == 'IsothermMultiComponentForm':
        data['compositionType'] = form.inp_composition_type.value
        data['concentrationUnits'] = form.inp_concentration_units.value
    else:
        data['compositionType'] = 'molefraction'  # default for single-component isotherm
        data['concentrationUnits'] = None
    data['custom'] = form.inp_comment.value
    data['associated_content'] = [form.inp_figure_image.filename]

    # 'associated_content' is a list in anticipation of multiple file selection
    # code for getting filenames will change

    # Log entry date
    data['date'] = datetime.date.today().strftime('%Y-%m-%d')
    # strftime is not strictly necessary but ensures correct YYYY-MM-DD format

    # Remakes required inputs lists then appends to data dict using the new list indexes
    required_inputs = []
    required_inputs2 = []
    required_inputs3 = []
    x = 0
    for item in AIF_REQUIRED:
        if x == 0:
            x = x+1
            required_inputs.append(item)
            
        elif x == 1:
            x = x+1
            required_inputs2.append(item)
            
        elif x == 2:
            x = 0
            required_inputs3.append(item)
    
    for item in required_inputs:
        index = required_inputs.index(item)
        data[item] = form.req_column[index].value

    for item in required_inputs2:
        index = required_inputs2.index(item)
        data[item] = form.req_column2[index].value

    for item in required_inputs3:
        index = required_inputs3.index(item)
        data[item] = form.req_column3[index].value
        
    #AIF Optional fields
    numb = len(list(form.inp_optkeynames.column))
    for x in range(0, numb):
        name = form.inp_optkeynames.column[x][0].value
        data[name] = form.inp_optkeynames.column[x][1].value
        if name == '':#'keyname here as _stub_stub2':
            msg += 'Please fill in all keyname/keyvalue pairs or remove the empty row\n'
            valid = False
        if not valid:
            raise ValidationError(msg)
            
        if form.inp_optkeynames.column[x][1].value == '':#'value here':
            msg += 'Please fill in all keyname/keyvalue pairs or remove the empty row\n'
            valid = False
        if not valid:
            raise ValidationError(msg)


    
    numb2 = len(list(form.inp_keynames.column))
    for x in range(0, numb2):
        name = form.inp_keynames.column[x][0].value
        data[name] = form.inp_keynames.column[x][1].value
        if name == '':#'keyname here as _stub_stub2':
            msg += 'Please fill in all keyname/keyvalue pairs or remove the empty row\n'
            valid = False
        if not valid:
            raise ValidationError(msg)
            
        if form.inp_keynames.column[x][1].value == '':#'value here':
            msg += 'Please fill in all keyname/keyvalue pairs or remove the empty row\n'
            valid = False
        if not valid:
            raise ValidationError(msg)
    print(form.inp_loopnames.row)
    #### Parse data loops here?
    # numb3 = len(list(form.inp_loopnames.row))
    # for x in range(0, numb3):
    #     name = form.inp_loopnames.row[0][x].value
    #     data[name] = parse_isotherm_data2(form.inp_isotherm_data.value)
    
     
    # Sanitize keys from optional menus
    for key in data:  # pylint: disable=consider-using-dict-items
        if data[key] == 'Select':
            data[key] = None
            
    # for key in data:
    #     if data[key] == '':
        
        

    return data

# def parse_isotherm_data2(measurements):
#     """Parse text from isotherm data field.

#     :param measurements: Data from text field
#     :param adsorbates: Adsorbates dictionary
#     :param form_type: 'single-component' or 'multi-component'
#     :returns: python dictionary with isotherm data

#     """
#     for delimiter in ['\t', ';', '|', ',']:
#         measurements = measurements.replace(delimiter, ' ')  # convert all delimiters to spaces
#     measurements = re.sub(' +', ' ', measurements)  # collapse whitespace
#     measurements = pd.read_table(
#         StringIO(measurements),
#         sep=',| ',
#         #sep=' ',
#         # for some reason, leaving only the space delimiter is causing a problem
#         #  when lines have trailing whitespace. Need to check pandas documentation
#         comment='#',
#         header=None,
#         engine='python')
#     measurements = measurements.to_numpy(dtype=float)
#     #return measurements
#     return measurements


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
    n_rows_no_total = 1 + 2 * n_adsorbates
    n_rows_total = n_rows_no_total + 1

    if form_type == 'single-component':
        if len(pressure) != 2:
            raise ValidationError('Expected 2 columns for pressure point "{}", found {}'. \
                                  format(str(pressure), len(pressure)), )
        measurement = {
            'pressure': pressure[0],
            'species_data': [{
                'InChIKey': adsorbates[0]['InChIKey'],
                'composition': 1.0,
                'adsorption': pressure[1],
            }],
            'total_adsorption': pressure[1]
        }
    else:
        if len(pressure) == n_rows_no_total:
            has_total_adsorption = False
        elif len(pressure) == n_rows_total:
            has_total_adsorption = True
        else:
            raise ValidationError('Expected {} or {} columns for pressure point "{}", found {}'. \
                                  format(n_rows_no_total, n_rows_total, str(pressure), len(pressure)), )

        measurement = {
            'pressure':
            pressure[0],
            'species_data': [{
                'InChIKey': adsorbates[i]['InChIKey'],
                'composition': pressure[1 + 2 * i],
                'adsorption': pressure[2 + 2 * i],
            } for i in range(n_adsorbates)],
        }
        if has_total_adsorption:
            measurement['total_adsorption'] = pressure[-1]
        else:
            pass
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
