#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# heromote - remotely control gopro hero cameras
# Copyright (C) 2012 Jean-Michel Vourgère
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
from time import sleep
import struct
import socket
import urllib.request

PASSWORD=None

GP_PARAM_READ  = 1
GP_PARAM_WRITE = 2

CAM_IP = '10.5.5.9'

CAMERA_PARAMETERS = {
    'CM': {
        'txt': 'Camera mode',
        'perm': GP_PARAM_READ | GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Video',
            1: 'Photo',
            2: 'Burst',
            3: 'Time Lapse',
            4: 'Delayed',
            5: 'Play',
            7: 'Config',
            },
        },
    'DM': {
        'txt': 'Default mode',
        'perm': GP_PARAM_READ | GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Video',
            1: 'Photo',
            2: 'Burst',
            3: 'Time Lapse',
            },
        },
    'TI': {
        'txt': 'Time lapse',
        'perm': GP_PARAM_READ | GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: '0.5 s',
            1: '1 s',
            2: '2 s',
            5: '5 s',
            10: '10 s',
            30: '30 s',
            60: '60 s',
            },
        },
    'EX': {
        'txt': 'Spot',
        'perm': GP_PARAM_READ | GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Off',
            1: 'On',
            },
        },
    'AO': {
        'txt': 'Auto poweroff',
        'perm': GP_PARAM_READ | GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Never',
            1: '60 s',
            2: '120 s',
            3: '300 s',
            },
        },
    'FV': {
        'txt': '1080p field of view',
        'perm': GP_PARAM_READ | GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Wide',
            1: 'Medium',
            2: 'Narrow',
            },
        },
    'PR': {
        'txt': 'Photo resolution',
        'perm': GP_PARAM_READ | GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: '11MP wide',
            1: '8MP medium',
            2: '5MP wide',
            3: '5MP medium',
            },
        },
    'VR': {
        'txt': 'Video resolution',
        'perm': GP_PARAM_READ | GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'WVGA 50',
            1: 'WVGA 100',
            2: '720p 25',
            3: '720p 50',
            4: '960p 25',
            5: '960p 50',
            6: '1080p 25',
            7: '1080p 30 Protune',
            11: '1080p 25 Protune',
            8: '1080p 24 Protune',
            9: '960p 48 Protune',
            10: '720p 60 Protune',
            },
        },
    'PH': { # Name is a guess
        'txt': 'Printed hours',
        'perm': GP_PARAM_READ,
        },
    'PM': { # Name is a guess
        'txt': 'Printed minutes',
        'perm': GP_PARAM_READ,
        },
    'PS': { # Name is a guess
        'txt': 'Printed seconds',
        'perm': GP_PARAM_READ,
        },
    'BS': {
        'txt': 'Beep sound',
        'perm': GP_PARAM_READ | GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Off',
            1: '70%',
            2: '100%',
            },
        },
    'LB': {
        'txt': 'Led blinking',
        'perm': GP_PARAM_READ | GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Off',
            1: '2',
            2: '4',
            },
        },
    'PV': {
        'txt': 'Preview',
        'perm': GP_PARAM_READ | GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Off',
            1: 'Unknown',
            2: 'On', # ffplay "http://10.5.5.9:8080/live/amba.m3u8"
                     # ffmpeg -i http://10.5.5.9:8080/live/amba.m3u8 -f mpegts -vcodec copy pipe:1 | mplayer -
            },
        },
    'UP': {
        'txt': 'Upside Down',
        'perm': GP_PARAM_READ | GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Off',
            1: 'On',
            },
        },
    'OS': { # Name is a guess
        'txt': 'On screen display',
        'perm': GP_PARAM_READ,
        'values': {
            0: 'Off',
            1: 'On',
            },
        },
    'VM': {
        'txt': 'PAL',
        'perm': GP_PARAM_READ | GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Off',
            1: 'On',
            },
        },
    'LL': {
        'txt': 'Locate',
        'perm': GP_PARAM_READ | GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Off',
            1: 'On',
            },
        },
    'US': { # Name is a guess
        'txt': 'USB mode',
        'perm': GP_PARAM_READ,
        'values': {
            0: 'Off',
            1: 'On',
            },
        },
    'BL': { # Name is a guess
        'txt': 'Battery level',
        'perm': GP_PARAM_READ,
        },
    'BC': { # Name is a guess
        'txt': 'Battery charging',
        'perm': GP_PARAM_READ,
        },
    'SH': {
        'txt': 'Shoot',
        'perm': GP_PARAM_READ | GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Off',
            1: 'On',
            },
        },
    'RP': { # Name is a guess
        'txt': 'Remaining photo',
        'perm': GP_PARAM_READ,
        },
    'NP': { # Name is a guess
        'txt': 'Number of photos',
        'perm': GP_PARAM_READ,
        },
    'RV': { # Name is a guess
        'txt': 'Remaining video minutes',
        'perm': GP_PARAM_READ,
        },
    'NV': { # Name is a guess
        'txt': 'Number of videos',
        'perm': GP_PARAM_READ,
        },
    'DL': {
        'txt': 'Delete last',
        'perm': GP_PARAM_WRITE,
        'write_target': 'camera',
        },
    'DA': {
        'txt': 'Delete all',
        'perm': GP_PARAM_WRITE,
        'write_target': 'camera',
        },
    'TM': {
        'txt': 'Date/Time',
        'perm': GP_PARAM_WRITE,
        'write_target': 'camera',
        # time set: TM?p=%0c%0b%14%16%23%32 (yMDhms) \00+yMDhms
        },
    'AI': {
        'txt': 'Audio input(?)',
        'perm': GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Built-in mic',
            1: 'Unknown value 1',
            2: 'Unknown value 2',
            3: 'External mic',
            },
        },
    'MM': {
        'txt': 'Microphone mode',
        'perm': GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Unknown value 0 (stereo?)',
            1: 'Unknown value 1 (mono?)',
            },
        },
    'PI': { # Ping cam ?
        'txt': 'Unkown PI parameter',
        'perm': GP_PARAM_WRITE,
        'write_target': 'camera',
        },
    'CN': {
        'txt': 'Camera name', # Built-in is HERO2
        'perm': GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': str,
        },
    'OB': {
        'txt': 'One button mode',
        'perm': GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Off',
            1: 'On',
            },
        },
    'PT': {
        'txt': 'ProTune mode',
        'perm': GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Off',
            1: 'On',
            },
        },
    'BM': { # Bluetooth mode?
        'txt': 'Unknown BT command (bluetooth?)',
        'perm': GP_PARAM_WRITE,
        'write_target': 'camera',
        'values': {
            0: 'Unknown value 0',
            1: 'Unknown value 1',
            2: 'Unknown value 2',
            },
        },

    #PB...
    #DF... delete file?
    #IF
    #WI -> 0 disables wifi. can be sent to either /bacac or /camera
    #PM ->1=peering?
    #BO -> /bacpac 0=off
    #OO one on one ?
    #BP
    #SP
    #DS 0/1
    #HS
    #WS
    #IT
    #JW jump wifi mode?
    #
    'PW': {
        'txt': 'Camera power',
        'perm': GP_PARAM_WRITE,
        'write_target': 'bacpac',
        'values': {
            0: 'Off',
            1: 'On',
            2: 'Unknown',
            },
        },
    'ST': { # Name is a guess
        'txt': 'Internal status',
        'perm': GP_PARAM_READ,
        'values': {
            0: '0 - Setup or HD video rec (no preview)',
            1: '1 - Busy: burst (no preview)',
            2: '2 - Protune video recording (no preview)',
            4: '4 - Photo or non-protune video',
            6: '6 - Protune video',
            },
        },
    }


def perm_to_text(reg):
    read_flag = (reg['perm'] & GP_PARAM_READ) and 'r' or '-'
    write_flag = (reg['perm'] & GP_PARAM_WRITE) and 'w' or '-'
    return read_flag + write_flag

def print_reg(name, value):
    cam_reg = CAMERA_PARAMETERS[name]
    if 'values' in cam_reg and isinstance(cam_reg['values'], dict):
        disp_value = '%s (%s)' % (value, cam_reg['values'].get(value,'unexpected value = %s' % value) )
    else:
        disp_value = '%s' % value
    print ('%s %s (%s): %s' % (
        perm_to_text(cam_reg),
        name,
        cam_reg['txt'],
        disp_value,
        ))


__opener__ = None
def httpopen(url):
    global __opener__
    if __opener__ is None:
        __opener__ = urllib.request.build_opener()
    http_response = __opener__.open(url)
    return http_response


def init_cam():
    global PASSWORD
    try:
        bcv = httpopen('http://%s/bacpac/cv' % CAM_IP).read()
        print('bacpac CV:', repr(bcv))
        bacpac_version = struct.unpack('BBB', bcv[9:12])
        bacpac_version = '.'.join([str(x) for x in bacpac_version])
        print('   bacpac version:', bacpac_version)
        bacpac_mac = bcv[12:18]
        bacpac_mac = ':'.join(['%02x' % x for x in bacpac_mac])
        print('bacpac mac:', bacpac_mac)
        bacpac_name = bcv[19:].decode('utf-8')
        print('bacpac name:', bacpac_name)
        
        bsd = httpopen('http://%s/bacpac/sd' % CAM_IP).read()
        print('bacpac SD:', repr(bsd))
        PASSWORD = bsd[2:].decode('utf-8')
        print('bacpac password', PASSWORD)
     
        ccv = httpopen('http://%s/camera/cv' % CAM_IP).read()
        print('camera CV:', repr(ccv))
        # b'\x00\x00\x01\x13HD2.08.12.198.47.00\x05HERO2'
        dlen = struct.unpack('B', ccv[3:4])[0]
        camera_version = ccv[4:4+dlen].decode('UTF-8')
        print('camera version', camera_version)
        ipos = 4+dlen
        dlen = struct.unpack('B', ccv[ipos:ipos+1])[0]
        ipos += 1
        camera_model = ccv[ipos:ipos+dlen].decode('UTF-8')
        print('camera_model', camera_model) #FIXME this is the CN parameter
        return True
    except (urllib.error.HTTPError, urllib.error.URLError, socket.error):
        print('Error communicating with bacpac/camera')
        return False


def dump_bacpac():
    try:
        bse = httpopen('http://%s/bacpac/se?t=%s' % (CAM_IP, PASSWORD)).read()
    except (urllib.error.HTTPError, urllib.error.URLError, socket.error):
        print ("Can't access bacpac")
        return

    print("bacpac SE:", repr(bse))
    bpad0, bacpac_battery, bpad1, bpad2, bpad3, bpad4, bpad5, bpad6, bpad7, bpad8, bpad9, bpada, bpadb, bpadc, bpadd, bpade = struct.unpack('BbBBBBBBBBBBBBBB', bse)
    assert bpad0 == 0
    if bacpac_battery == -1:
        print("bacpac battery: charging")
    elif bacpac_battery == -2:
        print("bacpac battery: using camera power")
    else:
        print('bacpac battery:', bacpac_battery, '%')
    print ('r- bpad1:', bpad1)
    print ('r- bpad2:', bpad2)
    print ('r- bpad3:', bpad3)
    print ('r- bpad4:', bpad4)
    print ('r- bpad5:', bpad5)
    print ('r- bpad6:', bpad6)
    print ('r- bpad7:', bpad7)
    print ('r- bpad8:', bpad8)
    print ('r- bpad9:', bpad9)
    print ('r- bpada:', bpada)
    print ('r- bpadb:', bpadb)
    print ('r- bpadc:', bpadc)
    print ('r- cam_attached:', bpadd)
    print ('r- bpade:', bpade)
    #cam off:                     6:0 7:0  8:0 9:1 a:0 b:255 c:255 e:0
    #usb mode only, cam on:       6:0 7:0  8:1 9:0 a:1 b:1   c:0   e:0
    #SD error:              5:255 6:0 7:0  8:1 9:0 a:1 b:1   c:0   e:0
    #SD error:              5:255 6:0 7:34 8:1 9:0 a:1 b:1   c:0   e:1
    #cam fully on:                6:0 7:34 8:1 9:0 a:1 b:1   c:0   e:1

def dump_camera():
    try:
        cse = httpopen('http://%s/camera/se?t=%s' % (CAM_IP, PASSWORD)).read()
    except (urllib.error.HTTPError, urllib.error.URLError, socket.error):
        print ("Can't access camera")
        return
    #print("camera SE: ", repr(cse))
    decoded_cse = struct.unpack('>BBBBBBBBBBBBBBBBBBBBBhhhhBB', cse)
    cpad0, mode, cpad1, default_mode, spot, time_lapse, autooff, video_fov, photo_res, video_res, cpad2, cpad3, disp_hour, disp_min, disp_sec, cpad7, sound, led, flags, battery, cpad8, remaining_photo, nphoto, remaining_video_min, nvideo, shoot, cpada = decoded_cse
    assert cpad0 == 0
    assert cpad3 == 255

    preview = int(bool(flags & 0x01)) * 2 # hence 0 or 2
    assert flags & 0x06 == 0
    updown = int(bool(flags & 0x04))
    osd = int(bool(flags & 0x10))
    pal = int(bool(flags & 0x20))
    locate = int(bool(flags & 0x40)) 
    usb = int(bool(flags & 0x80))

    charging = bool(battery & 0x80)
    battery = battery & 0x7F

    protune = int(bool(video_res & 7))

    print_reg('CM', mode)
    print ('r- cpad1 (audio):', cpad1)
    print_reg('DM', default_mode)
    print_reg('TI', time_lapse)
    print_reg('EX', spot)
    print_reg('AO', autooff)
    print_reg('FV', video_fov)
    print_reg('PR', photo_res)
    print_reg('VR', video_res)
    print ('r- cpad2 (audio):', cpad2)
    print_reg('PH', disp_hour)
    print_reg('PM', disp_min)
    print_reg('PS', disp_sec)
    print ('r- cpad7 (playback):', cpad7) # playback
    print_reg('BS', sound)
    print_reg('LB', led)
    #print ('r- flag:', flags)
    print_reg('PV', preview)
    print_reg('UP', updown)
    print_reg('OS', osd)
    print_reg('VM', pal)
    print_reg('LL', locate)
    print_reg('US', usb)
    print_reg('BL', battery)
    print_reg('BC', charging)
    print ('r- cpad8:', cpad8) # 1 if ready, 0 if USB only, same as bpade ?
    print_reg('RP', remaining_photo)
    print_reg('NP', nphoto)
    print_reg('RV', remaining_video_min)
    print_reg('NV', nvideo)
    print_reg('SH', shoot)
    print_reg('ST', cpada)


def main():
    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options] { dump | monitor | list [RR] | {RR[=value]}+ }')
    parser.add_option('-t', '--target',
        action='store', dest='target', default='auto',
        help='Specifiy where to send command. Default=auto. Allowed values=auto,camera,bacpac')

    options, args = parser.parse_args()

    if len(args) < 1:
        print ("missing argument", file=sys.stderr)
        sys.exit(1)

    if args[0] == 'dump':
        if not init_cam():
            sys.exit(1)
        dump_bacpac()
        dump_camera()
        return
    
    if args[0] == 'monitor':
        if not init_cam():
            sys.exit(1)
        while True:
            dump_bacpac()
            dump_camera()
            sleep(1)
    
    if args[0] == 'list':
        if len(args) == 1:
            print('Known RR codes:')
            for reg_name in CAMERA_PARAMETERS:
                reg = CAMERA_PARAMETERS[reg_name]
                print(perm_to_text(reg), reg_name, reg['txt'])
            print()
            print('Note that read-only RR code are heromote specific and not built in your device.')
            print('Use "list RR" to get possible values.')
        else:
            for reg_name in args[1:]:
                reg = CAMERA_PARAMETERS[reg_name]
                if reg['perm'] == GP_PARAM_READ:
                    txtperm = 'READ-ONLY'
                elif reg['perm'] == GP_PARAM_WRITE:
                    txtperm = 'WRITE-ONLY'
                elif reg['perm'] == GP_PARAM_READ | GP_PARAM_WRITE:
                    txtperm = 'READ/WRITE'
                else:
                    txtperm = ''
                print(reg_name, ':', reg['txt'], '(', txtperm, ')')
                if 'values' in reg:
                    values = reg['values']
                    if isinstance(values, dict):
                        for val, txt in reg['values'].items():
                            print('\t', val, ':', txt)
                    else:
                        print('\t', values.__name__)
        return
 
    if not init_cam():
        pass
        #sys.exit(1)
    #PASSWORD = 'a'
    for arg in args:
        command = arg.split('=', 1)
        if len(command) == 1:
            command.append(None)
        reg_name, value = command
        if reg_name not in CAMERA_PARAMETERS:
            print ("Warning: unknown command", reg_name, file=sys.stderr)
        print (reg_name, '<-', value)
        
        target = options.target
        if target == 'auto':
            if reg_name not in CAMERA_PARAMETERS or 'write_target' not in CAMERA_PARAMETERS[reg_name]:
                print('You need to specify target with -t parameter for unknown parameters', file=sys.stderr)
                sys.exit(1)
            target = CAMERA_PARAMETERS[reg_name]['write_target']

        url = 'http://' + CAM_IP + '/' + target + '/'+ reg_name + '?t=' + PASSWORD
        param = None
        if value and reg_name in CAMERA_PARAMETERS and 'values' in CAMERA_PARAMETERS[reg_name]:
            values = CAMERA_PARAMETERS[reg_name]['values']
            if values == str:
                param = chr(len(value)) + value
        if param is None and value:
            value = int(value)
            assert value < 256
            param = chr(value)
        if param is not None:
            url += '&p='
            for c in param:
                if ord(c) < 32:
                    url += '%' + '%02x' % ord(c)
                else:
                    url += c
        print (url)

        try:
            rsp = httpopen(url).read()
            print ("HTTP response:", rsp)
            print_reg(reg_name, value)
        except urllib.error.URLError as err:
            print ('Communication error', err)


if __name__ == '__main__':
    main()
