#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Lora Receive Realtime
# Generated: Sun Dec 30 15:05:11 2018
##################################################


from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import zeromq
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import lora
import osmosdr
import time


class lora_receive_realtime(gr.top_block):

    def __init__(self, target_freq, sf):
        gr.top_block.__init__(self, "Lora Receive Realtime")

        ##################################################
        # Variables
        ##################################################
        self.target_freq = target_freq
        self.sf = sf
        self.samp_rate = samp_rate = 1e6
        self.downlink = downlink = False
        self.decimation = decimation = 1
        self.capture_freq = capture_freq = 868e6
        self.bw = bw = 125000
        self.address = address = "tcp://127.0.0.1:5001"

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_push_msg_sink_1 = zeromq.push_msg_sink("tcp://127.0.0.1:5002", 100)
        self.zeromq_pub_msg_sink_0 = zeromq.pub_msg_sink(address, 100)
        self.osmosdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + 'rtl_tcp=127.0.0.1:7373' )
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(capture_freq, 0)
        self.osmosdr_source_0.set_freq_corr(0, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(False, 0)
        self.osmosdr_source_0.set_gain(10, 0)
        self.osmosdr_source_0.set_if_gain(20, 0)
        self.osmosdr_source_0.set_bb_gain(20, 0)
        self.osmosdr_source_0.set_antenna('', 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)

        self.lora_message_socket_sink_0 = lora.message_socket_sink('127.0.0.1', 5005, 2)
        self.lora_lora_receiver_0 = lora.lora_receiver(1e6, capture_freq, ([target_freq]), bw, sf, False, 4, True, False, downlink, decimation, False, False)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.lora_lora_receiver_0, 'frames'), (self.lora_message_socket_sink_0, 'in'))
        self.msg_connect((self.lora_lora_receiver_0, 'frames'), (self.zeromq_pub_msg_sink_0, 'in'))
        self.msg_connect((self.lora_lora_receiver_0, 'frames'), (self.zeromq_push_msg_sink_1, 'in'))
        self.connect((self.osmosdr_source_0, 0), (self.lora_lora_receiver_0, 0))

    def get_target_freq(self):
        return self.target_freq

    def set_target_freq(self, target_freq):
        self.target_freq = target_freq

    def get_sf(self):
        return self.sf

    def set_sf(self, sf):
        self.sf = sf
        self.lora_lora_receiver_0.set_sf(self.sf)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)

    def get_downlink(self):
        return self.downlink

    def set_downlink(self, downlink):
        self.downlink = downlink

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation

    def get_capture_freq(self):
        return self.capture_freq

    def set_capture_freq(self, capture_freq):
        self.capture_freq = capture_freq
        self.osmosdr_source_0.set_center_freq(self.capture_freq, 0)

    def get_bw(self):
        return self.bw

    def set_bw(self, bw):
        self.bw = bw

    def get_address(self):
        return self.address

    def set_address(self, address):
        self.address = address


def main(top_block_cls=lora_receive_realtime, options=None):

    tb = top_block_cls()
    tb.start()
    try:
        raw_input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
