#!/usr/bin/env python
from BlynkLib import Blynk
from time import sleep
import json

from serial import Serial

blynk = Blynk('62e3b56640974018aa5779f87cdd51cb')
ser = Serial('/dev/serial0', 115200, timeout=1)

def wait_for_json():
  result_raw = ''
  while (True if len(result_raw) == 0 else result_raw[0] != '{'):
    try:
      result_raw = ser.readline().decode('utf-8')
    except BlockingIOError as e:
      pass

  while result_raw[-1] != '}':
    try:
      result_raw += ser.readline().decode('utf-8')
      result_raw = result_raw.strip('\n').strip('\r')
    except BlockingIOError as e:
      pass

  try:
    print(result_raw)
    return json.loads(result_raw)
  except ValueError as e:
    print('Error: ' + str(e))
  except BlockingIOError as e:
    pass

#Temperature Inside (option 1)
def v0_read():
  ser.write(bytes('0', encoding='utf-8'))
  result = wait_for_json()
  print(result)
  blynk.virtual_write(0, result['v'])

blynk.add_virtual_pin(0, read=v0_read)

#Temperature Outside (option 3)
def v1_read():
  ser.write(bytes('1', encoding='utf-8'))
  result = wait_for_json()
  print(result)
  blynk.virtual_write(1, result['v'])

blynk.add_virtual_pin(1, read=v1_read)

#Humidity Inside (option 2)
def v2_read():
  ser.write(bytes('2', encoding='utf-8'))
  result = wait_for_json()
  print(result)
  blynk.virtual_write(2, result['v'])

blynk.add_virtual_pin(2, read=v2_read)

#Humidity Outside (option 4)
def v3_read():
  ser.write(bytes('3', encoding='utf-8'))
  result = wait_for_json()
  print(result)
  blynk.virtual_write(3, result['v'])

blynk.add_virtual_pin(3, read=v3_read)

#Light Intensity (option 6)
def v4_read():
  ser.write(bytes('4', encoding='utf-8'))
  result = wait_for_json()
  print(result)
  blynk.virtual_write(4, result['v'])

blynk.add_virtual_pin(4, read=v4_read)

#Upper Soil Moisture (option 7)
def v5_read():
  ser.write(bytes('5', encoding='utf-8'))
  result = wait_for_json()
  print(result)
  blynk.virtual_write(5, result['v'])

blynk.add_virtual_pin(5, read=v5_read)

#Lower Soil Moisture (option 8)
def v6_read():
  ser.write(bytes('6', encoding='utf-8'))
  result = wait_for_json()
  print(result)
  blynk.virtual_write(6, result['v'])

blynk.add_virtual_pin(6, read=v6_read)

#Water Level (option 5)
def v7_read():
  ser.write(bytes('7', encoding='utf-8'))
  result = wait_for_json()
  print(result)
  blynk.virtual_write(7, result['v'])

blynk.add_virtual_pin(7, read=v7_read)

#Fan Programme (30000 < option <= 50000)
def v8_write(param):
  if(param[0] == 1):
    ser.write(bytes('49999', encoding='utf-8'))
  else:
    ser.write(bytes('30001', encoding='utf-8'))
    blynk.virtual_write(8, 0)

def v8_read():
  ser.write(bytes('50000', encoding='utf-8'))
  result = wait_for_json()
  print(result)
  blynk.virtual_write(8, result['v'])

blynk.add_virtual_pin(8, write=v8_write, read=v8_read)

#Pump Programme (10000 < option <= 30000)
def v9_write(param):
  if(param[0] == 1):
    ser.write(bytes('29999', encoding='utf-8'))
  else:
    ser.write(bytes('10001', encoding='utf-8'))
    blynk.virtual_write(9, 0)

def v9_read():
  ser.write(bytes('30000', encoding='utf-8'))
  result = wait_for_json()
  print(result)
  blynk.virtual_write(9, result['v'])


blynk.add_virtual_pin(9, write=v9_write, read=v9_read)

def option_read():
  result = wait_for_json()
  sensor_id = globals()['sensor_id']
  globals()['v' + str(sensor_id) + '_read']()
  globals()['sensor_id'] = (sensor_id % 9) + 1

blynk.set_user_task(option_read, 100)

if __name__ == '__main__':
  sensor_id = 1
  blynk.run()
