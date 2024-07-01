# -*- coding: utf-8 -*-
"""Upload forms"""
import bokeh.models.widgets as bw
from traitlets import HasTraits, Instance
import panel as pn
import panel.widgets as pw

from . import ValidationError, config, restrict_kwargs
from .config import QUANTITIES, BIBLIO_API_URL, AIF_REQUIRED, AIF_OPTIONAL, AIF_LOOPS
from .adsorbates import Adsorbates
from .keynames import Keynames
from .optkeynames import OptKeynames
from .loopnames import LoopNames
from .parse import prepare_isotherm_dict, FigureImage
from .load_json import load_isotherm_json, load_isotherm_dict
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
        x = 0
        for item in AIF_REQUIRED:
            if x == 0:
                x = x+1
                required_inputs.append(pw.TextInput(name=item, placeholder = AIF_REQUIRED[item]))
                
            elif x == 1:
                x = x+1
                required_inputs2.append(pw.TextInput(name=item, placeholder = AIF_REQUIRED[item]))
                
            elif x == 2:
                x = 0
                required_inputs3.append(pw.TextInput(name=item, placeholder = AIF_REQUIRED[item]))

        #--------BOILER PLATE FOR OPTIONAL KEYWORDS----------------
        self.inp_optional1_key = pw.Select(name='Key Name 1', options=['Select', '_adsnt_info', '_adns_sample_density'])
        self.inp_optional1_key.param.watch(self.activate_optional, 'value')
        self.inp_optional1_val = pw.TextInput(name='Key Value 1', disabled=True)

        self.inp_optional2_key = pw.TextInput(name='Key Name 2')
        self.inp_optional2_key.param.watch(self.activate_optional, 'value')
        self.inp_optional2_val = pw.TextInput(name='Key Value 2', disabled=True)
        #----------------------------------------------------------
        self.inp_loop_name = pw.Select(name = 'Loop Name', options = AIF_LOOPS)
        
        self.inp_isotherm_data = pw.TextAreaInput(name='Use space, commas, or tab as delimiters between data columns',
                                                  height=200,
                                                  placeholder=config.SINGLE_COMPONENT_EXAMPLE)
        # self.inp_iso_data_column = pn.Column(self.inp_loop_name, self.inp_isotherm_data)
        
        self.inp_figure_image = pw.FileInput(name='Figure snapshot')

        
        # digitizer info
        self.inp_comment = pw.TextInput(name='Comment',
                                        placeholder='E.g. synthesis conditions & other background information.')

        # fill form from JSON upload
        self.inp_json = pw.FileInput(name='Upload JSON Isotherm')
        self.inp_json.param.watch(self.populate_from_json, 'value')

        # buttons
        self.btn_prefill = pn.widgets.Button(name='Prefill (default or from JSON)', button_type='primary')
        self.btn_prefill.on_click(self.on_click_populate)
        self.req_info = bw.PreText(text='Required inputs for AIF file.')
        self.opt_info = bw.PreText(text='Other common inputs, select from dropdown.')
        self.any_info = bw.PreText(text='Any other keyname/keyvalue pair.')
        self.out_info = bw.PreText(text='Click "Check" in order to download json.')
        self.blank = bw.PreText(text="")
        self.blank1 = bw.PreText(text="")
        self.blank2 = bw.PreText(text="")
        #self.out_info = pn.pane.Markdown(text='Click "Check" in order to download json.')
        self.inp_adsorbates = Adsorbates(show_controls=False)
        self.btn_plot = pn.widgets.Button(name='Check', button_type='primary')
        self.btn_plot.on_click(self.on_click_check)

        for inp in self.required_inputs:
            inp.css_classes = ['required']
        
        self.inp_keynames = Keynames(show_controls = True,)
        self.inp_optkeynames = OptKeynames(show_controls = True,)
        self.inp_loopnames = LoopNames(show_controls = True,)
        
        # Create Columns for Required Keys
        self.req_column = pn.Column(
            objects=required_inputs)
        self.req_column2 = pn.Column(
            objects=required_inputs2)
        self.req_column3 = pn.Column(
            objects=required_inputs3)        
        
        # create layout
        self.layout = pn.Column(
            self.blank,
            self.req_info,
            pn.Row(self.req_column, self.req_column2, self.req_column3),
            self.blank1,
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
            self.inp_loopnames.row,
            self.inp_isotherm_data,
            #self.inp_tabular, DONE
            pn.Row(self.btn_plot, self.btn_prefill, self.inp_json),
            self.out_info,
            footer,
        )
    
    def populate_from_isotherm(self, isotherm):
        """Populate form from isotherm instance.

        :param isotherm:  Isotherm instance
        """
        load_isotherm_dict(form=self, isotherm_dict=isotherm.json)

        figure_image = isotherm.figure_image
        self.inp_figure_image.value = figure_image.data
        self.inp_figure_image.filename = figure_image.filename

    def populate_from_json(self, event):
        """Prefills form from JSON.

        This function observes the inp_json field.
        """
        load_isotherm_json(form=self, json_string=event.new)

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
        return [
            self.inp_isotherm_data
        ] + self.inp_adsorbates.inputs

    def on_change_doi(self, event):
        """Warn, if DOI already known."""
        doi = event.new
        if doi in config.DOIs:
            self.log(f'{doi} already present in database (see {BIBLIO_API_URL}/{doi}.json ).', level='warning')


    def activate_optional(self, event):
        """Toggle Optional Field."""
        keyname = event.new
        if keyname != 'Select':
            self.inp_optional1_val.disabled = False
        else:
            self.inp_optional1_val.disabled = True
    
    def on_click_populate(self, event):  # pylint: disable=unused-argument
        """Populate form, either from JSON or with default values."""
        if self.inp_json.value:
            json_string = self.inp_json.value
            load_isotherm_json(form=self, json_string=json_string)
            self.inp_figure_image.value = None
            self.inp_figure_image.filename = None
        else:
            # Note: this could be replaced by loading a sample isotherm JSON (but makes it harder to edit defaults)
            # with open(DEFAULT_ISOTHERM_FILE) as handle:
            #     json_string = handle.read()
            # load_isotherm_json(form=self, json_string=json_string)

            for inp in self.required_inputs:
                try:
                    inp.value = inp.placeholder
                except AttributeError:
                    # select fields have no placeholder (but are currently pre-filled)
                    pass

            self.inp_figure_image.value = config.FIGURE_EXAMPLE
            self.inp_figure_image.filename = config.FIGURE_FILENAME_EXAMPLE

    def on_click_check(self, event):  # pylint: disable=unused-argument
        """Check isotherm."""
        try:
            data = prepare_isotherm_dict(self)
        except (ValidationError, ValueError) as exc:
            self.log(str(exc), level='error')
            raise

        figure_image = FigureImage(data=self.inp_figure_image.value,
                                   filename=self.inp_figure_image.filename) if self.inp_figure_image.value else None

        self.btn_plot.button_type = 'primary'
        self.log('')

        self.isotherm = Isotherm(data, figure_image)
        #self.tabs.active = 2
        self.tabs.active = 1

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


# class IsothermMultiComponentForm(IsothermSingleComponentForm):  # pylint:disable=too-many-instance-attributes
#     """Initialize form.

#     :param tabs: Panel tabs instance for triggering tab switching.
#     """
#     def __init__(self, tabs):
#         """Initialize form.

#         :param tabs: Panel tabs instance for triggering tab switching.
#         """

#         # new fields
#         self.inp_composition_type = pw.Select(name='Composition type',
#                                               options=['Select'] + QUANTITIES['composition_type']['names'])
#         self.inp_composition_type.param.watch(self.on_change_composition_type, 'value')
#         self.inp_concentration_units = pw.AutocompleteInput(name='Concentration Units',
#                                                             options=QUANTITIES['concentration_units']['names'],
#                                                             placeholder='Molarity (mol/l)',
#                                                             case_sensitive=False,
#                                                             disabled=True,
#                                                             **restrict_kwargs)

#         super().__init__(tabs)
        
#         # override fields
#         self.inp_adsorbates = Adsorbates(show_controls=True, )
#         self.inp_isotherm_data = pw.TextAreaInput(name='Isotherm Data',
#                                                   height=200,
#                                                   placeholder=config.MULTI_COMPONENT_EXAMPLE)

#         # modified prefill function
#         self.btn_prefill.on_click(self.on_click_populate)

#         # create layout
#         self.layout = pn.Column(
#             pn.pane.HTML('<div><b>Warning:</b> The multi-component form is not well tested</div>.'),
#             self.inp_optional1_key,
#             self.inp_digitizer,
#             self.inp_doi,
#             pn.pane.HTML('<hr>'),
#             self.inp_source_type,
#             pn.Row(pn.pane.HTML("""Attach Figure Graphics"""), self.inp_figure_image),
#             self.inp_measurement_type,
#             self.inp_adsorbent,
#             self.inp_adsorbates.column,
#             self.inp_temperature,
#             self.inp_isotherm_type,
#             pn.Row(self.inp_pressure_units, self.inp_saturation_pressure),
#             self.inp_pressure_scale,
#             self.inp_adsorption_units,
#             pn.Row(self.inp_composition_type, self.inp_concentration_units),
#             pn.pane.HTML("""We recommend the
#                 <b><a href='https://apps.automeris.io/wpd/' target="_blank">WebPlotDigitizer</a></b>
#                 for data extraction."""),
#             self.inp_isotherm_data,
#             self.inp_tabular,
#             pn.Row(self.btn_plot, self.btn_prefill, self.inp_json),
#             self.out_info,
#             footer,
#         )

#     @property
#     def required_inputs(self):
#         """Required inputs."""
#         return super().required_inputs + [self.inp_composition_type]

#     def on_click_populate(self, event):  # pylint: disable=unused-argument
#         """Prefill form for testing purposes."""
#         super().on_click_populate(event)
#         self.inp_composition_type.value = 'Mole Fraction'

#     def on_change_composition_type(self, event):
#         """Toggle concentration units input depending on pressure composition type."""
#         composition_type = event.new
#         if composition_type == 'Concentration (specify units)':
#             self.inp_concentration_units.disabled = False
#         else:
#             self.inp_concentration_units.disabled = True
