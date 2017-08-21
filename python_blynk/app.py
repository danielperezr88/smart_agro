#!/usr/bin/env python
from BlynkLib import Blynk
from time import sleep, ticks_ms
import json

from serial import Serial

blynk = Blynk('62e3b56640974018aa5779f87cdd51cb')
ser = Serial('/dev/serial0', 115200, timeout=1)
json_raw = ''
sensor_id = 0
timestamp = ticks_ms()

vpin_option_dict = {
    0: '1',
    1: '3',
    2: '2',
    3: '4',
    4: '6',
    5: '7',
    6: '8',
    7: '5',
    8: '50000',
    9: '30000'
}


def wait_for_json():

    json_ = None

    while json_ is None:
        json_ = maybe_retrieve_json()

    return json_


def maybe_retrieve_json():
    global json_raw

    try:
        json_raw += ser.readline().decode('utf-8').strip('\n').strip('\r')
    except BlockingIOError as _:
        pass

    while json_raw[0] != '{' if len(json_raw) > 0 else False:
        json_raw = json_raw[1:]

    if len(json_raw) == 0:
        return None

    close_idx = json_raw.find('}')
    while close_idx == -1:
        try:
            json_raw += ser.readline().decode('utf-8').strip('\n').strip('\r')
            close_idx = json_raw.find('}')
        except BlockingIOError as _:
            pass

    result = None

    try:
        result = json.loads(json_raw[:close_idx + 1])
    except ValueError as e:
        print('Error: ' + str(e))
        return result
    finally:
        if result is not None:
            json_raw = json_raw[close_idx + 1:]

    return result


# Temperature Inside (option 1)
def v0_read():
    ser.write(bytes(vpin_option_dict[0], encoding='utf-8'))

blynk.add_virtual_pin(0, read=v0_read)


# Temperature Outside (option 3)
def v1_read():
    ser.write(bytes(vpin_option_dict[1], encoding='utf-8'))

blynk.add_virtual_pin(1, read=v1_read)


# Humidity Inside (option 2)
def v2_read():
    ser.write(bytes(vpin_option_dict[2], encoding='utf-8'))

blynk.add_virtual_pin(2, read=v2_read)


# Humidity Outside (option 4)
def v3_read():
    ser.write(bytes(vpin_option_dict[3], encoding='utf-8'))

blynk.add_virtual_pin(3, read=v3_read)


# Light Intensity (option 6)
def v4_read():
    ser.write(bytes(vpin_option_dict[4], encoding='utf-8'))

blynk.add_virtual_pin(4, read=v4_read)


# Upper Soil Moisture (option 7)
def v5_read():
    ser.write(bytes(vpin_option_dict[5], encoding='utf-8'))

blynk.add_virtual_pin(5, read=v5_read)


# Lower Soil Moisture (option 8)
def v6_read():
    ser.write(bytes(vpin_option_dict[6], encoding='utf-8'))

blynk.add_virtual_pin(6, read=v6_read)


# Water Level (option 5)
def v7_read():
    ser.write(bytes(vpin_option_dict[7], encoding='utf-8'))

blynk.add_virtual_pin(7, read=v7_read)


# Fan Programme (30000 < option <= 50000)
def v8_write(param):
    print(param)
    if param[0] == 1:
        ser.write(bytes('49999', encoding='utf-8'))
    else:
        ser.write(bytes('30001', encoding='utf-8'))
        blynk.virtual_write(8, 0)


def v8_read():
    ser.write(bytes(vpin_option_dict[8], encoding='utf-8'))

blynk.add_virtual_pin(8, write=v8_write, read=v8_read)


# Pump Programme (10000 < option <= 30000)
def v9_write(param):
    print(param)
    if param[0] == 1:
        ser.write(bytes('29999', encoding='utf-8'))
    else:
        ser.write(bytes('10001', encoding='utf-8'))
        blynk.virtual_write(9, 0)


def v9_read():
    ser.write(bytes(vpin_option_dict[9], encoding='utf-8'))

blynk.add_virtual_pin(9, write=v9_write, read=v9_read)


def option_read():
    global sensor_id, timestamp

    result = maybe_retrieve_json()

    if result is not None:
        option = result['o']
        print(result)
        if (option > 10000 and option <= 29999) or (option > 30000 and option <= 49999):
            pass
        else:
            blynk.virtual_write(dict(tuple([v, k]) for k, v in vpin_option_dict.items())[str(option)], result['v'])

    if ticks_ms() - timestamp > 5000:
        timestamp += 5000
        globals()['v' + str(sensor_id) + '_read']()
        sensor_id = (sensor_id + 1) % 10

blynk.set_user_task(option_read, 100)

if __name__ == '__main__':
    blynk.run()
