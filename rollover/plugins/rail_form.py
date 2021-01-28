import os, sys
from abaqusGui import *
from collections import OrderedDict
from rollover.plugins.rollover_gui_utils import PartDB, KwAdder


class RailForm(AFXForm):

    def __init__(self, owner):

        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        
        # Define form title/name
        self.title = 'Create rail'
        
        # Define command to be called
        self.cmd = AFXGuiCommand(self, 'create_rail', 'commands')
        
        # Define keywords to be input arguments to function in self.cmd
        profile = ':/rail_profiles/UIC60_head.sat'
        self.profile = {'kw': AFXStringKeyword(self.cmd, 'profile', 
                                               TRUE, 
                                               defaultValue=profile),
                        'label': 'rail sketch file',
                        'pattern': 'Sketch files (*.sat)'}
        
        # Define in dictionary to be able to use loop to create text fields
        self.kw = OrderedDict() # Need to use OrderedDict to ensure that 
                                # the fields appear in the given order
        kwa = KwAdder(self.cmd, self.kw)
        
        kwa.add('rail cae name: ', 'name', 'rail_example')
        kwa.add('rail length: ', 'length', 50.0)
        kwa.add('mesh size: ', 'mesh_size', '2.0, 10')
        kwa.add('refine p1: ', 'pt_min', '-7.0, -5.0')
        kwa.add('refine p2: ', 'pt_max', '7.0, 5.0')
        kwa.add('sym_sign: ', 'sym_sign', 0)
        
        
    def getFirstDialog(self):
        return PartDB(self)
        

