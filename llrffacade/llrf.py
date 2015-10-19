__author__ = 'antmil'

from PyTango import DispLevel, Attr, DevDouble, DevState, DevVarStringArray, AttrWriteType, AttributeProxy, WAttribute
from PyTango.server import device_property, command, attribute#, run
from facadedevice import FacadeMeta, logical_attribute, proxy_attribute, Facade
from taurus import Attribute


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

        attr_to_proxy = attr_info[1].strip("(").strip(")").split(',')[0]
        self.info_stream('attr_to_proxy = %s' %attr_to_proxy)

        attr_formula = attr_info[1].strip("(").strip(")").split(',')[1]
        self.info_stream('attr_formula = %s' % attr_formula)

        self.dyn_attrs_dict[attr_name] = (attr_to_proxy, attr_formula)

    def create_dyn_attributes(self):
        self.info_stream("Creating dynamic attributes ...")
        for att in self.dyn_attrs_dict.keys():
            self.create_dyn_attribute(att)

    def create_dyn_attribute(self, attr_name):
        attr = Attr(attr_name, DevDouble, AttrWriteType.READ_WRITE)
        self.add_attribute(attr, self.read_dyn_attributes, self.write_dyn_attributes)

    def read_dyn_attributes(self, attr):
        self.info_stream("Reading attribute %s", attr_name)
        attr_name = attr.get_name()
        attr_proxy = Attribute(self.LlrfDevice + '/' + self.dyn_attrs_dict[attr_name][0])
        VALUE = attr_proxy.read().value
        formula = self.dyn_attrs_dict[attr_name][1]
        new_value = eval(formula)
        attr.set_value(new_value)

    def write_dyn_attributes(self, attr):
        self.info_stream("Writing attribute %s", attr_name)
        attr_name = attr.get_name()
        data=[]
        attr.get_write_value(data)
        attr_proxy = Attribute(self.LlrfDevice + '/' + self.dyn_attrs_dict[attr_name][0])
        attr_proxy.write(data[0])

    def delete_device(self):
        Facade.delete_device(self)



if __name__ == '__main__':
    Llrf.run_server()
    # run()
    #run({'Llrf': (Llrf, ws_rf_llrf_1)})
