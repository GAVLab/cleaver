#!/usr/bin/env python

import sys
import os
import struct
import binascii

IF_RATE = 16.3676e6

def get_sign_mag(sample_value):
    if sample_value == '\x01':
        # 1
        sign_mag = '00'
    elif sample_value == '\x03':
        # 3
        sign_mag = '01'
    elif sample_value == '\xff':
        # -1
        sign_mag = '10'
    elif sample_value == '\xfd':
        # -3
        sign_mag = '11'
    else:
        print 'invalid sample value:', sample_value, binascii.hexlify(sample_value)
        return None
    return sign_mag
 

def get_sample(sample_value):
    if sample_value == '\x01':
        sign_mag = 0
    elif sample_value == '\x03':
        sign_mag = 1
    elif sample_value == '\xff':
        sign_mag = 2
    elif sample_value == '\xfd':
        sign_mag = 3
    else:
        print 'invalid sample value:', sample_value, binascii.hexlify(sample_value)
    return sign_mag

def compactor(data):
    compacted = 0
    compacted |= get_sample(data[0]) << 6
    compacted |= get_sample(data[1]) << 4
    compacted |= get_sample(data[2]) << 2
    compacted |= get_sample(data[3])
    return struct.pack('=B', compacted)

class Force:
    def __init__(self, step=61.1):
        self.time = 0.
        self.step = step

    def header(self):
        return 'force -freeze /sig_in'

    def epoch(self, sample_value):
        if sample_value == '\x01':
            # 1
            sign_mag = '00'
        elif sample_value == '\x03':
            # 3
            sign_mag = '01'
        elif sample_value == '\xff':
            # -1
            sign_mag = '10'
        elif sample_value == '\xfd':
            # -3
            sign_mag = '11'
        else:
            print 'invalid sample value:', sample_value, binascii.hexlify(sample_value)
        t = round(self.time, 1).__str__()
        self.time += self.step
        return sign_mag + ' ' + t + 'ns'

    def force_line(self, sample_value):
        if sample_value == '\x01':
            # 1
            sign_mag = '00'
        elif sample_value == '\x03':
            # 3
            sign_mag = '01'
        elif sample_value == '\xff':
            # -1
            sign_mag = '10'
        elif sample_value == '\xfd':
            # -3
            sign_mag = '11'
        else:
            print 'invalid sample value:', sample_value, binascii.hexlify(sample_value)
        t = round(self.time, 1).__str__()
        self.time += self.step
        return 'force -freeze $tbpath${ps}gps_data_in_pin ' + sign_mag + ' ' + t + 'ns'
    
if len(sys.argv) < 3:
    print 'use: cleaver.py file seconds [options]'
    print 'options: -p = packed'
    print '         -f = force file'
    print '         -d = sign and magnitude data'
elif not os.path.isfile(sys.argv[1]):
    print 'not a valid file'
else:
    try:
        num = float(sys.argv[2])
    except ValueError:
        num = 0.
    if num > 0.:
        infile = open(sys.argv[1], 'rb')
        if '-p' in sys.argv:
            samples = int(num*IF_RATE/4)
            outfile = open(str(int(num)) + 'p' + sys.argv[1].split('/')[-1],
                    'wb')
            print 'packing', samples*4, 'samples'
            for byte in xrange(samples):
                outfile.write(compactor(infile.read(4)))
        elif '-f' in sys.argv:
            force = Force()
            samples = int(num*IF_RATE)
            outfile = open("force_" + sys.argv[1].split('/')[-1], 'w')
            print 'cleaving', samples, 'samples'
            outfile.write(force.header())
            for byte in xrange(samples):
                outfile.write(' ' + force.epoch(infile.read(1)))
                if byte != samples-1:
                    outfile.write(',')
                #outfile.write(force.force_line(infile.read(1)) + '\n')
        elif '-d' in sys.argv:
            samples = int(num*IF_RATE)
            outlife = open("signmag_" + sys.argv[1].split('/')[-1], 'w')
            print 'cleaving', samples, 'samples'
            for byte in xrange(samples):
                outfile.write(get_sign_mag(infile.read(1)) + '\n')
        else:
            samples = int(num*IF_RATE)
            outfile = open(str(int(num)) + sys.argv[1].split('/')[-1], 'wb')
            print 'cleaving', samples, 'samples'
            for byte in xrange(samples):
                outfile.write(infile.read(1))
        outfile.close()
        infile.close()
        print 'finished writing'

