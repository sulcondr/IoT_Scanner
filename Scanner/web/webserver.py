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
from numpy import median
import socket
import time
import configparser
import argparse
import binascii
import struct
import eventlet

eventlet.monkey_patch()
from lora_receive_realtime import lora_receive_realtime
from sigfox_receive_realtime import sigfox_receive_realtime

app = Flask(__name__, static_url_path="")
# app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)


def parse_cli():
    """parses argument needed for choosing the right enviroment"""
    parser = argparse.ArgumentParser()
    parser.add_argument("ENV", help="Enviorment SCANNER, PC, REMOMTE")
    args = parser.parse_args()

    return args


def background_lora():
    """receives UDP frames from LoRa GNU radio session"""
    # time.sleep(15)
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((UDP_IP, UDP_LORA))
    print "LoRa UDP listening on port", UDP_LORA
    while True:
        recv, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print recv
        data = bytearray(recv)
        parsed = parse_frame(data)
        message = make_message(parsed)
        socketio.emit('lora', message)
        time.sleep(0.10)


def background_sigfox():
    """receives UDP frames from Sigfox GNU radio session"""
    # time.sleep(15)
    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((UDP_IP, int(UDP_SIGFOX)))
    print "Sigfox UDP listening on port", UDP_SIGFOX
    while True:
        recv, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
        print recv
        socketio.emit('sigfox', recv)
        time.sleep(0.10)


def make_message(parsed):
    """makes dictionary from the parsed data"""
    frame = {
        'technology': 'LoRa',
        'freq': parsed[3],
        'bw': parsed[4],
        'sf': parsed[5],
        'snr': parsed[9] / 100.0,
        'length': parsed[11],
        'payload': str(parsed[14]).decode('latin-1').encode("utf-8")
    }
    print frame
    return frame


def parse_frame(data):
    """parses LoRa frame received from GNU Radio"""
    test = binascii.hexlify(data)
    # defines the format of received LoRa frame header
    tap_header_format = 'bbhiibbbbib'
    phy_header_format = 'bbb'
    header_format = tap_header_format + phy_header_format
    print header_format
    header_len = struct.calcsize(header_format)
    data_len = len(data)
    if header_len > data_len:
        print 'packet too short'
        return (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,)
    else:
        # defines the frame format based on header and length of frame
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


def stop_lora_session(channel, sf):
    print 'stopping session ({}, {})'.format(channel, sf)
    LORA_SESSIONS[channel][sf].stop()
    LORA_SESSIONS[channel][sf].wait()
    del LORA_SESSIONS[channel][sf]
    time.sleep(1)
    print 'session stopped', LORA_SESSIONS


def start_lora_session(channel=868100000, sf=7):
    if channel not in LORA_SESSIONS:
        LORA_SESSIONS[channel] = {}
    if sf not in LORA_SESSIONS[channel]:
        try:
            LORA_SESSIONS[channel][sf] = lora_receive_realtime(channel, sf, UDP_LORA, RTL_ADDRESS, DECIMATION,
                                                               CAPTURE_FREQ)
            print LORA_SESSIONS
            print 'session on channel {} and SF {} created'.format(channel, sf)
        except RuntimeError as error:
            print('Failed to start LoRa receiver: {}'.format(error))
    try:
        LORA_SESSIONS[channel][sf].start()
        print 'session on channel {} and SF {} started'.format(channel, sf)
    except RuntimeError as error:
        if error != 'top_block::start: top block already running or wait() not called after previous stop()':
            print error
        else:
            print 'session already started'


def start_sigfox():
    SIGFOX_SESSIONS['sigfox'] = sigfox_receive_realtime(UDP_SIGFOX)
    try:
        SIGFOX_SESSIONS['sigfox'].start()
    except RuntimeError as error:
        print error


def resolve_settings(settings):
    """parses LoRa settings and sends the necessary commands to update it"""
    print('received settings: ' + str(settings))
    # Lora settings cannot be uodated while Sigfox is on as it would mess up its radio receiver
    if SETTINGS['sigfox'] == 'True':
        return "LoRa and Sigfox cannot be turned on at the same time"
    # at least one channel and one sf has to be chosen at all times
    if settings['sf'] and settings['channel']:
        if ONE_SESSION and ((len(settings['sf']) > 1) or (len(settings['channel']) > 1)):
            message = 'Sorry only one channel and one sf allowed at once on SCANNER'
            return message
        channel_list = [int(x) for x in settings['channel']]
        sf_list = [int(x) for x in settings['sf']]
        # takes the median freq of all selected channels so there is the biggest chance they all fall in BW of receiver
        CAPTURE_FREQ = median(channel_list)
        print CAPTURE_FREQ
        # stops all session that are not in the newest settings
        for channel in LORA_SESSIONS.keys():
            print type(channel), type(channel_list[0])

            for sf in LORA_SESSIONS[channel].keys():
                if channel not in channel_list:
                    stop_lora_session(channel, sf)
                else:
                    if sf not in sf_list:
                        stop_lora_session(channel, sf)
        # starts or updates all session specified in the newest settings
        for channel in channel_list:
            for sf in sf_list:
                start_lora_session(channel, sf)
                update_local_settings({'lora': 'True'})
        update_local_settings(settings)
        message = 'LORA: Started listening on channel(s) {} and decoding SF {}'.format(settings['channel'],
                                                                                       settings['sf'])
        return message
    else:
        message = 'Please set at least one channel and one SF'
        return message


def turn_off_lora():
    for channel in LORA_SESSIONS.keys():
        for sf in LORA_SESSIONS[channel].keys():
            stop_lora_session(channel, sf)


def turn_off_sigfox():

    SIGFOX_SESSIONS['sigfox'].stop()
    SIGFOX_SESSIONS['sigfox'].wait()
    del SIGFOX_SESSIONS['sigfox']
    print 'Turning off Sigfox'


@app.route("/")
def index():
    """
    makes index.html avaiable at the root address of the server
    :return:
    """
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
    """
    Is called when socket io message from topic settings is received
    It send the message to resolve and once it is resolved it sends messages back to the client updating his log
    and displayed settings
    :param settings:
    :param methods:
    :return:
    """
    message = resolve_settings(settings)
    socketio.emit('settings_update', SETTINGS)
    socketio.emit('log', message)


@socketio.on('switch')
def handle_switch(settings, methods=['GET', 'POST']):
    """
    Is called when socket io meassege from topic switch is received
    It parses the received message and based on content turns of and IoT technologies
    :param settings:
    :param methods:
    :return:
    """
    print(settings)
    message = ''
    if not ((settings['lora'] == "True") and (settings['sigfox'] == "True")):
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
        if settings['sigfox'] != SETTINGS['sigfox']:
            if settings['sigfox'] == "True":
                start_sigfox()
                message += 'Sigfox receiver turned ON \n'
            if settings['sigfox'] == 'False':
                turn_off_sigfox()
                message += 'Sigfox receiver turned OFF \n'
            socketio.emit('log', message)
        update_local_settings(settings)
    else:
        socketio.emit('log', "LoRa and Sigfox cannot be turned on at the same time")
    socketio.emit('settings_update', SETTINGS)


def clean_up_prevous():
    """
    Kills processes listening on port 7373 and 1234, normally these would be processes left
    there from previous run of this script
    :return:
    """
    rtl_mus = subprocess.Popen('lsof -n -i4TCP:7373 | grep LISTEN | awk \'{ print $2 }\' | xargs kill', shell=True)
    rtl_mus.wait()
    rtl_tcp = subprocess.Popen('lsof -n -i4TCP:1234 | grep LISTEN | awk \'{ print $2 }\' | xargs kill -9', shell=True)
    rtl_tcp.wait()


if __name__ == "__main__":
    env = parse_cli().env
    print env
    # loads config based on eviroment
    config = configparser.ConfigParser()
    config.read('config.ini')

    RTL_ADDRESS = str(config.get(env, 'RTL_ADDRESS'))               # address where TCP stream of IQ data can be found
    GET_RTL_ADDRESS = config.getboolean(env, 'GET_RTL_ADDRESS')     # should the addresse be asked as input from user
    ONE_SESSION = config.getboolean(env, 'ONE_SESSION')             # is receiver limimted per one session at the time?
    RUN_TCP_MUS = config.getboolean(env, 'RUN_TCP_MUS')             # should rtl_tcp and rtl_mus be run locally?
    HTTP_PORT = 5000                                                # port on which the interface is shown
    UDP_IP = "127.0.0.1"                                            # address to be bound be UDP rececivers
    UDP_LORA = 5005                                                 # port for LoRa receiver
    UDP_SIGFOX = '5006'                                             # port for Sigfox receiver
    SETTINGS = {'lora': 'False', 'sigfox': 'False', 'channel': [], 'sf': []}    # settings holder with initial settings
    LORA_SESSIONS = {}                                              # holder for LoRa session
    SIGFOX_SESSIONS = {}                                            # holder for Sigfox sessions
    DECIMATION = 1                                                  # decimation factor
    CAPTURE_FREQ = 868e6                                            # initial frequency set on RTL_SDR

    # sets higher decimation factor for SCANNER enviorment
    if ONE_SESSION:
        DECIMATION = 4

    # gets rtl stream address for REMOTE env
    if GET_RTL_ADDRESS:
        RTL_ADDRESS = 'rtl_tcp' + raw_input("Please input address for rtl_mus in format address:port")

    # starts rtl_tcp and rtl_mus for PC env
    if RUN_TCP_MUS:
        clean_up_prevous()
        rtl_tcp = subprocess.Popen(['rtl_tcp', '-f', '868000000', '-g', '10', '-s', '1000000'])
        time.sleep(1)
        subprocess.Popen(['./rtl_mus/rtl_mus.py'])
        # subprocess.Popen('exec ncat localhost 1234 | ncat -4l 7373 -k --send-only --allow 127.0.0.1', shell=True)

    # starting threads for UDP rreceivers
    thread1 = Thread(target=background_lora)
    thread1.daemon = True
    thread1.start()

    thread2 = Thread(target=background_sigfox)
    thread2.daemon = True
    thread2.start()
    # starting flask
    socketio.run(app, host="0.0.0.0", port=HTTP_PORT, debug=False)
