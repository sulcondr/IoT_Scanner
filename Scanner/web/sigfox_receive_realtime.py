#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Sigfox Receive Realtime
# Generated: Mon Dec 24 08:28:50 2018
##################################################


from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import sigfox


class sigfox_receive_realtime(gr.top_block):

    def __init__(self, udp_port):
        gr.top_block.__init__(self, "Sigfox Receive Realtime")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 250000
        self.taps = taps = firdes.low_pass(1,samp_rate,100,50,firdes.WIN_HAMMING)
        self.decim_second = decim_second = 250
        self.decim_first = decim_first = 5
        self.udp_port = udp_port

        ##################################################
        # Blocks
        ##################################################
        self.sigfox_packet_sink_scapy_0_1_1_9 = sigfox.packet_sink_scapy()
        self.sigfox_packet_sink_scapy_0_1_1_8 = sigfox.packet_sink_scapy()
        self.sigfox_packet_sink_scapy_0_1_1_7 = sigfox.packet_sink_scapy()
        self.sigfox_Detection_Peak_0 = sigfox.Detection_Peak(90, samp_rate/6.28)
        self.freq_xlating_fir_filter_xxx_0_1_9 = filter.freq_xlating_fir_filter_ccc(decim_first, (taps), 0, samp_rate)
        self.freq_xlating_fir_filter_xxx_0_1_8 = filter.freq_xlating_fir_filter_ccc(decim_first, (taps), 0, samp_rate)
        self.freq_xlating_fir_filter_xxx_0_1_7 = filter.freq_xlating_fir_filter_ccc(decim_first, (taps), 0, samp_rate)
        self.fir_filter_xxx_0_1 = filter.fir_filter_ccc(decim_second, (1, ))
        self.fir_filter_xxx_0_1.declare_sample_delay(0)
        self.fir_filter_xxx_0_0 = filter.fir_filter_ccc(decim_second, (1, ))
        self.fir_filter_xxx_0_0.declare_sample_delay(0)
        self.fir_filter_xxx_0 = filter.fir_filter_ccc(decim_second, (1, ))
        self.fir_filter_xxx_0.declare_sample_delay(0)
        self.digital_diff_decoder_bb_0_0_0_1_1_9 = digital.diff_decoder_bb(2)
        self.digital_diff_decoder_bb_0_0_0_1_1_8 = digital.diff_decoder_bb(2)
        self.digital_diff_decoder_bb_0_0_0_1_1_7 = digital.diff_decoder_bb(2)
        self.digital_costas_loop_cc_0_0_0_0_0_0_0_1_2_1_1_1_9 = digital.costas_loop_cc(6.28/100, 2, False)
        self.digital_costas_loop_cc_0_0_0_0_0_0_0_1_2_1_1_1_8 = digital.costas_loop_cc(6.28/100, 2, False)
        self.digital_costas_loop_cc_0_0_0_0_0_0_0_1_2_1_1_1_7 = digital.costas_loop_cc(6.28/100, 2, False)
        self.digital_clock_recovery_mm_xx_0_0_1_1_9 = digital.clock_recovery_mm_cc(2, 0.25*0.175*0.175, 0.5, 0.175, 0.005)
        self.digital_clock_recovery_mm_xx_0_0_1_1_8 = digital.clock_recovery_mm_cc(2, 0.25*0.175*0.175, 0.5, 0.175, 0.005)
        self.digital_clock_recovery_mm_xx_0_0_1_1_7 = digital.clock_recovery_mm_cc(2, 0.25*0.175*0.175, 0.5, 0.175, 0.005)
        self.digital_binary_slicer_fb_0_1_1_9 = digital.binary_slicer_fb()
        self.digital_binary_slicer_fb_0_1_1_8 = digital.binary_slicer_fb()
        self.digital_binary_slicer_fb_0_1_1_7 = digital.binary_slicer_fb()
        self.blocks_socket_pdu_0_0_1 = blocks.socket_pdu("UDP_CLIENT", '127.0.0.1', self.udp_port, 10000, False)
        self.blocks_message_debug_0_0_0_1_1 = blocks.message_debug()
        self.blocks_message_debug_0 = blocks.message_debug()
        self.blocks_complex_to_real_0_1_1_9 = blocks.complex_to_real(1)
        self.blocks_complex_to_real_0_1_1_8 = blocks.complex_to_real(1)
        self.blocks_complex_to_real_0_1_1_7 = blocks.complex_to_real(1)
        self.analog_simple_squelch_cc_1_1_0 = analog.simple_squelch_cc(-20, 1)
        self.analog_pll_freqdet_cf_0 = analog.pll_freqdet_cf(6.28/100, 6.28*110e3/samp_rate, -6.28*110e3/samp_rate)
        self.analog_const_source_x_0 = analog.sig_source_c(0, analog.GR_CONST_WAVE, 0, 0, 0)

        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.sigfox_Detection_Peak_0, 'out0'), (self.blocks_message_debug_0, 'print'))
        self.msg_connect((self.sigfox_Detection_Peak_0, 'out1'), (self.blocks_message_debug_0, 'print'))
        self.msg_connect((self.sigfox_Detection_Peak_0, 'out2'), (self.blocks_message_debug_0, 'print'))
        self.msg_connect((self.sigfox_Detection_Peak_0, 'out0'), (self.freq_xlating_fir_filter_xxx_0_1_7, 'freq'))
        self.msg_connect((self.sigfox_Detection_Peak_0, 'out1'), (self.freq_xlating_fir_filter_xxx_0_1_8, 'freq'))
        self.msg_connect((self.sigfox_Detection_Peak_0, 'out2'), (self.freq_xlating_fir_filter_xxx_0_1_9, 'freq'))
        self.msg_connect((self.sigfox_packet_sink_scapy_0_1_1_7, 'out'), (self.blocks_message_debug_0_0_0_1_1, 'print'))
        self.msg_connect((self.sigfox_packet_sink_scapy_0_1_1_7, 'out'), (self.blocks_socket_pdu_0_0_1, 'pdus'))
        self.msg_connect((self.sigfox_packet_sink_scapy_0_1_1_8, 'out'), (self.blocks_message_debug_0_0_0_1_1, 'print'))
        self.msg_connect((self.sigfox_packet_sink_scapy_0_1_1_8, 'out'), (self.blocks_socket_pdu_0_0_1, 'pdus'))
        self.msg_connect((self.sigfox_packet_sink_scapy_0_1_1_9, 'out'), (self.blocks_message_debug_0_0_0_1_1, 'print'))
        self.msg_connect((self.sigfox_packet_sink_scapy_0_1_1_9, 'out'), (self.blocks_socket_pdu_0_0_1, 'pdus'))
        self.connect((self.analog_const_source_x_0, 0), (self.analog_simple_squelch_cc_1_1_0, 0))
        self.connect((self.analog_pll_freqdet_cf_0, 0), (self.sigfox_Detection_Peak_0, 0))
        self.connect((self.analog_simple_squelch_cc_1_1_0, 0), (self.analog_pll_freqdet_cf_0, 0))
        self.connect((self.analog_simple_squelch_cc_1_1_0, 0), (self.freq_xlating_fir_filter_xxx_0_1_7, 0))
        self.connect((self.analog_simple_squelch_cc_1_1_0, 0), (self.freq_xlating_fir_filter_xxx_0_1_8, 0))
        self.connect((self.analog_simple_squelch_cc_1_1_0, 0), (self.freq_xlating_fir_filter_xxx_0_1_9, 0))
        self.connect((self.blocks_complex_to_real_0_1_1_7, 0), (self.digital_binary_slicer_fb_0_1_1_7, 0))
        self.connect((self.blocks_complex_to_real_0_1_1_8, 0), (self.digital_binary_slicer_fb_0_1_1_8, 0))
        self.connect((self.blocks_complex_to_real_0_1_1_9, 0), (self.digital_binary_slicer_fb_0_1_1_9, 0))
        self.connect((self.digital_binary_slicer_fb_0_1_1_7, 0), (self.digital_diff_decoder_bb_0_0_0_1_1_7, 0))
        self.connect((self.digital_binary_slicer_fb_0_1_1_8, 0), (self.digital_diff_decoder_bb_0_0_0_1_1_8, 0))
        self.connect((self.digital_binary_slicer_fb_0_1_1_9, 0), (self.digital_diff_decoder_bb_0_0_0_1_1_9, 0))
        self.connect((self.digital_clock_recovery_mm_xx_0_0_1_1_7, 0), (self.blocks_complex_to_real_0_1_1_7, 0))
        self.connect((self.digital_clock_recovery_mm_xx_0_0_1_1_8, 0), (self.blocks_complex_to_real_0_1_1_8, 0))
        self.connect((self.digital_clock_recovery_mm_xx_0_0_1_1_9, 0), (self.blocks_complex_to_real_0_1_1_9, 0))
        self.connect((self.digital_costas_loop_cc_0_0_0_0_0_0_0_1_2_1_1_1_7, 0), (self.fir_filter_xxx_0, 0))
        self.connect((self.digital_costas_loop_cc_0_0_0_0_0_0_0_1_2_1_1_1_8, 0), (self.fir_filter_xxx_0_0, 0))
        self.connect((self.digital_costas_loop_cc_0_0_0_0_0_0_0_1_2_1_1_1_9, 0), (self.fir_filter_xxx_0_1, 0))
        self.connect((self.digital_diff_decoder_bb_0_0_0_1_1_7, 0), (self.sigfox_packet_sink_scapy_0_1_1_7, 0))
        self.connect((self.digital_diff_decoder_bb_0_0_0_1_1_8, 0), (self.sigfox_packet_sink_scapy_0_1_1_8, 0))
        self.connect((self.digital_diff_decoder_bb_0_0_0_1_1_9, 0), (self.sigfox_packet_sink_scapy_0_1_1_9, 0))
        self.connect((self.fir_filter_xxx_0, 0), (self.digital_clock_recovery_mm_xx_0_0_1_1_7, 0))
        self.connect((self.fir_filter_xxx_0_0, 0), (self.digital_clock_recovery_mm_xx_0_0_1_1_8, 0))
        self.connect((self.fir_filter_xxx_0_1, 0), (self.digital_clock_recovery_mm_xx_0_0_1_1_9, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0_1_7, 0), (self.digital_costas_loop_cc_0_0_0_0_0_0_0_1_2_1_1_1_7, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0_1_8, 0), (self.digital_costas_loop_cc_0_0_0_0_0_0_0_1_2_1_1_1_8, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0_1_9, 0), (self.digital_costas_loop_cc_0_0_0_0_0_0_0_1_2_1_1_1_9, 0))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_taps(firdes.low_pass(1,self.samp_rate,100,50,firdes.WIN_HAMMING))
        self.analog_pll_freqdet_cf_0.set_max_freq(6.28*110e3/self.samp_rate)
        self.analog_pll_freqdet_cf_0.set_min_freq(-6.28*110e3/self.samp_rate)

    def get_taps(self):
        return self.taps

    def set_taps(self, taps):
        self.taps = taps
        self.freq_xlating_fir_filter_xxx_0_1_9.set_taps((self.taps))
        self.freq_xlating_fir_filter_xxx_0_1_8.set_taps((self.taps))
        self.freq_xlating_fir_filter_xxx_0_1_7.set_taps((self.taps))

    def get_decim_second(self):
        return self.decim_second

    def set_decim_second(self, decim_second):
        self.decim_second = decim_second

    def get_decim_first(self):
        return self.decim_first

    def set_decim_first(self, decim_first):
        self.decim_first = decim_first


def main(top_block_cls=sigfox_receive_realtime, options=None):

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
