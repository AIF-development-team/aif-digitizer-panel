# -*- coding: utf-8 -*-
"""Upload forms"""
import bokeh.models.widgets as bw
from traitlets import HasTraits, Instance
import panel as pn
import panel.widgets as pw

import warnings

from . import ValidationError, config, restrict_kwargs
from .config import AIF_REQUIRED, AIF_OPTIONAL, AIF_LOOPS, prefill
from .keynames import Keynames
from .optkeynames import OptKeynames
from .loopnames import LoopNames
from .parse import prepare_isotherm_dict, FigureImage
from .footer import footer
from .submission import Isotherm


class IsothermSingleComponentForm(HasTraits):  # pylint:disable=too-many-instance-attributes
    """HTML form for uploading new isotherms."""

    isotherm = Instance(Isotherm)  # this traitlet is observed by the "check" view

    def __init__(self, tabs):  # pylint: disable=redefined-outer-name
        """Initialize form.

        :param tabs: Panel tabs instance for triggering tab switching.
        """
        super().__init__()
        self.tabs = tabs

        # AIF Required Fields
        required_inputs = []
        required_inputs2 = []
        required_inputs3 = []
        required_inputs4 = []
        x = 0
        for item in AIF_REQUIRED:
            if x == 0:
                x = x + 1
                required_inputs.append(pw.TextInput(name=item, placeholder=AIF_REQUIRED[item]))

            elif x == 1:
                x = x + 1
                required_inputs2.append(pw.TextInput(name=item, placeholder=AIF_REQUIRED[item]))

            elif x == 2:
                x = x + 1
                required_inputs3.append(pw.TextInput(name=item, placeholder=AIF_REQUIRED[item]))
            elif x == 3:
                x = 0
                required_inputs4.append(pw.TextInput(name=item, placeholder=AIF_REQUIRED[item]))

        #--------BOILER PLATE FOR OPTIONAL KEYWORDS----------------
        self.inp_optional1_key = pw.Select(name='Key Name 1', options=['Select', '_adsnt_info', '_adns_sample_density'])
        self.inp_optional1_key.param.watch(self.activate_optional, 'value')
        self.inp_optional1_val = pw.TextInput(name='Key Value 1', disabled=True)

        self.inp_optional2_key = pw.TextInput(name='Key Name 2')
        self.inp_optional2_key.param.watch(self.activate_optional, 'value')
        self.inp_optional2_val = pw.TextInput(name='Key Value 2', disabled=True)
        #----------------------------------------------------------
        self.inp_loop_name = pw.Select(name='Loop Name', options=AIF_LOOPS)

        self.inp_isotherm_data = pw.TextAreaInput(name='Use space, commas, or tab as delimiters between data columns',
                                                  height=200,
                                                  placeholder=config.SINGLE_COMPONENT_EXAMPLE)
        # self.inp_iso_data_column = pn.Column(self.inp_loop_name, self.inp_isotherm_data)

        self.inp_figure_image = pw.FileInput(name='Figure snapshot')

        # digitizer info
        self.inp_comment = pw.TextInput(name='Comment',
                                        placeholder='E.g. synthesis conditions & other background information.')

        # fill form from JSON upload
        #self.inp_json = pw.FileInput(name='Upload JSON Isotherm')
        #self.inp_json.param.watch(self.populate_from_json, 'value')

        # buttons
        self.btn_prefill = pn.widgets.Button(name='Prefill Example Data', button_type='primary')
        self.btn_prefill.on_click(self.on_click_populate)
        self.req_info = bw.PreText(text='Required inputs for AIF file, all inputs should be floats or strings.')
        self.opt_info = bw.PreText(text='Other common inputs, select a name from the dropdown and enter a value.')
        self.any_info = bw.PreText(text='Any other keyname/keyvalue pair.')
        self.out_info = bw.PreText(text='Click "Check" in order to download json.')
        self.loop_info = bw.PreText(
            text='Select loop column headers using the dropdowns and input data into the box below.')
        self.blank = bw.PreText(text='')
        self.blank1 = bw.PreText(text='')
        self.blank2 = bw.PreText(text='')
        self.btn_plot = pn.widgets.Button(name='Check', button_type='primary')
        self.btn_plot.on_click(self.on_click_check)
        self.btn_checkbox = pn.widgets.Checkbox(
            name='Override Warnings',
            disabled=False,
        )

        for inp in self.required_inputs:
            inp.css_classes = ['required']

        self.inp_keynames = Keynames(show_controls=True, )
        self.inp_optkeynames = OptKeynames(show_controls=True, )
        self.inp_loopnames = LoopNames(show_controls=True, )

        # Create Columns for Required Keys
        self.req_column = pn.Column(objects=required_inputs)
        self.req_column2 = pn.Column(objects=required_inputs2)
        self.req_column3 = pn.Column(objects=required_inputs3)
        self.req_column4 = pn.Column(objects=required_inputs4)

        # create layout
        self.divider1 = pn.Column(
            '# Required Inputs',
            pn.layout.Divider(),
            styles=dict(background='white'),
            width=800,
        )

        self.divider2 = pn.Column(
            '# Optional Inputs',
            pn.layout.Divider(),
            styles=dict(background='white'),
            width=800,
        )

        self.divider3 = pn.Column(
            '# Loop Names & Data',
            pn.layout.Divider(),
            styles=dict(background='white'),
            width=800,
        )

        self.layout = pn.Column(
            self.blank,
            self.divider1,
            self.req_info,
            pn.Row(self.req_column, self.req_column2, self.req_column3, self.req_column4),
            self.blank1,
            self.divider2,
            self.opt_info,
            self.inp_optkeynames.column,
            self.blank2,
            self.any_info,
            self.inp_keynames.column,
            #self.req_column,
            #pn.Row(self.inp_optional1_key, self.inp_optional1_val),
            #pn.Row(self.inp_optional2_key, self.inp_optional2_val),
            #self.inp_digitizer, DONE
            #self.inp_doi, DONE
            #pn.pane.HTML('<hr>'), already gone?
            #pn.pane.HTML('BLANK LINE'),
            #self.inp_source_type, DONE
            self.inp_comment,
            #pn.Row(pn.pane.HTML("""Attach Figure Graphics"""), self.inp_figure_image),
            #self.inp_measurement_type, DONE
            #self.inp_adsorbent, DONE
            #self.inp_adsorbates.column, May break a lot
            #self.inp_temperature, DONE
            #self.inp_isotherm_type, DONE
            #pn.Row(self.inp_pressure_units, self.inp_saturation_pressure), DONE
            #self.inp_pressure_scale, DONE
            #self.inp_adsorption_units, DONE
            #pn.pane.HTML("""We recommend the
            #    <b><a href='https://apps.automeris.io/wpd/' target="_blank">WebPlotDigitizer</a></b>
            #    for data extraction."""),
            # self.inp_loop_name,
            self.divider3,
            self.loop_info,
            self.inp_loopnames.row,
            self.inp_isotherm_data,
            #self.inp_tabular, DONE
            #pn.Row(self.btn_plot, self.btn_prefill, self.inp_json),
            pn.Row(self.btn_plot, self.btn_prefill),
            #pn.Row(self.btn_plot, self.btn_prefill, self.btn_checkbox),
            self.out_info,
            footer,
        )

    # def populate_from_isotherm(self, isotherm):
    #     """Populate form from isotherm instance.

    #     :param isotherm:  Isotherm instance
    #     """

    #     print('HERE')
    #     print(type(isotherm))

    #     load_isotherm_dict(form=self, isotherm_dict=isotherm.json)

    #     figure_image = isotherm.figure_image
    #     self.inp_figure_image.value = figure_image.data
    #     self.inp_figure_image.filename = figure_image.filename

    # def populate_from_json(self, event):
    #     """Prefills form from JSON.

    #     This function observes the inp_json field.
    #     """
    #     load_isotherm_json(form=self, json_string=event.new)

    # @property
    # def required_inputs(self):
    #     """Required inputs."""
    #     return [
    #         self.inp_doi, self.inp_adsorbent, self.inp_temperature, self.inp_isotherm_data, self.inp_pressure_units,
    #         self.inp_adsorption_units, self.inp_source_type, self.inp_digitizer
    #     ] + self.inp_adsorbates.inputs

    @property
    def required_inputs(self):
        """Required inputs."""
        return [self.inp_isotherm_data]

    def activate_optional(self, event):
        """Toggle Optional Field."""
        keyname = event.new
        if keyname != 'Select':
            self.inp_optional1_val.disabled = False
        else:
            self.inp_optional1_val.disabled = True

    def on_click_populate(self, event):  # pylint: disable=unused-argument

        for item in self.req_column:
            if item.name in prefill.keys():
                item.value = prefill[item.name]
        for item in self.req_column2:
            if item.name in prefill.keys():
                item.value = prefill[item.name]
        for item in self.req_column3:
            if item.name in prefill.keys():
                item.value = prefill[item.name]
        for item in self.req_column4:
            if item.name in prefill.keys():
                item.value = prefill[item.name]

        for inp in self.required_inputs:
            try:
                inp.value = inp.placeholder
            except AttributeError:
                pass
        self.inp_comment.value = 'User Comment'
        """Populate form with default values."""
        # for inp in self.required_inputs:
        #     try:
        #         inp.value = inp.placeholder
        #     except AttributeError:
        #         # select fields have no placeholder (but are currently pre-filled)
        #         pass

    def on_click_check(self, event):  # pylint: disable=unused-argument
        """Check isotherm."""
        if self.btn_checkbox.value == True:
            try:
                data, msg = prepare_isotherm_dict(self)
            except (ValidationError, ValueError) as exc:
                self.log(str(exc), level='error')
                raise
        if self.btn_checkbox.value == False:
            try:
                data, msg = prepare_isotherm_dict(self)
            except (ValidationError, ValueError) as exc:
                self.log(str(exc), level='error')
                pn.state.notifications.position = 'center-right'
                pn.state.notifications.warning('This is a warning notification.', duration=4000)
                raise
            if 'WARNING' in msg:
                self.log(str(msg), level='warning')
                self.layout.insert(-2, self.btn_checkbox)
                raise Warning(msg)

        # try:
        #     data = prepare_isotherm_dict(self)
        #     #data(dict) --> data(aif)
        #     #aif --> checker
        #     #return aif?
        # except (ValidationError, ValueError) as exc:
        #     self.log(str(exc), level='error')
        #     raise

        figure_image = FigureImage(data=self.inp_figure_image.value,
                                   filename=self.inp_figure_image.filename) if self.inp_figure_image.value else None

        self.btn_plot.button_type = 'primary'
        self.log('')

        self.isotherm = Isotherm(data, figure_image)
        self.tabs.active = 1  # this changes to the IsothermCheckView tab

    def log(self, msg, level='info'):
        """Print log message.

        Note: For some reason, simply updating the .text property of the PreText widget stopped working after moving
        to tabs (TODO: open issue on panel for this).
        """
        #self.layout.remove(self.out_info)
        self.layout.pop(-2)  # -1 is footer for the moment
        self.out_info.text = msg
        self.layout.insert(-1, self.out_info)  # inserts *before* -1

        if level == 'info':
            self.btn_plot.button_type = 'primary'
        elif level == 'warning':
            self.btn_plot.button_type = 'warning'
        elif level == 'error':
            self.btn_plot.button_type = 'danger'
