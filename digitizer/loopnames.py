# -*- coding: utf-8 -*-
"""Dynamic list of adsorbates."""
import collections
import panel as pn
import panel.widgets as pw
from .config import AIF_LOOPS
from . import restrict_kwargs


class LoopName():  # pylint: disable=too-few-public-methods
    """Input form"""
    def __init__(self):
        """Initialize single keyname row.
        """
        self.inp_name = pw.Select(name='Loop Name',
                                    options = AIF_LOOPS,)
        
        self.row = pn.Row(self.inp_name)

    @property
    def dict(self):
        """Dictionary with keyname info"""
        return {'name': self.inp_name.value}


class LoopNameWithControls(LoopName):
    """Input form for describing adsorbates with controls to append/remove them."""
    def __init__(self, parent):
        """Initialize single keyname row.

        :param parent: Keynames instance
        """
        super().__init__()
        self.parent = parent
        self.btn_add = pw.Button(name='+', button_type='primary')
        self.btn_add.on_click(self.on_click_add)
        self.btn_remove = pw.Button(name='-', button_type='primary')
        self.btn_remove.on_click(self.on_click_remove)
        #self.inp_refcode = pw.TextInput(name='Refcode')
        self.row = pn.Row(self.inp_name, self.btn_add, self.btn_remove)
        # self.row = pn.GridSpec(height=50)
        # self.row[0, 0:8] = self.inp_name
        # self.row[0, 9] = self.btn_add
        # self.row[0, 10] = self.btn_remove

    def on_click_add(self, event):  # pylint: disable=unused-argument
        """Add new keyname."""
        self.parent.append(LoopNameWithControls(parent=self.parent))

    def on_click_remove(self, event):  # pylint: disable=unused-argument
        """Remove this keyname from the list."""
        self.parent.remove(self)


class LoopNames(collections.UserList):  # pylint: disable=R0901
    """List of all keynames"""
    def __init__(self, loopnames=None, show_controls=True):
        """
        Create dynamic list of keynames.

        :param keynames: List of adsorbate entities to prepopulate (optional)
        :param show_controls: Whether to display controls for addin/removing keynames.

        Note: This class inherits from collections.UserList for automatic implementation of len() and the subscript
         operator. The internal list is stored in self.data.
        """
        super().__init__()
        self.data = loopnames or []
        self._row = pn.Row(objects=[a.row for a in self]) #column

        # Add one adsorbate
        if not self.data:
            if show_controls:
                self.append(LoopNameWithControls(parent=self))
            else:
                self.append(LoopName())

    @property
    def row(self): #column
        """Panel column for visualization"""
        return self._row #column

    @property
    def inputs(self):
        """List of inputs"""
        return [a.inp_name for a in self]

    def append(self, item):  # pylint: disable=W0221
        """Add new keyname."""
        self.data.append(item)
        self._row.append(item.row) #column

    def remove(self, item):  # pylint: disable=W0221
        """Remove keyname from list."""
        self.data.remove(item)
        self._row.remove(item.row) #column
