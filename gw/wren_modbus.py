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
    except Exception as e:
        return None

    unit = 0xff
    if config.has_key('unit_id'):
        unit = config['unit_id']

    value = None
    if config['table'] == 'InputRegister':
        result = m.read_input_registers(config['address'], 1, unit=unit)
        if result:
            value = result.registers[config['address']]
    if config['table'] == 'HoldingRegister':
        result = m.read_holding_registers(config['address'], 1, unit=unit)
        if result:
            value = result.registers[config['address']]

    m.close()
    return str(value)

def wren_gw_modbus_write(config, value):
    ''' write a value to the peer.

    @param value a number in the string type.
    '''

    try:
        m = ModbusTcpClient(host=config['node'], port=config['port'])
        m.connect()
    except Exception as e:
        return False

    unit = 0xff
    if config.has_key('unit_id'):
        unit = config['unit_id']

    result = False
    if config['table'] == 'HoldingRegister':
        result = m.write_register(config['address'], int(value), unit=unit)
        if result.value == int(value):
            result = True

    m.close()
    return str(value)

'''
test code
'''
if __name__ == '__main__' :
    config = { 'node':'127.0.0.1', 'port':'50200',
              'table':'InputRegister', 'address':0 }
    print(wren_gw_modbus_read(config))
