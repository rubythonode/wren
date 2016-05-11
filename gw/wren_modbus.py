#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import traceback

import sys
from pymodbus.client.sync import ModbusTcpClient

def wren_gw_modbus_read(config):
    ''' read a value from the peer.

    @param config the configuration in the key/value type.
    '''

    try:
        m = ModbusTcpClient(host=config['node'], port=config['port'])
        m.connect()
        unit = 0xff
        if config.has_key('unit_id'):
            unit = config['unit_id']
        # sed data
        value = None
        if config['table'] == 'InputRegister':
            result = m.read_input_registers(config['address'], 1, unit=unit)
            if result:
                value = result.registers[config['address']]
        if config['table'] == 'HoldingRegister':
            result = m.read_holding_registers(config['address'], 1, unit=unit)
            if result:
                value = result.registers[config['address']]
        # close it.
        m.close()
        return {"status":True, "value":str(value)};
    except Exception as e:
        return {"status":False, "value":str(e)};

def wren_gw_modbus_write(config, value):
    ''' write a value to the peer.

    @param value a number in the string type.
    '''

    try:
        m = ModbusTcpClient(host=config['node'], port=config['port'])
        # XXX
        # ModbusTcpClient.connect() does not look to do connect(2) actually.
        m.connect()
        unit = 0xff
        if config.has_key('unit_id'):
            unit = config['unit_id']
        # send data
        result = False
        if config['table'] == 'HoldingRegister':
            result = m.write_register(config['address'], int(value), unit=unit)
            if result.value == int(value):
                result = True
        # close it.
        m.close()
        return {"status":True, "value":str(value)};
    except Exception as e:
        return {"status":False, "value":str(e)};

'''
test code
'''
if __name__ == '__main__' :
    config = { 'node':'127.0.0.1', 'port':'50200',
              'table':'InputRegister', 'address':0 }
    print(wren_gw_modbus_read(config))
