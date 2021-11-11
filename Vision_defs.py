import cv2
import serial
import numpy as np
from datetime import datetime


class SaveImages:
    def __init__(self, window_, id_ima, ini_t):
        self.window = window_
        self.id_ima = id_ima
        self.ini_time = ini_t
        self.time_c = None

    def save(self, path, name_i, type_, time_c, values, image):
        filename = path + name_i + str(self.id_ima) + type_
        delta_t = datetime.now() - self.ini_time
        self.time_c = time_c
        time_sleep = delta_t.seconds
        if values['_TMI_']:
            time_sleep /= 60
        rest_time = np.round(self.time_c - time_sleep, 4)
        self.window['_RES_'].update(rest_time)
        # -----------------------------------------------------------------
        if self.time_c == time_sleep or self.id_ima == 1:
            print(filename)
            print('SAVE IMAGE SUCCESSFULLY')
            cv2.imwrite(filename, image)
            self.window['_CIM_'].update(self.id_ima)
            self.ini_time = datetime.now()
            self.id_ima += 1


class ControlPump:
    def __init__(self, window_, init_t, ctr, port_n, bauds):
        self.window = window_
        self.ini_time = init_t
        self.control = ctr
        self.port_name = port_n
        self.bauds = bauds
        self.fluid_H, self.fluid_L, self.time_H, self.time_L, self.port = None, None, None, None, None

    def active_pump(self, v_fluid):
        self.port = serial.Serial(port=self.port_name,
                                  baudrate=self.bauds,
                                  bytesize=serial.EIGHTBITS,
                                  parity=serial.PARITY_NONE,
                                  stopbits=serial.STOPBITS_ONE)
        # Start pump
        self.port.write(b'<<J000R>\n')
        # Vary flow pump
        if v_fluid < 100:
            cad_port = '<<J000F00' + str(v_fluid) + '.0000>\n'
        else:
            cad_port = '<<J000F0' + str(v_fluid) + '.0000>\n'
        self.port.write(bytes(cad_port.encode()))
        # Stop pump
        self.port.write(b'<<J000S>\n')
        self.port.close()

    def control_pump(self, fluid_h_, fluid_l_, time_h_, time_l_):
        self.fluid_H, self.fluid_L, self.time_H, self.time_L = fluid_h_, fluid_l_, time_h_, time_l_
        delta = datetime.now() - self.ini_time
        time_sleep = delta.seconds / 60

        if self.control:
            rest_time = np.round(self.time_H - time_sleep, 4)
            print('Highest fluid : ' + str(self.fluid_H) + ' ul/min.  Remaining time ----->> ' + str(rest_time))
            if rest_time > 0:
                self.window['_MES_'].update('Highest fluid is activated')
                self.active_pump(self.fluid_H)
            else:
                self.control = False
                self.ini_time = datetime.now()
        else:
            rest_time = np.round(self.time_L - time_sleep, 4)
            print('Lowest fluid: ' + str(self.fluid_L) + ' ul/min.  Remaining time ----->> ' + str(rest_time))
            if rest_time > 0:
                self.window['_MES_'].update('Lowest fluid is activated')
                self.active_pump(self.fluid_L)
            else:
                self.control = True
                self.ini_time = datetime.now()


def bytes_(img_, m, n):
    ima = cv2.resize(img_, (m, n))
    return cv2.imencode('.png', ima)[1].tobytes()


def camera_idx():
    # checks the first 10 indexes.
    index_ = 10
    videos = []
    for idx_ in range(index_):
        cap = cv2.VideoCapture(idx_)
        if cap.read()[0]:
            videos.append(idx_)
            cap.release()
    return videos


def update_dir(path):
    path_s = path.split('/')
    cad, path_f = len(path_s), path_s[0]
    for p in range(1, cad):
        path_f += '\\' + path_s[p]
    return path_f


def serial_test(port_n, bauds):
    try:
        c, port = 1, serial.Serial(port=port_n,
                                   baudrate=bauds,
                                   bytesize=serial.EIGHTBITS,
                                   parity=serial.PARITY_NONE,
                                   stopbits=serial.STOPBITS_ONE)
        print('--------------------------------------')
        print('           Port: ' + port.name)
        print('----------- Test successfully --------')

    except serial.SerialException:
        print('------- Port is not available ---------')
        c = 0
    return c

