import PyTango
import sys
import fandango
import math

class LlrfFacade(fandango.DynamicDS):

    def __init__(self,cl,name):
        fandango.DynamicDS.__init__(self,cl,name,_locals={
                                                            'SQRT': lambda value: math.sqrt(value),
                                                            'ASIN': lambda value: math.asin(value),
                                                            'ACOS': lambda value: math.acos(value)
                                                         })
        LlrfFacade.init_device(self)

    def init_device(self):
        self.debug_stream('In Python init_device method')
        self.set_state(PyTango.DevState.ON)
	self.get_device_properties(self.get_device_class())

#------------------------------------------------------------------

    def delete_device(self):
        self.debug_stream('[delete_device] for device %s ' % self.get_name())

#------------------------------------------------------------------
# COMMANDS
#------------------------------------------------------------------
#------------------------------------------------------------------
#       Always excuted hook method
#------------------------------------------------------------------
    def always_executed_hook(self):
        print "In ", self.get_name(), "::always_excuted_hook()"
        fandango.DynamicDS.always_executed_hook(self)
#------------------------------------------------------------------
# ATTRIBUTES
#------------------------------------------------------------------

    def read_attr_hardware(self, data):
        self.debug_stream('In read_attr_hardware')

#------------------------------------------------------------------


#------------------------------------------------------------------
# CLASS
#------------------------------------------------------------------

class LlrfFacadeClass(fandango.DynamicDSClass):

    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name)
        print 'In LlrfFacadeClass __init__'

    class_property_list = {
    }
    
    device_property_list = {
        'DynamicAttributes':
            [PyTango.DevVarStringArray,
            "",
            []
            ]
        }
    
    cmd_list = {
        'updateDynamicAttributes':
            [[PyTango.DevVoid, ""],
            [PyTango.DevVoid, ""],
            {
                'Display level':PyTango.DispLevel.EXPERT,
            } ],
    }

    attr_list = { 
    }

if __name__ == '__main__':
    try:
        util = PyTango.Util(sys.argv)

        util.add_class(LlrfFacadeClass, LlrfFacade, 'LlrfFacade')

        U = PyTango.Util.instance()
        U.server_init()
        U.server_run()
    except PyTango.DevFailed,e:
        print '-------> Received a DevFailed exception:',e
    except Exception,e:
        print '-------> An unforeseen exception occured....',e
