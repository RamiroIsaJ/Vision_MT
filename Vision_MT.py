# Ramiro Isa-Jara, ramiro.isaj@gmail.com
# Vision Interface to use for viewing and saving images from Video Camera Input
# Activate Pump with high and low values
# This program uses 2 threads to avoid errors during the execution

import cv2
import threading
import numpy as np
import PySimpleGUI as sg
from datetime import datetime
import Vision_defs as Vs


def thread_images(path_des_, name_, type_i_, time1_, values_, image_):
    saveIm.save(path_des_, name_, type_i_, time1_, values_, image_)


def thread_pump(fluid_h_, fluid_l_, time_h_, time_l_):
    pumpC.control_pump(fluid_h_, fluid_l_, time_h_, time_l_)


# -------------------------------
# Adjust size screen
# -------------------------------
Screen_size = 10
# -------------------------------
sg.theme('LightGrey1')
m1, n1 = 450, 400
img = np.ones((m1, n1, 1), np.uint8)*255
portsWIN = ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'COM10', 'COM11']
portsLIN = ['/dev/pts/2', '/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2', '/dev/ttyS3']

layout1 = [[sg.Radio('Windows', "RADIO1", enable_events=True, default=True, key='_SYS_')],
           [sg.Radio('Linux', "RADIO1", enable_events=True, key='_LIN_')], [sg.Text('')]]

layout2 = [[sg.Checkbox('*.jpg', default=True, key="_IN1_")], [sg.Checkbox('*.png', default=False, key="_IN2_")],
           [sg.Checkbox('*.tiff', default=False, key="_IN3_")]]

idx = ['0']
layout3 = [[sg.Radio('Minutes', "RADIO2", enable_events=True, default=True, key='_TMI_'),
           sg.Radio('Seconds', "RADIO2", enable_events=True, key='_TSE_')],
           [sg.Text('Time to wait:', size=(10, 1)), sg.InputText('5', key='_INF_', enable_events=True, size=(7, 1))],
           [sg.Text('Id_ini image:', size=(10, 1)), sg.InputText('1', key='_IDI_', size=(7, 1))],
           [sg.Text('Video input: ', size=(10, 1)),
            sg.Combo(values=idx, size=(6, 1), enable_events=True, key='_VIN_')]]

layout4a = [[sg.Text('*Highest fluid:', size=(12, 1)),
             sg.InputText('100', key='_HST_', size=(5, 1), enable_events=True), sg.Text('ul/min.', size=(5, 1))],
            [sg.Text('*Time/highest:', size=(12, 1)),
             sg.InputText('60', key='_THS_', size=(5, 1), enable_events=True), sg.Text('min.', size=(4, 1))],
            [sg.Text('**Lowest fluid:', size=(12, 1)),
             sg.InputText('10', key='_LST_', size=(5, 1), enable_events=True), sg.Text('ul/min.', size=(5, 1))],
            [sg.Text('**Time/lowest:', size=(12, 1)),
             sg.InputText('5', key='_TLS_', size=(5, 1), enable_events=True),  sg.Text('min.', size=(4, 1))]]

layout4b = [[sg.Text('Name: ', size=(9, 1)),
            sg.Combo(values=portsWIN, size=(9, 1), enable_events=True, key='_PORT_')],
            [sg.Text('Baudrate:', size=(9, 1)), sg.InputText('9600', key='_RTE_', size=(10, 1))],
            [sg.Text('', size=(10, 1))],
            [sg.Text('Status:', size=(8, 1)), sg.Text('NOT CONNECT', size=(13, 1), key='_CON_', text_color='red')]]

layout5 = [[sg.Text('Name images: ', size=(12, 1)), sg.InputText('Experiment1_', size=(28, 1), key='_NAM_')],
           [sg.Text('Destiny: ', size=(12, 1)), sg.InputText(size=(28, 1), key='_DES_'), sg.FolderBrowse()]]

layout6 = [[sg.T("", size=(20, 1)), sg.Text('NO PROCESS', size=(29, 1), key='_MES_', text_color='DarkRed')]]

layout7 = [[sg.T("", size=(15, 1)), sg.Text('Current time: ', size=(10, 1)), sg.Text('', size=(10, 1), key='_TAC_')],
           [sg.T("", size=(2, 1)),
            sg.Text('Start time: ', size=(8, 1)), sg.Text('-- : -- : --', size=(10, 1), key='_TIN_', text_color='blue'),
            sg.T("", size=(5, 1)),
            sg.Text('Finish time: ', size=(8, 1)), sg.Text('-- : -- : --', size=(10, 1), key='_TFI_', text_color='red')],
           [sg.Text('Time remaining: ', size=(13, 1)), sg.InputText('', key='_RES_', size=(7, 1)),
            sg.Text('...', size=(4, 1), key='_ITM_'),
           sg.Text('Total/images: ', size=(12, 1)), sg.InputText('', key='_CIM_', size=(8, 1))]]


v_image = [sg.Image(filename='', key="_IMA_")]
# columns
col_1 = [[sg.Frame('', [v_image])]]
col_2 = [[sg.Frame('Operative System: ', layout1, title_color='Blue'),
          sg.Frame('Type image: ', layout2, title_color='Blue'), sg.Frame('Settings: ', layout3, title_color='Blue')],
         [sg.Frame('Save directories: ', layout5, title_color='Blue')],
         [sg.Frame('Pump settings: ', layout4a, title_color='Blue'),
          sg.Frame('Port settings: ', layout4b, title_color='Blue')],
         [sg.T(" ", size=(2, 1)), sg.Button('View', size=(8, 1)), sg.Button('Save', size=(8, 1)),
          sg.Button('Pump', size=(8, 1)), sg.Button('Finish', size=(8, 1))],
         [sg.Frame('', layout6)], [sg.Frame('', layout7)]]

layout = [[sg.Column(col_1), sg.Column(col_2)]]

# Create the Window
window = sg.Window('Vision_MT Interface', layout, font="Helvetica "+str(Screen_size), finalize=True)
window['_IMA_'].update(data=Vs.bytes_(img, m1, n1))
# ----------------------------------------------------------------------------------
time_, id_image, time_h, time_l, fluid_h, fluid_l, port_name, bauds_, c_port = 0, 0, 0, 0, 0, 0, 0, 0, -1
view_, save_, pump_, control = False, False, False, True
video, name, image, ini_time, ini_time_, path_des, type_i = None, None, None, None, None, None, None
saveIm, pumpC = None, None
# -----------------------------------------------------------------------------------

# Event Loop to process "events" and get the "values" of the inputs
while True:
    event, values = window.read(timeout=50)
    window.Refresh()
    now = datetime.now()
    now_time = now.strftime("%H : %M : %S")
    window['_TAC_'].update(now_time)

    if event == sg.WIN_CLOSED:
        break

    if event == '_VIN_':
        index = Vs.camera_idx()
        window.Element('_VIN_').update(values=index)

    if event == '_LIN_':
        window.Element('_PORT_').update(values=portsLIN)
    if event == '_SYS_':
        window.Element('_PORT_').update(values=portsWIN)

    if event == '_INF_':
        if values['_INF_'] != '':
            time_ = int(values['_INF_']) if int(values['_INF_']) > 0 else 1

    if event == '_HST_':
        if values['_HST_'] != '':
            fluid_h = int(values['_HST_']) if int(values['_HST_']) > 10 else 0
    if event == '_THS_':
        if values['_THS_'] != '':
            time_h = float(values['_THS_']) if float(values['_THS_']) > 1 else 1
    if event == '_LST_':
        if values['_LST_'] != '':
            fluid_l = int(values['_LST_']) if int(values['_LST_']) > 1 else 0
    if event == '_TLS_':
        if values['_TLS_'] != '':
            time_l = float(values['_TLS_']) if float(values['_TLS_']) > 1 else 1

    if event == '_PORT_':
        port_name = values['_PORT_']
        bauds_ = int(values['_RTE_'])
        sg.Popup('Serial Port: ', values['_PORT_'])
        c_port = Vs.serial_test(port_name, bauds_)
        text = 'CONNECT' if c_port == 1 else 'ERROR'
        window.Element('_CON_').update(text)

    if event == 'Finish':
        print('FINISH')
        window['_MES_'].update('Process finished')
        pump_, control = False, True
        if view_:
            window.find_element('View').Update(disabled=False)
            now_time = now.strftime("%H : %M : %S")
            window['_TFI_'].update(now_time)
            view_, save_ = False, False
            video.release()

    if event == 'View':
        idx = values['_VIN_']
        if view_ is False and idx != '':
            video = cv2.VideoCapture(int(idx))
            now_time1 = now.strftime("%H : %M : %S")
            window['_TIN_'].update(now_time1)
            window['_TFI_'].update('-- : -- : --')
            view_ = True
            window.find_element('View').update(disabled=True)
        elif idx == '':
            sg.Popup('Error', ['Not selected Input Video'])
        else:
            sg.Popup('Warning', ['Process is running'])

    if view_:
        ret, image = video.read()
        if ret:
            window['_IMA_'].update(data=Vs.bytes_(image, m1, n1))
            window['_MES_'].update('View video frame')

    if event == 'Save':
        print('SAVE PROCESS')
        id_image = int(values['_IDI_'])
        if values['_SYS_']:
            path_des = Vs.update_dir(values['_DES_']) + "\\"
            path_des = r'{}'.format(path_des)
        else:
            path_des = values['_DES_'] + '/'
        # -------------------------------------------------------------------
        if values['_TMI_']:
            window['_ITM_'].update('min')
        else:
            window['_ITM_'].update('sec')
        # -------------------------------------------------------------------
        if values['_IN2_']:
            type_i = ".png"
        elif values['_IN3_']:
            type_i = ".tiff"
        else:
            type_i = ".jpg"
        # ------------------------------------------------------------------
        if view_ and len(path_des) > 1 and save_ is False:
            ini_time = datetime.now()
            time_ = float(values['_INF_'])
            saveIm = Vs.SaveImages(window, id_image, ini_time)
            name = values['_NAM_']
            save_ = True
        elif view_ and len(path_des) > 1 and save_:
            sg.Popup('Warning', ['Save images is running'])
        else:
            sg.Popup('Error', ['Information or process is incorrect'])

    if save_:
        thread = threading.Thread(name="Thread-{}".format(1),
                                  target=thread_images(path_des, name, type_i, time_, values, image), args=(saveIm,))
        thread.setDaemon(True)
        thread.start()

    if event == 'Pump':
        if c_port == 1 and pump_ is False:
            fluid_h = int(values['_HST_'])
            time_h = float(values['_THS_'])
            fluid_l = int(values['_LST_'])
            time_l = float(values['_TLS_'])
            ini_time_ = datetime.now()
            pumpC = Vs.ControlPump(window, ini_time_, control, port_name, bauds_)
            pump_ = True
        elif c_port == 1 and pump_:
            sg.Popup('Warning', ['Pump control is running'])
        else:
            sg.Popup('Error', ['Port is not connected ...'])

    if pump_:
        thread = threading.Thread(name="Thread-{}".format(2),
                                  target=thread_pump(fluid_h, fluid_l, time_h, time_l), args=(pumpC,))
        thread.setDaemon(True)
        thread.start()

    # processing threads and join in main thread to next iteration
    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()


print('CLOSE WINDOW')
window.close()
