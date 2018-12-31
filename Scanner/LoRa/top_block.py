#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Top Block
# Generated: Sun Dec 30 14:52:50 2018
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


class top_block(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Top Block")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1e6
        self.capture_freq = capture_freq = 868e6

        ##################################################
        # Blocks
        ##################################################
        self.zeromq_push_msg_sink_0 = zeromq.push_msg_sink('tcp://127.0.0.1:5002', 100)
        self.zeromq_pub_msg_sink_0 = zeromq.pub_msg_sink('tcp://127.0.0.1:5001', 100)
        self.rtlsdr_source_1 = osmosdr.source( args="numchan=" + str(1) + " " + 'rtl_tcp=localhost:7373' )
        self.rtlsdr_source_1.set_sample_rate(samp_rate)
        self.rtlsdr_source_1.set_center_freq(capture_freq, 0)
        self.rtlsdr_source_1.set_freq_corr(0, 0)
        self.rtlsdr_source_1.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_1.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_1.set_gain_mode(False, 0)
        self.rtlsdr_source_1.set_gain(10, 0)
        self.rtlsdr_source_1.set_if_gain(20, 0)
        self.rtlsdr_source_1.set_bb_gain(20, 0)
        self.rtlsdr_source_1.set_antenna('', 0)
        self.rtlsdr_source_1.set_bandwidth(0, 0)

        self.lora_message_socket_sink_0 = lora.message_socket_sink('127.0.0.1', 5005, 1)
        self.lora_lora_receiver_0 = lora.lora_receiver(samp_rate, capture_freq, ([868.1e6]), 125000, 7, False, 4, True, False, False, 1, False, False)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.lora_lora_receiver_0, 'frames'), (self.lora_message_socket_sink_0, 'in'))
        self.msg_connect((self.lora_lora_receiver_0, 'frames'), (self.zeromq_pub_msg_sink_0, 'in'))
        self.msg_connect((self.lora_lora_receiver_0, 'frames'), (self.zeromq_push_msg_sink_0, 'in'))
        self.connect((self.rtlsdr_source_1, 0), (self.lora_lora_receiver_0, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.rtlsdr_source_1.set_sample_rate(self.samp_rate)

    def get_capture_freq(self):
        return self.capture_freq

    def set_capture_freq(self, capture_freq):
        self.capture_freq = capture_freq
        self.rtlsdr_source_1.set_center_freq(self.capture_freq, 0)


def main(top_block_cls=top_block, options=None):

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
