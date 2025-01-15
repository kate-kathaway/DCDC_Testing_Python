import tkinter.scrolledtext as tkscrolled
import tkinter as tk
from tkinter import filedialog
import tkinter.ttk as ttk #this is for THEMED widgets. Explicitly calls them out
from DCDCTesting import DCDC_main
import threading
from Tests import set_wait, set_skip
import os
from DebugDevelopmentFile import *
from EquipmentClasses import *
#import tk.scrolledtext as scrolledtext

'''
NOTES:

This is the main file that will be run when DC DC Testing is needed. 
It calls on DCDCTesting and passes over the starting paramters, and which tests to run


'''



window = tk.Tk(
    screenName = 'screenname',
    baseName = 'basename',
    className = 'dc-dc Power Testing' #this is the name of the window
)
window.resizable(width=False, height=False)
window.lift()
window.attributes("-topmost", True)


#Grab resource names for displau
resource_list, resource_alias_list = list_equipment()

def quit_and_close(self=None):
    window.quit()
    try:
        close_equipment()
    except Exception as e:
        pass

def update_test_selection(event):
    dut_type = device_type_var.get()
    match dut_type:
        case 'Load Switch':
            EFF_test_var.set(True)
            RIP_test_var.set(True)
            TRA_test_var.set(True)
            OVC_test_var.set(True)
            VDS_test_var.set(False)
            DEA_test_var.set(False)
            TRN_test_var.set(True)
            extfets_entry_var.set(False)
        case 'LDO':
            EFF_test_var.set(True)
            RIP_test_var.set(True)
            TRA_test_var.set(True)
            OVC_test_var.set(True)
            VDS_test_var.set(False)
            DEA_test_var.set(False)
            TRN_test_var.set(True)
            extfets_entry_var.set(False)
        case 'Converter':
            #Jitter is set in the device class
            EFF_test_var.set(True)
            RIP_test_var.set(True)
            TRA_test_var.set(True)
            OVC_test_var.set(True)
            VDS_test_var.set(True)
            DEA_test_var.set(False)
            TRN_test_var.set(True)
            extfets_entry_var.set(False)
        case 'External Fet Converter':
            #Jitter is set in the device class
            EFF_test_var.set(True)
            RIP_test_var.set(True)
            TRA_test_var.set(True)
            OVC_test_var.set(True)
            VDS_test_var.set(True)
            DEA_test_var.set(True)
            TRN_test_var.set(True)
            extfets_entry_var.set(True)
        case '':
            EFF_test_var.set(False)
            RIP_test_var.set(False)
            TRA_test_var.set(False)
            OVC_test_var.set(False)
            VDS_test_var.set(False)
            DEA_test_var.set(False)
            TRN_test_var.set(False)
            extfets_entry_var.set(False)


def debug_screenshot():
    debug_filename = filename_entry_var.get()
    debugscope_connection_ID = resource_list[debug_scope_equip_cbox.current()]
    try:
        debugscope_screenshot(debugscope_connection_ID, debug_filename)
    except Exception as e:
        print(e)
        pass


#Function to read all variables as input to main testing function (?)
def get_variables():
    """
    
    Grabs all variables from the user-input GUI
        
    """
    try:

        popup_label.config(background = 'white')
        start_test_button.config(state = 'disabled')


        device = DUT()

        
        device.dut_type = device_type_var.get()
        #['Load Switch', 'LDO', 'Converter', 'External Fet Converter']

        #Eff, RippleJitter, Transient, Overcurrent, VDS, Deadtime, Turnon-off

        

        device.test_list.append(EFF_test_var.get())
        device.test_list.append(RIP_test_var.get())
        device.test_list.append(TRA_test_var.get())
        device.test_list.append(OVC_test_var.get())
        device.test_list.append(VDS_test_var.get())
        device.test_list.append(DEA_test_var.get())
        device.test_list.append(TRN_test_var.get())



        if True in device.test_list:
            pass
        else:
            raise Exception('No Test Selected')
        

        #Gives index list position. Perfect. If not chosen, returns -1

       
        if -1 in [scope_equip_cbox.current(), supply_equip_cbox.current(), load_equip_cbox.current()]:
            raise Exception('Equipment not selected')
        
        scope_connection_ID = resource_list[scope_equip_cbox.current()]

        supply_connection_ID = resource_list[supply_equip_cbox.current()]
     
        load_connection_ID = resource_list[load_equip_cbox.current()]


        #print (resource_list[scope_pos], resource_list[supply_pos], resource_list[load_pos])

        min_load_bool = min_load_var.get()
        tdc_load_bool = tdc_load_var.get()
        max_load_bool = max_load_var.get()
        transient_load_bool = transient_load_var.get()

        current_testing_list_bool = [min_load_bool, tdc_load_bool, max_load_bool, transient_load_bool]

        

        if True in current_testing_list_bool:
            pass
        else:
             raise Exception('No load points selected')
        

        for index, value in enumerate(current_testing_list_bool):
            if value and index == 0:
                device.load_list.append('min')
            elif value and index == 1:
                device.load_list.append('tdc')
            elif value and index == 2:
                device.load_list.append('max')
            elif value and index == 3:
                device.load_list.append('transient')
            else:
                continue

        device.name = name_entry_var.get()

        if len(device.name) == 0:
            raise Exception('Device name missing')


        device.extfets = extfets_entry_var.get()


        device.device_input_voltage = voltage_input_entry_var.get()
        device.supply_input_voltage = voltage_supply_entry_var.get()


        device.output_voltage_max = round(voltage_out_nom_entry_var.get() * 1.05,3)
        device.output_voltage_nom = voltage_out_nom_entry_var.get()
        device.output_current_max = iout_max_entry_var.get()
        device.output_current_nom = iout_nom_entry_var.get()
        fsw_khrts = freq_khrts_entry_var.get()

        device.frequency = float(fsw_khrts*1000)

        if device.frequency >0:
            device.jitter_bool = True


        for entry_var in [device.device_input_voltage, device.supply_input_voltage, device.output_voltage_max, device.output_voltage_nom, device.output_current_max, device.output_current_nom]:
            if entry_var <= float(0):
                raise Exception('Entry field unfilled or negative')


        if device.test_list[1]:
            device.frequency = float(100000)


        '''
        if device.test_list[1]:
            rip_test_label.config(background = 'white')
            if transient_load_bool:
                tra_test_label.config(background = 'white')
            ovc_test_label.config(background = 'white')

        if device.test_list[2]:
            rip_test_label.config(background = 'white')
            jit_test_label.config(background = 'white')
            if transient_load_bool:
                tra_test_label.config(background = 'white')
            ovc_test_label.config(background = 'white')
            vds_test_label.config(background = 'white')
        if device.test_list[0]:
            eff_test_label.config(background = 'white')
        if device.test_list[3]:
            dea_test_label.config(background = 'white')
        if device.test_list[4]:
            trn_test_label.config(background = 'white')

        '''

        device.user_folder_location = file_entry_var.get()

        testing_thread = threading.Thread(target=DCDC_main, args = [window, error_log, start_test_button, popup_label, popup_button1, popup_button2, testing_progressbar, scope_connection_ID, supply_connection_ID, load_connection_ID, device], daemon=True)
        testing_thread.start()



    except Exception as e:
        popup_label.config(text = f'Whoops! Error: \n {e}')
        start_test_button.config(state = 'enabled')
        popup_label.config(background = 'red')
   

    
    



#Making two tabs
tabControl = ttk.Notebook(window)

tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)

tabControl.add(tab1, text='Main')
tabControl.add(tab2, text='Debugging & Other Features')

tabControl.pack(expand=1, fill="both")




#Title
title_label = ttk.Label(tab1, text = 'Onlogic DCDC Power Testing')
title_label.grid(column = 0, row = 0, columnspan = 2)



tests_frame = ttk.Frame(tab1, relief = "ridge", borderwidth = 2)
tests_frame.grid(column = 0, row = 1, columnspan = 1)

tests_label = ttk.Label(tests_frame, text = 'High-Level Tests to Execute')
tests_label.grid(column = 0, row = 0, columnspan = 2)


#Start and quit buttons
start_test_button = ttk.Button(tests_frame, text="Start", command = get_variables )
start_test_button.grid(column = 0, row = 1)
quit_test_button = ttk.Button(tests_frame, text="Quit", command = quit_and_close)
quit_test_button.grid(column = 1, row = 1)


#Test choosing
EFF_test_var = tk.BooleanVar(tests_frame, value = False)
EFF_test_button = ttk.Checkbutton(tests_frame, text="Efficiency", variable = EFF_test_var, offvalue = False, onvalue = True)
EFF_test_button.grid(column = 1, row = 2)

RIP_test_var = tk.BooleanVar(tests_frame, value = False)
RIP_test_button = ttk.Checkbutton(tests_frame, text="Ripple&Jitter", variable = RIP_test_var, offvalue = False, onvalue = True)
RIP_test_button.grid(column = 1, row = 3)

TRA_test_var = tk.BooleanVar(tests_frame, value = False)
TRA_test_button = ttk.Checkbutton(tests_frame, text="Transient", variable = TRA_test_var, offvalue = False, onvalue = True)
TRA_test_button.grid(column = 1, row = 4)

OVC_test_var = tk.BooleanVar(tests_frame, value = False)
OVC_test_button = ttk.Checkbutton(tests_frame, text="OverCurrent", variable = OVC_test_var, offvalue = False, onvalue = True)
OVC_test_button.grid(column = 1, row = 5)

VDS_test_var = tk.BooleanVar(tests_frame, value = False)
VDS_test_button = ttk.Checkbutton(tests_frame, text="Fet VDS Stress", variable = VDS_test_var, offvalue = False, onvalue = True)
VDS_test_button.grid(column = 1, row = 6)

DEA_test_var = tk.BooleanVar(tests_frame, value = False)
DEA_test_button = ttk.Checkbutton(tests_frame, text="Deadtime", variable = DEA_test_var, offvalue = False, onvalue = True)
DEA_test_button.grid(column = 1, row = 7)

TRN_test_var = tk.BooleanVar(tests_frame, value = False)
TRN_test_button = ttk.Checkbutton(tests_frame, text="Turn-On/Off", variable = TRN_test_var, offvalue = False, onvalue = True)
TRN_test_button.grid(column = 1, row = 8)




device_type_list = ['Load Switch','LDO','Converter','External Fet Converter']
device_type_var = tk.StringVar()
device_type_cbox = ttk.Combobox(tests_frame, textvariable = device_type_var, values = device_type_list, state = 'readonly')
device_type_cbox.grid(column = 0, row = 2, pady = 15)

device_type_cbox.bind('<<ComboboxSelected>>', update_test_selection)




extfets_label = ttk.Label(tests_frame, text = 'External Fets?')
extfets_label.grid(column = 0, row = 3)
extfets_entry_var = tk.BooleanVar(tests_frame, value = False)
extfets_entry = ttk.Checkbutton(tests_frame, variable = extfets_entry_var, offvalue = False, onvalue = True)
extfets_entry.grid(column = 0, row = 4)






config_frame = tk.Frame(tab2, borderwidth = 2, relief = 'ridge')
config_frame.grid(column = 0, row = 0, columnspan = 2)


newequip_label = ttk.Label(config_frame, text = 'If having instrument issues press "New Instrument"\n Button, then send "NewInstrumentConfig.txt" to Kate H', justify = 'left')
newequip_label.grid(column = 0, row = 3, sticky = 'w')

direct_button = ttk.Button(config_frame, text="New Instrument", command = debug_config)
direct_button.grid(column = 1, row = 3)

initial_direct = os.getcwd()

def get_newdirect():
    selected_direct = filedialog.askdirectory(initialdir = initial_direct)

    if selected_direct:
        direct_var.set(selected_direct)
        os.chdir(selected_direct)

direct_label = ttk.Label(config_frame, text = 'Please ensure directory matches python folder:')
direct_label.grid(column = 0, row = 0, columnspan = 2)

direct_var = tk.StringVar(value = initial_direct)
direct_entry = ttk.Entry(config_frame, textvariable = direct_var, state = 'readonly', width = 65)
direct_entry.grid(column = 0, row = 1, columnspan = 2, sticky = 'nsew')

direct_button = ttk.Button(config_frame, text="...", command = get_newdirect, width = 5)
direct_button.grid(column = 1, row = 1, sticky = 'e')


debug_scope_equip_label = ttk.Label(config_frame, text = 'Debug Oscilloscope')
debug_scope_equip_label.grid(column = 0, row = 4, columnspan = 1)
scope_equip_var = tk.StringVar()
debug_scope_equip_cbox = ttk.Combobox(config_frame, textvariable = scope_equip_var, values = resource_alias_list, state = 'readonly')
debug_scope_equip_cbox.grid(column = 0, row = 5, columnspan = 1)

#debug_supply_equip_label = ttk.Label(config_frame, text = 'Debug Supply')
#debug_supply_equip_label.grid(column = 0, row = 6, columnspan = 1)
#supply_equip_var = tk.StringVar()
#debug_supply_equip_cbox = ttk.Combobox(config_frame, textvariable = supply_equip_var, values = resource_alias_list, state = 'readonly')
#debug_supply_equip_cbox.grid(column = 0, row = 7, columnspan = 1)

#debug_load_equip_label = ttk.Label(config_frame, text = 'Debug Load')
#debug_load_equip_label.grid(column = 0, row = 8, columnspan = 1)
#load_equip_var = tk.StringVar()
#debug_load_equip_cbox = ttk.Combobox(config_frame, textvariable = load_equip_var, values = resource_alias_list, state = 'readonly')
#debug_load_equip_cbox.grid(column = 0, row = 9, columnspan = 1)

debug_screenshot_button = ttk.Button(config_frame, text="Screenshot", command = debug_screenshot)
debug_screenshot_button.grid(column = 1, row =6, columnspan = 1)

filename_label = ttk.Label(config_frame, text = 'Screenshot File Name:')
filename_label.grid(column = 1, row = 4, columnspan = 1)
filename_entry_var = tk.StringVar()
filename_entry = ttk.Entry(config_frame, textvariable = filename_entry_var)
filename_entry.grid(column = 1, row = 5, columnspan = 1)

filename_entry_var.set('DefaultScreenshot')


run_testprog_button = ttk.Button(config_frame, text="Run TestScript Function In DebugDevolopmentFile", command = TestScript)
run_testprog_button.grid(column = 0, row = 6, columnspan = 1)


error_log = tkscrolled.ScrolledText(config_frame, height = 10, width = 50)
error_log.grid(column = 0, row = 7, columnspan = 2)
error_log.indexnum = 0.0




#Instrument picking
instrument_frame = tk.Frame(tab1, borderwidth = 2)
instrument_frame.grid(column = 1, row = 2, columnspan = 1)

instrument_label = ttk.Label(instrument_frame, text = 'Hardware Selection')
instrument_label.grid(column = 0, row = 0, columnspan = 2)

scope_equip_label = ttk.Label(instrument_frame, text = 'Oscilloscope')
scope_equip_label.grid(column = 0, row = 1, columnspan = 2)
# Scope var is shared with debug menu
scope_equip_cbox = ttk.Combobox(instrument_frame, textvariable = scope_equip_var, values = resource_alias_list, state = 'readonly')
scope_equip_cbox.grid(column = 0, row = 2, columnspan = 2)

supply_equip_label = ttk.Label(instrument_frame, text = 'Power Supply')
supply_equip_label.grid(column = 0, row = 3, columnspan = 2)
supply_equip_var = tk.StringVar()
supply_equip_cbox = ttk.Combobox(instrument_frame, textvariable = supply_equip_var, values = resource_alias_list, state = 'readonly')
supply_equip_cbox.grid(column = 0, row = 4, columnspan = 2)

load_equip_label = ttk.Label(instrument_frame, text = 'DC Load')
load_equip_label.grid(column = 0, row = 5, columnspan = 2)
load_equip_var = tk.StringVar()
load_equip_cbox = ttk.Combobox(instrument_frame, textvariable = load_equip_var, values = resource_alias_list, state = 'readonly')
load_equip_cbox.grid(column = 0, row = 6, columnspan = 2)









#Device testing parameters
device_frame = ttk.Frame(tab1, borderwidth = 2)
device_frame.grid(column = 1, row = 1, columnspan = 1)
device_label = ttk.Label(device_frame, text = 'Device Parameters')
device_label.grid(column = 0, row = 8, columnspan = 2)




name_label = ttk.Label(device_frame, text = 'Device Name')
name_label.grid(column = 0, row = 9)
name_entry_var = tk.StringVar()
name_entry = ttk.Entry(device_frame, textvariable = name_entry_var)
name_entry.grid(column = 0, row = 10)


voltage_input_label = ttk.Label(device_frame, text = 'DUT VIN')
voltage_input_label.grid(column = 0, row = 11)
voltage_input_entry_var = tk.DoubleVar()
voltage_input_entry = ttk.Spinbox(device_frame, textvariable = voltage_input_entry_var, from_= 0.0, to = 100.0, width = 10)
voltage_input_entry.grid(column = 0, row = 12)



voltage_supply_label = ttk.Label(device_frame, text = 'Supply VIN')
voltage_supply_label.grid(column = 1, row = 11)
voltage_supply_entry_var = tk.DoubleVar()
voltage_supply_entry = ttk.Spinbox(device_frame, textvariable = voltage_supply_entry_var, from_= 0.0, to = 100.0, width = 10)
voltage_supply_entry.grid(column = 1, row = 12)

voltage_out_nom_label = ttk.Label(device_frame, text = 'V-Out Nom')
voltage_out_nom_label.grid(column = 0, row = 13)
voltage_out_nom_entry_var = tk.DoubleVar()
voltage_out_nom_entry = ttk.Spinbox(device_frame, textvariable = voltage_out_nom_entry_var, from_= 0.0, to = 100.0, width = 10)
voltage_out_nom_entry.grid(column = 0, row = 14)

freq_khrts_label = ttk.Label(device_frame, text = 'Switching Freq (kHz)')
freq_khrts_label.grid(column = 1, row = 13)
freq_khrts_entry_var = tk.IntVar()
freq_khrts_entry = ttk.Spinbox(device_frame, textvariable = freq_khrts_entry_var, from_= 0.0, to = 100.0, width = 10)
freq_khrts_entry.grid(column = 1, row = 14)

iout_max_label = ttk.Label(device_frame, text = 'IOut Max')
iout_max_label.grid(column = 0, row = 15)
iout_max_entry_var = tk.DoubleVar()
iout_max_entry = ttk.Spinbox(device_frame, textvariable = iout_max_entry_var, from_= 0.0, to = 100.0, width = 10)
iout_max_entry.grid(column = 0, row = 16)

iout_nom_label = ttk.Label(device_frame, text = 'IOut TDC')
iout_nom_label.grid(column = 1, row = 15)
iout_nom_entry_var = tk.DoubleVar()
iout_nom_entry = ttk.Spinbox(device_frame, textvariable = iout_nom_entry_var, from_= 0.0, to = 100.0, width = 10)
iout_nom_entry.grid(column = 1, row = 16)


#folder_direct = os.getcwd()

file_label = ttk.Label(device_frame, text = 'Folder Location')
file_label.grid(column = 0, row = 17, columnspan = 2)
file_entry_var = tk.StringVar()
file_entry_var.set(os.getcwd())
file_entry = ttk.Entry(device_frame, textvariable = file_entry_var, state = 'readonly', width = 35)
file_entry.grid(column = 0, row = 18, columnspan = 2, sticky = 'nsw')



def new_folder_location():
    selected_direct = filedialog.askdirectory(initialdir = file_entry_var.get())

    if selected_direct:
        file_entry_var.set(selected_direct)

folder_button = ttk.Button(device_frame, text="...", width = 2, command = new_folder_location)
folder_button.grid(column = 1, row = 18, columnspan = 1, sticky = 'e')



#Load Points selection
loadpoints_frame = ttk.Frame(tab1)
loadpoints_frame.grid(column = 0, row = 2, columnspan = 1)

loadpoints_label = ttk.Label(loadpoints_frame, text = 'Current Points to Test', padding=(0,20,5,0))
loadpoints_label.grid(column = 0, row = 17, columnspan = 2)

min_load_label = ttk.Label(loadpoints_frame, text = 'Min Load')
min_load_label.grid(column = 0, row = 18)
min_load_var = tk.BooleanVar(loadpoints_frame, value = True)
min_load_button = ttk.Checkbutton(loadpoints_frame, variable = min_load_var, offvalue = False, onvalue = True)
min_load_button.grid(column = 0, row = 19)

tdc_load_label = ttk.Label(loadpoints_frame, text = 'TDC Load')
tdc_load_label.grid(column = 1, row = 18)
tdc_load_var = tk.BooleanVar(loadpoints_frame, value = True)
tdc_load_button = ttk.Checkbutton(loadpoints_frame, variable = tdc_load_var, offvalue = False, onvalue = True)
tdc_load_button.grid(column = 1, row = 19)

max_load_label = ttk.Label(loadpoints_frame, text = 'Max Load')
max_load_label.grid(column = 0, row = 20)
max_load_var = tk.BooleanVar(loadpoints_frame, value = True)
max_load_button = ttk.Checkbutton(loadpoints_frame, variable = max_load_var, offvalue = False, onvalue = True)
max_load_button.grid(column = 0, row = 21)

transient_load_label = ttk.Label(loadpoints_frame, text = 'Transient Load')
transient_load_label.grid(column = 1, row = 20)
transient_load_var = tk.BooleanVar(loadpoints_frame, value = True)
transient_load_button = ttk.Checkbutton(loadpoints_frame, variable = transient_load_var, offvalue = False, onvalue = True)
transient_load_button.grid(column = 1, row = 21)







#Testing interface
testing_frame = tk.Frame(tab1, borderwidth = 2)
testing_frame.grid(column = 0, row = 10, columnspan = 2)


testing_progressbar = ttk.Progressbar(testing_frame, name = 'progressbar')
testing_progressbar.grid(column = 0, row = 11, columnspan = 2)


popup_label = ttk.Label(testing_frame, text = f'User Input / Current Progress \n will display here', padding=(5,5,5,5))
popup_label.grid(column = 0, row = 13, columnspan=2)

#global popup_button1
popup_button1 = ttk.Button(testing_frame, text = "Continue", state = 'disabled', command = set_wait)
popup_button1.grid(column = 0, row = 12)

popup_button2 = ttk.Button(testing_frame, text = "Skip", state = 'disabled', command = set_skip)
popup_button2.grid(column = 1, row = 12)



window.bind('<Escape>', quit_and_close)

#window.bind('<Enter>', set_wait)



window.mainloop()
