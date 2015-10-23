#!/usr/bin/env python

###############################################################################
#     LLRF Facade device server.
#
#     Copyright (C) 2015  Max IV Laboratory, Lund Sweden
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see [http://www.gnu.org/licenses/].
###############################################################################

"""This module contains the Facade device server for the LLRF.
"""

__all__ = ["Llrf", "run_device"]

__docformat__ = 'restructuredtext'

__author__ = 'antmil'

from PyTango import Attr, DevDouble, DevState, DevVarStringArray, AttrWriteType, AttrQuality
from PyTango.server import device_property, Device, DeviceMeta, run

from taurus import Attribute
import taurus.core


class Llrf(Device):
    """
    Tango Device server for a high level control of the llrf cavities.
    """
    __metaclass__ = DeviceMeta

    DynamicAttributes = device_property(
        dtype=DevVarStringArray,
        default_value='',
        doc='Example: Attr = (Attr, Formula)'
    )

    LlrfDevice = device_property(
        dtype=str,
        default_value='',
        doc='Device server for the llrf device to proxy'
    )

    def delete_device(self):
        Device.delete_device(self)
        for att in self.dyn_attrs_dict.keys():
            listener_name = att + 'Listener'
            self.dyn_attrs_dict[att][0].removeListener(self.__dict__[listener_name])

    def init_device(self):
        Device.init_device(self)
        try:
            self.dyn_attrs_dict = {}
            self.extract_attributes_from_property()
            self.create_dyn_attributes()
        except Exception, e:
            self.set_state(DevState.FAULT)
            self.set_status(e.message)

    def extract_attributes_from_property(self):
        self.info_stream("Extracting dynamicAttributes ...")
        dyn_attrs = self.DynamicAttributes

        for attr in dyn_attrs:
            attr_name, attr_info_list = self.extract_attribute_info(attr)
            self.info_stream("... DynamicAttributes info extracted")
            self.create_listeners(attr_name, attr_info_list)
            self.info_stream("... Listeners created")

    def extract_attribute_info(self, attr):
        self.info_stream('Attribute = %s' % attr)

        attr_info = attr.split('=')
        self.info_stream('attr_info = %s' % attr_info)

        attr_name = attr_info[0]
        self.info_stream('attr_name = %s' % attr_name)

        attr_info_list = attr_info[1].strip("(").strip(")").split(',')
        return attr_name, attr_info_list

    def create_listeners(self, attr_name, attr_info_list):
        self.info_stream("Creating Listeners ...")

        attr_to_proxy = attr_info_list[0]
        full_attr_to_proxy = self.LlrfDevice + '/' + attr_to_proxy
        taurus_attr = Attribute(full_attr_to_proxy)

        if len(attr_info_list) == 2:
            r_method = attr_info_list[1]
            self.dyn_attrs_dict[attr_name] = (taurus_attr, r_method)

        elif len(attr_info_list) == 3:
            r_method, w_method = attr_info_list[1::]
            self.dyn_attrs_dict[attr_name] = (taurus_attr, r_method, w_method)
            self.info_stream('w_method = %s' % w_method)

        self.info_stream('r_method = %s' % r_method)

        listener_name = attr_name + 'Listener'
        self.__dict__[listener_name] = taurus.core.TaurusListener(None)
        self.__dict__[listener_name].eventReceived = lambda a, b, c: self._dyn_attr_event_received(a,
                                                                                                   self.__dict__[listener_name],
                                                                                                   c,
                                                                                                   attr_name,
                                                                                                   r_method )
        taurus_attr.addListener(self.__dict__[listener_name])

        self.info_stream('attr_to_proxy = %s' % attr_to_proxy)

    def _dyn_attr_event_received(self, tango_attr, event_type, event_value, attr_nane, r_method):
        if event_type in [taurus.core.TaurusEventType.Periodic, taurus.core.TaurusEventType.Change]:
            VALUE = event_value.value
            new_value = eval(r_method)
            time = event_value.time.tv_sec + 1e-6*event_value.time.tv_usec
            self.push_change_event(attr_nane, new_value, time, event_value.quality)

        elif event_type in [taurus.core.TaurusEventType.Error]:
            v = tango_attr.getValueObj()
            time = v.time.tv_sec + 1e-6 * v.time.tv_usec
            self.push_change_event(attr_nane, 0, time, AttrQuality.ATTR_INVALID)

    def create_dyn_attributes(self):
        self.info_stream("Creating dynamic attributes ...")
        for att in self.dyn_attrs_dict.keys():
            self.create_dyn_attribute(att)
        self.info_stream("... Dynamic attributes created")

    def create_dyn_attribute(self, attr_name):
        self.info_stream("Creating dynamic attribute: %s" % attr_name)
        if len(self.dyn_attrs_dict[attr_name]) == 2:
            attr = Attr(attr_name, DevDouble, AttrWriteType.READ)
            self.add_attribute(attr, self.read_dyn_attributes)

        elif len(self.dyn_attrs_dict[attr_name]) == 3:
            attr = Attr(attr_name, DevDouble, AttrWriteType.READ_WRITE)
            self.add_attribute(attr, self.read_dyn_attributes, self.write_dyn_attributes)

        self.set_change_event(attr_name, True)

    def read_dyn_attributes(self, attr):
        attr_name = attr.get_name()
        self.info_stream("Reading attribute: %s", attr_name)

        VALUE = self.dyn_attrs_dict[attr_name][0].getValueObj().value
        r_method = self.dyn_attrs_dict[attr_name][1]
        new_value = eval(r_method)
        attr.set_value(new_value)

    def write_dyn_attributes(self, attr):
        attr_name = attr.get_name()
        self.info_stream("Writing attribute: %s", attr_name)
        data=[]
        attr.get_write_value(data)
        VALUE = data[0]

        attr_proxy = self.dyn_attrs_dict[attr_name][0]
        w_method = self.dyn_attrs_dict[attr_name][2]
        new_value = eval(w_method)
        attr_proxy.write(new_value)


def run_device():
    run([Llrf])

if __name__ == '__main__':
    run_device()
