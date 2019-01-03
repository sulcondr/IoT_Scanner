#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
#
import subprocess

from flask import Flask, request
from flask_socketio import SocketIO, emit
from threading import Thread
import socket
import time
import zmq
import pmt
import binascii
import struct
from lora_receive_realtime import lora_receive_realtime
from sigfox_receive_realtime import sigfox_receive_realtime

HTTP_PORT = 5000
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
RTL_ADDRESS = '192.168.0.23'
SETTINGS = {'lora': 'False', 'sigfox': 'False', 'channel': [], 'sf': []}
LORA_SESSIONS = {}

app = Flask(__name__, static_url_path="")
# app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)


def background_thread():
    # time.sleep(15)
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((UDP_IP, UDP_PORT))

    while True:
        recv, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        data = bytearray(recv)
        parsed = parse_frame(data)
        message = make_message(parsed)
        socketio.emit('gnu radio', message)
        time.sleep(0.10)


def make_message(parsed):
    frame = {
        'freq': parsed[3],
        'bw': parsed[4],
        'sf': parsed[5],
        'snr': parsed[9] / 100.0,
        'length': parsed[11],
        'payload': parsed[14]
    }
    print frame
    #socketio.emit('gnu_radio', frame)
    return frame

def parse_frame(data):
    test = binascii.hexlify(data)
    tap_header_format = 'bbhiibbbbib'
    phy_header_format = 'bbb'
    header_format = tap_header_format + phy_header_format
    print header_format
    header_len = struct.calcsize(header_format)
    data_len = len(data)
    if header_len > data_len:
        print 'bad packet received'
        return (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,)
    else:
        data_format = header_format + str(data_len - header_len) + 's'
        print data_format
        # print "tap header: ", header_len
        # print "data length: ", data_len
        # print "test length: ", len(test)

        unpacked = struct.unpack(data_format, data)
        print unpacked
        # print '-----------------------------------------------------'
        # print "bin " + data
        # print 'hex ' + test
        return unpacked


def update_local_settings(settings):
    for key in settings:
        SETTINGS[key] = settings[key]


def create_lora_session(channel, sf):
    if channel not in LORA_SESSIONS:
        LORA_SESSIONS[channel] = {}
    if sf not in LORA_SESSIONS[channel]:
        try:
            LORA_SESSIONS[channel][sf] = lora_receive_realtime(channel, sf, UDP_PORT)
            print LORA_SESSIONS
        except RuntimeError as error:
            print('Failed to start LoRa receiver: {}'.format(error))
        # LORA_SESSIONS[channel][sf].start()
        print 'session on channel {} and SF {} created'.format(channel, sf)
    else:
        print 'session already exists'


def stop_lora_session(channel, sf):
    print 'stopping session ({}, {})'.format(channel, sf)
    LORA_SESSIONS[channel][sf].stop()
    LORA_SESSIONS[channel][sf].wait()


def start_lora_session(channel=868100000, sf=7):
    # channel = int(channel)
    # sf = int(sf)
    create_lora_session(channel, sf)
    try:
        LORA_SESSIONS[channel][sf].start()
    except RuntimeError as error:
        if error != 'top_block::start: top block already running or wait() not called after previous stop()':
            print error
        print 'session already started'


def resolve_settings(settings):
    print('received settings: ' + str(settings))
    if settings['sf'] and settings['channel']:
        channel_list = [int(x) for x in settings['channel']]
        sf_list = [int(x) for x in settings['sf']]
        for channel in LORA_SESSIONS:
            print type(channel), type(channel_list[0])
            if channel not in channel_list:
                for sf in LORA_SESSIONS[channel]:
                    print LORA_SESSIONS
                    stop_lora_session(channel, sf)
            else:
                for sf in LORA_SESSIONS[channel]:
                    if sf not in sf_list:
                        stop_lora_session(channel, sf)
        for channel in channel_list:
            for sf in sf_list:
                start_lora_session(channel, sf)
                update_local_settings({'lora': 'True'})
        message = 'LORA: Started listening on channel(s) {} and decoding SF {}'.format(settings['channel'],
                                                                                       settings['sf'])
        return message
    else:
        message = 'Please set at least one channel and one SF'
        return message


def turn_off_lora():
    for channel in LORA_SESSIONS:
        for sf in LORA_SESSIONS[channel]:
            LORA_SESSIONS[channel][sf].stop()
            LORA_SESSIONS[channel][sf].wait()
            print 'turning off LORA ch={} sf={}'.format(channel, sf)


@app.route("/")
def index():
    return app.send_static_file("index.html")


@socketio.on("connect")
def connect():
    print("Client connected", request.sid)
    socketio.emit('settings_update', SETTINGS)


@socketio.on("disconnect")
def disconnect():
    print("Client disconnected", request.sid)


@socketio.on('settings')
def change_settings(settings, methods=['GET', 'POST']):
    message = resolve_settings(settings)
    update_local_settings(settings)
    socketio.emit('settings_update', SETTINGS)
    socketio.emit('log', message)


@socketio.on('switch')
def handle_switch(settings, methods=['GET', 'POST']):
    print(settings)
    message = ''
    if settings['lora'] != SETTINGS['lora']:
        if settings['lora'] == "True":
            start_lora_session()
            settings['channel'] = 868100000
            settings['sf'] = 7
            message += 'LoRa receiver turned ON \n'
        if settings['lora'] == "False":
            turn_off_lora()
            message += 'LoRa receiver turned OFF \n'
            settings['channel'] = []
            settings['sf'] = []
        socketio.emit('log', message)
    # if 'sigfox' in settings:
    #     if settings['sigfox'] == "True":
    #         sigfox.start()
    #         message += 'Sigfox receiver turned ON \n'
    #     if settings['sigfox'] == 'False':
    #         sigfox.stop()
    #         sigfox.wait()
    #         message += 'Sigfox receiver turned OFF \n'
    #     socketio.emit('log', message)
    update_local_settings(settings)
    socketio.emit('settings_update', SETTINGS)


if __name__ == "__main__":
    thread1 = Thread(target=background_thread)
    thread1.daemon = True
    thread1.start()

    # subprocess.Popen(['rtl_tcp', '-f', '868000000', '-g',  '10', '-s', '1000000'])
    # subprocess.Popen('exec ncat localhost 1234 | ncat -4l 7373 -k --send-only --allow 127.0.0.1', shell=True)
    print 'debug -------------------'

    socketio.run(app, host="0.0.0.0", port=HTTP_PORT, debug=False)
