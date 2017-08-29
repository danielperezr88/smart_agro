#!/usr/bin/env python
from BlynkLib import Blynk
from time import ticks_ms
import json

import asyncio
import serial_asyncio

from flask import Flask, render_template, Response
from camera_pi_proc import Camera


app = Flask(__name__)

blynk = Blynk('62e3b56640974018aa5779f87cdd51cb')
ser = None
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
    if int(param) == 1:
        ser.write(bytes('49999', encoding='utf-8'))
    else:
        ser.write(bytes('30001', encoding='utf-8'))


def v8_read():
    ser.write(bytes(vpin_option_dict[8], encoding='utf-8'))

blynk.add_virtual_pin(8, write=v8_write, read=v8_read)


# Pump Programme (10000 < option <= 30000)
def v9_write(param):    
    if int(param) == 1:
        ser.write(bytes('29999', encoding='utf-8'))
    else:
        ser.write(bytes('10001', encoding='utf-8'))


def v9_read():
    ser.write(bytes(vpin_option_dict[9], encoding='utf-8'))

blynk.add_virtual_pin(9, write=v9_write, read=v9_read)


class Output(asyncio.Protocol):

    def __init__(self):
        super().__init__()
        self.transport = None

    def connection_made(self, transport):
        global ser
        self.transport = transport
        print('port opened', transport)
        transport.serial.rts = False
        ser = transport
        blynk.set_user_task(self.option_read, 100)

    @staticmethod
    def option_read():
        global sensor_id, timestamp
        if ticks_ms() - timestamp > 5000:
            timestamp += 5000
            globals()['v' + str(sensor_id) + '_read']()
            sensor_id = (sensor_id + 1) % 10

    def data_received(self, data):

        global sensor_id, timestamp, json_raw

        json_raw += data.decode('utf-8').strip('\n').strip('\r')

        while json_raw[0] != '{' if len(json_raw) > 0 else False:
            json_raw = json_raw[1:]

        if len(json_raw) == 0:
            return

        close_idx = json_raw.find('}')
        if close_idx == -1:
            return

        try:
            result = json.loads(json_raw[:close_idx + 1])
        except ValueError as e:
            print('Error: ' + str(e), flush=True)
            return

        if result is not None:

            json_raw = json_raw[close_idx + 1:]

            option = result['o']
            print(result, flush=True)
            if 10000 < option <= 29999 or 30000 < option <= 49999:
                pass
            elif option in [int(v) for v in vpin_option_dict.values()]:
                blynk.virtual_write(dict((v, k) for k, v in vpin_option_dict.items())[str(option)], result['v'])
            else:
                print('Error: unknown option #%d' % (option,))

    def connection_lost(self, exc):
        print('port closed')
        self.transport.loop.stop()

    def pause_writing(self):
        print('pause writing')
        print(self.transport.get_write_buffer_size())
        print('resume writing')

    def write(self, msg):
        self.transport.write(msg)

    def close(self):
        self.transport.close()


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def flask_run():
    app.run(host='0.0.0.0', threaded=True, port=5001)


@asyncio.coroutine
def blynk_runner(l):
    yield from l.run_in_executor(None, blynk.run)


@asyncio.coroutine
def flask_runner(l):
    yield from l.run_in_executor(None, flask_run)


if __name__ == '__main__':

    loop = asyncio.get_event_loop()

    coor = serial_asyncio.create_serial_connection(loop, Output, '/dev/serial0', baudrate=115200)

    loop.run_until_complete(
        asyncio.wait([
            coor,
            blynk_runner(loop),
            flask_runner(loop)
        ])
    )

    loop.run_forever()
    loop.close()
