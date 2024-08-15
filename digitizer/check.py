# -*- coding: utf-8 -*-
"""Isotherm plotting."""
from io import StringIO
from traitlets import HasTraits, observe, Instance
import bokeh.models as bmd
from bokeh.plotting import figure
import panel as pn

#from .submission import Submissions,
from .submission import Isotherm
from .footer import footer
from .parse import prepare_isotherm_dict
from .makeAIF import makeAIF

TOOLS = ['pan', 'wheel_zoom', 'box_zoom', 'reset', 'save']


def get_bokeh_plot(isotherm_dict, pressure_scale='linear'):
    """Plot isotherm using bokeh.

    :returns: bokeh Figure instance
    """

    title = f'Placeholder Title'
    #title = f'{isotherm_dict["temperature"]} K'
    #title = f'{isotherm_dict["articleSource"]}, {isotherm_dict["adsorbent"]["name"]}, {isotherm_dict["temperature"]} K'
    p = figure(tools=TOOLS, x_axis_type=pressure_scale, title=title)  # pylint: disable=invalid-name
    p_vals = list(isotherm_dict['loops'][0].values())[0]
    #print(p_vals)
    a_vals = list(isotherm_dict['loops'][1].values())[0]
    #print(a_vals)
    #pressures = [point['pressure'] for point in isotherm_dict['isotherm_data']]
    pressures = [float(x) for x in p_vals]
    #print(pressures)
    adsorption = [float(x) for x in a_vals]
    #adsorption = [float(x) for x in isotherm_dict['loops']['_adsorp_amount'] if x != 'adsorption']
    #print(adsorption)
    data = bmd.ColumnDataSource(
        data=dict(index=[x for x in range(len(pressures))], pressure=pressures, adsorption=adsorption))
    p.line(  # pylint: disable=too-many-function-args
        'pressure', 'adsorption', source=data, legend_label='adsorbate')
    p.circle(  # pylint: disable=too-many-function-args
        'pressure', 'adsorption', source=data, legend_label='adsorbate')

    # update labels
    p.xaxis.axis_label = 'Pressure Units'
    #p.xaxis.axis_label = 'Pressure [{}]'.format(isotherm_dict['pressureUnits'])
    p.yaxis.axis_label = 'Adsorption Units'
    #p.yaxis.axis_label = 'Adsorption Units[{}]'.format(isotherm_dict['adsorptionUnits'])

    tooltips = [(p.xaxis.axis_label, '@pressure'), (p.yaxis.axis_label, '@adsorption')]
    hover = bmd.HoverTool(tooltips=tooltips)
    p.tools.pop()
    p.tools.append(hover)

    return p


def _get_figure_pane(figure_image):
    """Get Figure pane for display."""
    if figure_image:
        return figure_image.pane
    return pn.pane.HTML('')


class IsothermCheckView(HasTraits):
    """Consistency checks for digitized isotherms.
    """
    isotherm = Instance(Isotherm)

    def __init__(self, isotherm=None, observed_forms=None):
        """Create check of isotherm data for consistency check.

        :param isotherm: Isotherm instance (optional).
        :param observed_forms: list of IsothermForm instances to observe
        """
        super().__init__()

        if isotherm:
            self.isotherm = isotherm
        else:
            self.row = pn.Row(figure(tools=TOOLS), _get_figure_pane(None))
        # self.btn_download = pn.widgets.FileDownload(filename='data.json',
        #                                             button_type='primary',
        #                                             callback=self.on_click_download)
        self.btn_download = pn.widgets.FileDownload(filename='data.txt',
                                                    button_type='primary',
                                                    callback=self.on_click_check)
        # self.btn_add = pn.widgets.Button(name='Add to submission', button_type='primary')
        # self.btn_add.on_click(self.on_click_add)

        self.inp_pressure_scale = pn.widgets.RadioButtonGroup(name='Pressure scale', options=['linear', 'log'])
        self.inp_pressure_scale.param.watch(self.on_click_set_scale, 'value')

        # observe input forms
        def on_change_update(change):
            self.isotherm = change['new']

        if observed_forms:
            for form in observed_forms:
                form.observe(on_change_update, names=['isotherm'])

        # observe submission form and propagate changes to input forms
        self.observed_forms = observed_forms

        # def on_load_update(change):
        #     self.isotherm = change['new']
        #     # todo: reload multi-component form depending on isotherm data  # pylint: disable=fixme
        #     for form in self.observed_forms[0:1]:
        #         form.populate_from_isotherm(isotherm=change['new'])

        # self.submissions = Submissions()
        # self.submissions.observe(on_load_update, names=['loaded_isotherm'])

    @observe('isotherm')
    def _observe_isotherm(self, change):
        isotherm = change['new']
        #self.row[0] = get_bokeh_plot(isotherm.json)
        fig_obj = get_bokeh_plot(isotherm.json)
        self.row[0] = fig_obj
        self.row[1] = _get_figure_pane(isotherm.figure_image)

    # def on_click_download(self):
    #     """Download JSON file."""
    #     return StringIO(self.isotherm.json_str)

    # def on_click_download(self):
    #     """Download JSON file."""
    #     return StringIO(self.prepare_isotherm_dict.AIF)

    def on_click_check(self):  # pylint: disable=unused-argument
        """Check isotherm."""
        data, msg = prepare_isotherm_dict(self.observed_forms[0])
        #print(makeAIF(data))
        return StringIO(makeAIF(data))
        #return StringIO('aaaa')

    # def on_click_add(self, event):  # pylint: disable=unused-argument
    #     """Add isotherm to submission."""
    #     self.submissions.append(self.isotherm)

    def on_click_set_scale(self, event):  # pylint: disable=unused-argument
        """Set pressure scale."""
        self.row[0] = get_bokeh_plot(self.isotherm.json, pressure_scale=self.inp_pressure_scale.value)

    @property
    def layout(self):
        """Return layout."""
        return pn.Column(
            self.row,
            self.inp_pressure_scale,
            pn.Row(self.btn_download),
            #self.submissions.layout,
            footer)
