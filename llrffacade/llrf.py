__author__ = 'antmil'

from PyTango import DispLevel, Attr, DevDouble, DevState, DevVarStringArray, AttrWriteType, AttributeProxy, WAttribute
from PyTango.server import device_property, command, attribute#, run
from facadedevice import FacadeMeta, logical_attribute, proxy_attribute, Facade
from taurus import Attribute
import taurus.core
import PyTango


# from PyTango import Util,

class Llrf(Facade):
    """
    Tango Device server for a high level control of the llrf cavities
    """
    __metaclass__ = FacadeMeta

    # Attributes

    RawAmprefinaKW = proxy_attribute(
        dtype=float,
        device='LlrfDevice',
        attr='AmpRefInA',
        display_level=DispLevel.EXPERT,
        doc=''
    )
    # RawPhrefinaKW = proxy_attribute(
    #     dtype=float,
    #     device='LlrfDevice',
    #     attr='PhRefInA',
    #     display_level=DispLevel.EXPERT,
    #     doc=''
    # )
    # RawDiag_amprefaKW = proxy_attribute(
    #     dtype=float,
    #     device='LlrfDevice',
    #     attr='AmpRefA',
    #     display_level=DispLevel.EXPERT,
    #     doc=''
    # )
    # RawDiag_phrefaKW = proxy_attribute(
    #     dtype=float,
    #     device='LlrfDevice',
    #     attr='PhRefA',
    #     display_level=DispLevel.EXPERT,
    #     doc=''
    # )
    # RawDiag_ampcavloopsaKW = proxy_attribute(
    #     dtype=float,
    #     device='LlrfDevice',
    #     attr='AmpCavLoopsA',
    #     display_level=DispLevel.EXPERT,
    #     doc=''
    # )
    # RawDiag_ampfwcavloopsaKW = proxy_attribute(
    #     dtype=float,
    #     device='LlrfDevice',
    #     attr='AmpFwCavLoopsA',
    #     display_level=DispLevel.EXPERT,
    #     doc=''
    # )
    # RawDiag_phcavloopsaKW = proxy_attribute(
    #     dtype=float,
    #     device='LlrfDevice',
    #     attr='PhCavLoopsA',
    #     display_level=DispLevel.EXPERT,
    #     doc=''
    # )
    # RawDiag_phfwcavloopsaKW = proxy_attribute(
    #     dtype=float,
    #     device='LlrfDevice',
    #     attr='PhFwCavloopsA',
    #     display_level=DispLevel.EXPERT,
    #     doc=''
    # )
    # RawDiag_amprvcavaKW = proxy_attribute(
    #     dtype=float,
    #     device='LlrfDevice',
    #     attr='AmpRvCavA',
    #     display_level=DispLevel.EXPERT,
    #     doc=''
    # )
    # RawDiag_phrvcavaKW = proxy_attribute(
    #     dtype=float,
    #     device='LlrfDevice',
    #     attr='PhRvCavA',
    #     display_level=DispLevel.EXPERT,
    #     doc=''
    # )

    @logical_attribute(
        dtype=float,
        #device='LlrfDevice',
        unit='KW',
        doc=''
    )
    def AmpRefInAKW(self, data):
        VALUE = data['RawAmprefinaKW']
        new_value = eval(self.AmpRefInAKW_formula)
        return new_value

    AmpRefInAKW_formula = device_property(
        dtype=str,
        default_value='VALUE*2',
        doc=''
    )

    # @logical_attribute(
    #     dtype=float,
    #     unit='KW',
    #     doc=''
    # )
    # def PhRefInAKW(self, data):
    #     VALUE = data['RawPhRefInAKW']
    #     new_value = eval(self.PhRefInAKW_formula)
    #     return new_value
    #
    # PhRefInAKW_formula = device_property(
    #     dtype=str,
    #     default_value='VALUE',
    #     doc=''
    # )

    # diag_amprefaKW
    # diag_phrefaKW
    # diag_ampcavloopsaKW
    # diag_ampfwcavloopsaKW
    # diag_phcavloopsaKW
    # diag_phfwcavloopsaKW
    # diag_amprvcavaKW
    # diag_phrvcavaKW

    @command(dtype_in=str)
    def CreateFloatAttribute(self, attr_name):
        attr = Attr(attr_name, DevDouble)
        # attr = attribute(label=attr_name,
        #                  dtype=float,
        #                  #display_level=DispLevel.OPERATOR,
        #                  access=AttrWriteType.READ_WRITE,
        #                  unit='',
        #                  format='%6.2f',
        #                  min_value=0, max_value=10,
        #                  rel_change='0.1',
        #                  polling_period=1000,
        #                  # fget="get_KpA",
        #                  # fset="set_KpA",
        #                  doc=""
        # )

        self.add_attribute(attr, self.read_General, self.write_General)

    def read_General(self, attr):
        self.info_stream("Reading attribute %s", attr.get_name())
        attr.set_value(99.99)

    def write_General(self, attr):
        self.info_stream("Writting attribute %s", attr.get_name())

    DynamicAttributes = device_property(
        dtype=DevVarStringArray,
        default_value='',
        doc='Example: Attr = (Attr, Formula)'
    )

    def delete_device(self):
        for att in self.dyn_attrs_dict.keys():
            listener_name = att + 'Listener'
            self.dyn_attrs_dict[att][0].removeListener(self.__dict__[listener_name])

    def init_device(self):
        Facade.init_device(self)
        try:
            self.dyn_attrs_dict = {}
            self.extract_attributes()
            self.create_dyn_attributes()
        except Exception, e:
            self.set_state(DevState.FAULT)
            self.set_status(e.message)

    def extract_attributes(self):
        self.info_stream("Extracting dynamicAttributes ...")
        dyn_attrs = self.DynamicAttributes
        print dyn_attrs
        for attr in dyn_attrs:
            self.get_attributes_dict(attr)
        self.info_stream("... DynamicAttributes Extracted")

    def get_attributes_dict(self, attr):
        self.info_stream("Creating dynamic attributes dict ...")
        self.info_stream('Attribute = %s' % attr)

        attr_info = attr.split('=')
        self.info_stream('attr_info = %s' % attr_info)

        attr_name = attr_info[0]
        self.info_stream('attr_name = %s' % attr_name)

        attr_formula = attr_info[1].strip("(").strip(")").split(',')[1]
        self.info_stream('attr_formula = %s' % attr_formula)

        attr_to_proxy = attr_info[1].strip("(").strip(")").split(',')[0]
        full_attr_to_proxy = self.LlrfDevice + '/' + attr_to_proxy
        taurus_attr = Attribute(full_attr_to_proxy)
        listener_name = attr_name + 'Listener'
        self.__dict__[listener_name] = taurus.core.TaurusListener(None)
        self.__dict__[listener_name].eventReceived = lambda a, b, c: self._dyn_attr_event_received(a,self.__dict__[listener_name],c, attr_name, attr_formula )
        taurus_attr.addListener(self.__dict__[listener_name])

        self.info_stream('attr_to_proxy = %s' %attr_to_proxy)

        self.dyn_attrs_dict[attr_name] = (taurus_attr, attr_formula)

    def _dyn_attr_event_received(self, tango_attr, event_type, event_value, attr_nane, attr_formula):
        if event_type in [taurus.core.TaurusEventType.Periodic, taurus.core.TaurusEventType.Change]:
            VALUE = event_value.value
            new_value = eval(attr_formula)
            time = event_value.time.tv_sec + 1e-6*event_value.time.tv_usec
            self.push_change_event(attr_nane, new_value, time, event_value.quality)
        elif event_type in [taurus.core.TaurusEventType.Error]:
            v = tango_attr.getValueObj()
            time = v.time.tv_sec + 1e-6 * v.time.tv_usec
            self.push_change_event(attr_nane, 0, time, PyTango.AttrQuality.ATTR_INVALID)


    def create_dyn_attributes(self):
        self.info_stream("Creating dynamic attributes ...")
        for att in self.dyn_attrs_dict.keys():
            self.create_dyn_attribute(att)

    def create_dyn_attribute(self, attr_name):
        attr = Attr(attr_name, DevDouble, AttrWriteType.READ_WRITE)
        self.add_attribute(attr, self.read_dyn_attributes, self.write_dyn_attributes)
        self.set_change_event(attr_name, True)

    def read_dyn_attributes(self, attr):
        attr_name = attr.get_name()
        self.info_stream("Reading attribute %s", attr_name)
        #attr_proxy = Attribute(self.LlrfDevice + '/' + self.dyn_attrs_dict[attr_name][0])
        #VALUE = attr_proxy.read().value
        VALUE = self.dyn_attrs_dict[attr_name][0].getValueObj().value
        formula = self.dyn_attrs_dict[attr_name][1]
        new_value = eval(formula)
        attr.set_value(new_value)

    def write_dyn_attributes(self, attr):
        attr_name = attr.get_name()
        self.info_stream("Writing attribute %s", attr_name)
        data=[]
        attr.get_write_value(data)
        #attr_proxy = Attribute(self.LlrfDevice + '/' + self.dyn_attrs_dict[attr_name][0])
        attr_proxy = self.dyn_attrs_dict[attr_name][0]
        attr_proxy.write(data[0])

    def delete_device(self):
        Facade.delete_device(self)



if __name__ == '__main__':
    Llrf.run_server()
    # run()
    #run({'Llrf': (Llrf, ws_rf_llrf_1)})
