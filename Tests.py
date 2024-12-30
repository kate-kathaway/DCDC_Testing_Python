from datetime import datetime
#from EquipmentClasses import *
from EquipmentClasses import *
import os
import csv
import time
import tkinter as tk
import tkinter.ttk as ttk #this is for THEMED widgets. Explicitly calls them out



wait_var = False
skip_var = False

def get_wait():
    global wait_var
    return wait_var

def set_wait(value=False):
    global wait_var
    wait_var = value

def get_skip():
    global skip_var
    return skip_var

def set_skip(value=False):
    global skip_var
    skip_var = value

def listener(popup_button1, popup_button2, popup_button2_state:str, popup_label, test_text:str, testing_progressbar):
    listen_val = get_wait()
    listen_skip = get_skip()
    popup_label.config(text = test_text)
    popup_label.config(background = '#FFFACD') #Turn background yellow
    popup_button1.config(state = 'enabled')
    popup_button2.config(state = popup_button2_state)
    testing_progressbar.stop()
    testing_progressbar.config(mode = 'determinate')

    if listen_skip:
        while listen_skip and listen_val:
            listen_val = get_wait()
            listen_skip = get_skip()
            time.sleep(0.5)
    else:
        while listen_val:
            listen_val = get_wait()
            time.sleep(0.5)

    popup_button1.config(state = 'disabled')
    popup_button2.config(state = 'disabled')
    testing_progressbar.config(mode = 'indeterminate')
    testing_progressbar.start()
    popup_label.config(background = 'white')
    set_wait()
  



'''
NOTES:

This file holds individual high-level functions and tests. 


create_folder: creates the testing folder that houses all testing results

copy_csv: Copies any csv file given the path and file name. Places into the folder made by create_folder

write_to_csv: Writes to any CSV. It does so by copying and replacing the info on the given linenum variable, then clearing the old unedited file


Tests: All tests are accoridng to the "DC-DC testing instructions (Non-LabVIEW)". Bode plots excluded



'''


def create_folder(input_voltage:float, device_under_test:str):
    """
    
    Creates and names the folder for all results of the test in the current code directory

    Parameters:
        input_voltage (float): Device input voltage
        device_under_test (str): Name of the device being tested, names the folder for seperating results

    """
    now = datetime.now()
    date_time_str = now.strftime(r'%Y-%m-%d--%H-%M-%S')

    global results_folder_name
    results_folder_name = f'{input_voltage}V-{device_under_test}-DCDCTesting_{date_time_str}'

    global python_path
    python_path = os.getcwd()
    print(python_path)
    folder_name_path = f'{python_path}\\{results_folder_name}'
    os.makedirs(folder_name_path)

    return folder_name_path, python_path


def copy_csv(python_path:str,folder_name_path:str,filename:str):
    """
    
    Copys a CSV in the current python code path, then places it in the indiicated file location

    Parameters:
        python_path (str): Current path of python code
        folder_name_path (str): Path for the testing results folder
        filename (str): Name of the CSV file to be copied

    """
    with open(f'{python_path}\\{filename}.csv', newline='') as inf, open(f'{folder_name_path}\\{filename}.csv','w', newline='') as outf:

        #Opens the reults CSV to be read. Opens a temnorary csv file to overwrite
        reader = csv.reader(inf, delimiter=',', quotechar='|')
        writer = csv.writer(outf)

        count = 0
        for line in reader:
            #Linenum -1 for indexing. If i enter "Row 1" for the sheet, it will index row 0 on the csv. Easier on front end
            writer.writerow(line)

        inf.close()
        outf.close()


def write_to_csv(folder_name_path:str, linenum:int, information, filename:str):
    """
    
    Writes information to a specified line in a CSV. Does so by copying and replacing the whole file. Will not retain metadata

    Parameters:
        folder_name_path (str): Path for the testing results folder
        linaenum (int): The linenumber in the CSV to be writteb over
        information (list): A list of strings of the information to write to CSV
        filename (str): Name of the CSV file to be copied

    """

    with open(f'{folder_name_path}\\{filename}.csv', newline='') as inf, open(f'{folder_name_path}\\{filename}_temp.csv','w', newline='') as outf:

        #Opens the reults CSV to be read. Opens a temnorary csv file to overwrite
        reader = csv.reader(inf, delimiter=',', quotechar='|')
        writer = csv.writer(outf)

        count = 0
        for line in reader:
            #Linenum -1 for indexing. If i enter "Row 1" for the sheet, it will index row 0 on the csv. Easier on front end
            if count == (linenum-1):
                writer.writerow(information)
            else:
                writer.writerow(line)
            count = count + 1

        inf.close()
        outf.close()

        os.remove(f'{folder_name_path}\\{filename}.csv')
        os.rename(f'{folder_name_path}\\{filename}_temp.csv', f'{folder_name_path}\\{filename}.csv')



def test_eff(popup_label, popup_button1, popup_button2, testing_progressbar, scope:SCOPE, supply:SUPPLY, load:LOAD, device:DUT):
    """
    
    Efficiency test as defined in DC DC testing manual

    Parameters:
        Load_ID (str): MFG name of load
        Supply_ID (str): MFG name of supply
        max_current (float): The maximum current of the DUT
        tdc_current (float): Nominal current of the DUT during normal operation

    """

    def eff_main():
        popup_label.config(text = 'Running Efficiency Test....')

        efficiency_results = []

        load.mode('CC','H')
        #load.autoCCMode(device)
        load.staticCurrent('0')
        supply.output(True)
        load.output(True)

        scope.recall(1)
        #scope.autoSetup()
        scope.setTrigger('C1','POS', device.output_voltage_nom)
        scope.setupChannelPercent('C1', device.output_voltage_nom , 2)
        scope.setupChannelPercent('C2', device.device_input_voltage, 2)

        first_loop = True
        for linspace in range(0,25):

            meas_result = []

            scope.clearSweeps()

            current_set = round(float(linspace*(device.output_current_nom/24)),3)
            
            load.staticCurrent(current_set)
            time.sleep(0.3)
            scope.trigMode('SINGLE')
            scope.waitUntilTrig(5)
            scope.STOP()

            meas_result.append(current_set)
            meas_result.append(scope.meas('P1','out'))
            meas_result.append(scope.meas('P5','out'))
            meas_result.append(supply.meas('CURR'))
        
            efficiency_results.append(meas_result)

            if first_loop:
                for repeat in range(18):
                    efficiency_results.append([])
                first_loop = False


        for defined_point in [device.output_current_nom,device.output_current_max]:
            meas_result = []

            scope.clearSweeps()

            meas_result.append(defined_point)
            load.staticCurrent(defined_point)
            time.sleep(0.4)
            scope.trigMode('SINGLE')
            time.sleep(0.4)
            scope.STOP()

            meas_result.append(scope.meas('P1','out'))
            meas_result.append(scope.meas('P5','out'))
            meas_result.append(supply.meas('CURR'))

            efficiency_results.append(meas_result)

        discharge(device)

        with open(f'{python_path}\\{results_folder_name}\\efficiency.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(efficiency_results)
            csvfile.close()
        testing_progressbar.config(mode = 'determinate')
        

    set_wait(True)
    test_text = 'Efficiency Test Setup: \n Channel 1: Output Voltage \n Channel 2: Input Voltage \n Channel 3: Load Current (BNC) \n Channel 4: Low-Side Mosfet (Differential) \n Setup Complete?'
    listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
    eff_main()





def test_ripple_jitter(popup_label, popup_button1, popup_button2, testing_progressbar, scope:SCOPE, supply:SUPPLY, load:LOAD, device:DUT):

    """
    
    Executes ripple and jitter test as defined in DC DC testing manual. Jitter test can be skipped

    Parameters:
        Scope_ID (str): MFG name of scope
        Supply_ID (str): MFG name of supply
        Load_ID (str): MFG name of load
        fsw (float): Switching frequency of DUT
        tdc_current (float): Nominal current of the DUT during normal operation
        max_current (float): The maximum current of the DUT
        filepath (str): Path for the testing results folder
        current_testing (list): A list of strings. Contains current operating points to test for
        input_voltage (float): Input voltage for the DUT
        jitter_bol(bool): True if the jitter test should be performed, false if not
        

    """

    '''
    Steps: 
    1. Recall setup 1
    2. Set power supply voltage and current (Already done)
    3. Adjust horizontal scale to show 10 cycles of channel 4 (derive using entered switching freq number)
    4. Set scope to fixed sample rate of >250M/S
    5. Adjust offsets of all 4 channels (should be done from autosetup. If not, whatever)
    6. Set trigger to channel 4, at mid of vertical range (half the input voltage)

    7. DC load OFF. Capture 100 cycles. 
    8. Turn off traces 2 and 4. Capture a screenshot
    9, Record max, min, mean of C1 (Using P1, P2, P3. Want max max, min min, mean mean)
    10. Turn on CH2, turn off CH1. Capture sceenshot

    11. Record highest max, and minimum min (use the P4 and P5 channels)

    12. Turn off CH1 and CH2, Turn on CH 4. turn on persist
    13. Clear previous sweeps, then sweep until CH4 cycled are >2k
    14. Capture screenshot. 
    15. Copy freq measurements, Min max and mean. Then std dev, min, max, stdev (no mean)


    16. Repeat steps 7-15 at TDC current
    17. Repeat steps 7-15 at max current
    '''

    def ripple_jitter_main():
        popup_label.config(text = 'Running Ripple Test.... \n Step: Setup')

        load.mode('CC','H')
        current_count = 0
        current_point = 0.0

        current_list = device.makeLoadPointList('transient')

        scope.recall(1)
        #scope.autoSetup()
        scope.horScale(float(1/device.frequency))
        scope.sampleRate()
        scope.setTrigger('C4','POS',float(device.device_input_voltage/2))

        scope.traceToggle('C1', True)
        scope.traceToggle('C2', True)
        scope.traceToggle('C3', True)
        scope.traceToggle('C4', True)

        scope.setupChannelPercent('C1',device.output_voltage_nom,5)
        scope.setupChannelPercent('C2',device.device_input_voltage,5)
        scope.setupChannel('C4', device.device_input_voltage, 0.0)

        for current in current_list:
            popup_label.config(text = f'Running Ripple Test.... \n Step: {current} Load')
            load.output(False)
            supply.output(True)
            current_point = float(0)
            

            if current == 'tdc':
                current_point = device.output_current_nom
                load.staticCurrent(current_point)
                load.output(True)
                current_count = 1
            elif current == 'max':
                current_point = device.output_current_max
                load.staticCurrent(current_point)
                load.output(True)
                current_count = 2

            scope.setupChannelPercent('C3',current_point,30)

            scope.captureWaveforms('P1', 100, f'Running Ripple Test.... \n Step: {current} Load' , popup_label)

            scope.traceToggle('C2', False)
            scope.traceToggle('C4', False)
            

            filename = f'01_Vout_{current}'
            scope.screenshot(device.folder_name_path,filename)

            scope.meas('P1','min')

            p1_min = scope.meas('P1','min')
            p2_mean = scope.meas('P1','mean')
            p3_max = scope.meas('P3','max')

            #write_to_csv(filepath, current_count+3, [f'{p1_min}',f'{p2_mean}', f'{p3_max}', f'{filepath}\\{filename}.png'],'Results')
            write_to_csv(device.folder_name_path, current_count+3, [f'{p3_max}',f'{p2_mean}', f'{p1_min}', f'{device.folder_name_path}\\{filename}.png'],'Results') #Swapped order

            scope.traceToggle('C2', True)
            scope.traceToggle('C1', False)

            filename = f'04_Vin_{current}'
            scope.screenshot(device.folder_name_path,filename)
            p4_min = scope.meas('P4','min')
            p5_max = scope.meas('P5','max')

            write_to_csv(device.folder_name_path, current_count+8, [f'{p5_max}',f'{p4_min}', f'{device.folder_name_path}\\{filename}.png'],'Results')


            if device.jitter_bool:
                popup_label.config(text = f'Running Jitter Test.... \n Step: {current} Load')

                scope.traceToggle('C1', False)
                scope.traceToggle('C2', False)
                scope.traceToggle('C4', True)
 
                scope.persist(True)

                scope.setParam('P5','C3','MAX') #Changed from TOP to MAX. Seems like it makes way more sense
                #scope.setParam('P5','C3','TOP')

                scope.captureWaveforms('P6', 2000, f'Running Jitter Test.... \n Step: {current} Load', popup_label )
                filename = f'08_Jitter_{current}'


                scope.screenshot(device.folder_name_path,filename)
                p6_min = scope.meas('P6','min')
                p6_mean = scope.meas('P6','mean')
                p6_max = scope.meas('P6','max')
                p5_min = scope.meas('P5','min')
                p5_max = scope.meas('P5','max')
                p5_stdev = scope.meas('P5','sdev')

                write_to_csv(device.folder_name_path, current_count+14, [f'{p6_min}',f'{p6_mean}', f'{p6_max}',f'{p5_min}', f'{p5_max}', f'{p5_stdev}',f'{device.folder_name_path}\\{filename}.png'],'Results')

                scope.persist(False)
   

            scope.traceToggle('C1', True)
            scope.traceToggle('C2', True)
            scope.traceToggle('C3', True)
            scope.traceToggle('C4', True)
        discharge(device)



        

    set_wait(True)
    test_text = 'Ripple & Jitter Test Setup: \n Channel 1: Output Voltage \n Channel 2: Input Voltage \n Channel 3: Load Current (BNC) \n Channel 4: Low-Side Mosfet (Differential) \n Setup Complete?'
    listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
    ripple_jitter_main()




def test_transient(popup_label, popup_button1, popup_button2, testing_progressbar, scope, supply, load, device):
    """
    
    Executes transient test as defined in DC DC testing manual

    Parameters:
        Scope_ID (str): MFG name of scope
        Supply_ID (str): MFG name of supply
        Load_ID (str): MFG name of load
        tdc_current (float): Nominal current of the DUT during normal operation
        max_current (float): The maximum current of the DUT
        filepath (str): Path for the testing results folder

    """
     
    '''
    Steps: 
    1. Recall setup 1
    2. Set load CCD
    3. First test from 0% to 50% load
    4. Set slew rate to HIGH
    5. Set repeat to 0 (indefinite) 
    5.5(whoops) Set T1 and T2 to 5ms for 100Hz
    6. Turn off channel 2 & 4
    7. Turn on load
    8. Adjust horizontal scale to 5ms/div
    9. Set memeory maximum to 500KS (?)
    10. Adjust vertical scale of voltage and current channels
    11. Set scope trigger to CH3, at half transient level 
    12. Aquire 100 samples. Capture screenshot
    13. Record max max, mean mean, and min min for CH1
    14. Repeat Steps 3-13 for 50%-100% load. 
    15. Repeat steps 3-14 at 1kHz. t1&T2=0.5ms. Horizontal scale = 500us/div
    16. Repeat steps 3-14 at 10kHz. t1&t2=0.05ms. Hoz scale = 50us/div
    17. Turn off channel 2, turn on channel 1
    18. From 0A to TDC, test at 1kHz. Capture screenshot and record max max and min min
    '''

    

    def transient_main():

        #Set up scaling
        load(Load_ID, 'MODE', 'CCH')
        load(Load_ID, 'OUT', 'OFF')
        load(Load_ID,'CURR',f'{tdc_current}')
        supply(Supply_ID,'OUT','ON')
        time.sleep(0.5)
        load(Load_ID, 'OUT', 'ON')

        #time.sleep(0.2)

        scope(Scope_ID,'RECALL','1')
        scope(Scope_ID,'AUTOSETUP')
        time.sleep(0.5)
        supply(Supply_ID,'OUT','OFF')
        load(Load_ID, 'OUT', 'OFF')
        scope_chan(Scope_ID,'C3','TRIGCHANNEL','POS')
        scope_chan(Scope_ID,'C3','ATTEN','6.03')

        scope_chan(Scope_ID,'C1','BANDWIDTH','20MHz')
        scope_chan(Scope_ID,'C2','BANDWIDTH','20MHz')

        scope_chan(Scope_ID,'C2','TRACETOGGLE','OFF')
        scope_chan(Scope_ID,'C4','TRACETOGGLE','OFF')
        load(Load_ID, 'MODE', 'CCDH')

        time_array = ['5ms','0.5ms','0.05ms']
        hertz_array = ['100','1k','10k']

        count = 0
        
        for tscale in time_array:
            popup_label.config(text = f'Running Transient Test... \n Step: {hertz_array[count]}Hz 0-50% ')

            load(Load_ID, 'L1', '0')
            load(Load_ID, 'L2', f'{max_current/2}')
            load(Load_ID, 'T1', f'{tscale}')
            load(Load_ID, 'T2', f'{tscale}')
            load(Load_ID, 'RISE', 'MAX')
            load(Load_ID, 'FALL', 'MAX')
            load(Load_ID, 'REPEAT', '0')
            
        
            supply(Supply_ID,'OUT','ON')
            load(Load_ID, 'OUT', 'ON')
            time.sleep(0.5)
            scope(Scope_ID,'AUTOSETUP')
            scope(Scope_ID,'TDIV',f'{tscale}')
            scope_chan(Scope_ID,'C3','TRIGCHANNEL','POS')
            scope_chan(Scope_ID,'C3','ATTEN','6.03')
            scope_chan(Scope_ID,'C3','TRIGLEVEL', float(max_current/4)) 
            scope_chan(Scope_ID,'C3','VOFFSET',f'-{float(max_current/4)}')


            capture_waveforms(Scope_ID,'P1', 100, f'Running Transient Test... \n Step: {hertz_array[count]}Hz 0-50% ', popup_label)
            filename = f'Trans_vo_0_50_{hertz_array[count]}Hz'
            scope_screenshot(filepath,filename)


            p1_min = float(scope_chan(Scope_ID,'P1','MEAS','min'))
            p2_mean = float(scope_chan(Scope_ID,'P2','MEAS','mean'))
            p3_max = float(scope_chan(Scope_ID,'P3','MEAS','max'))

            #write_to_csv(filepath, count + 19, [f'{p1_min}',f'{p2_mean}', f'{p3_max}', f'{filepath}\\{filename}.png'],'Results')
            write_to_csv(filepath, count + 19, [f'{p3_max}',f'{p2_mean}', f'{p1_min}', f'{filepath}\\{filename}.png'],'Results') #swapped order


            popup_label.config(text = f'Running Transient Test... \n Step: {hertz_array[count]}Hz 50-100%')

            load(Load_ID, 'L1', f'{max_current/2}')
            load(Load_ID, 'L2', f'{max_current}')
            load(Load_ID, 'T1', f'{tscale}')
            load(Load_ID, 'T2', f'{tscale}')
            load(Load_ID, 'RISE', 'MAX')
            load(Load_ID, 'FALL', 'MAX')
            load(Load_ID, 'REPEAT', '0')
            supply(Supply_ID,'OUT','ON')
            time.sleep(0.5)
            load(Load_ID, 'OUT', 'ON')
            scope(Scope_ID,'AUTOSETUP')
            
            
            #time.sleep(0.3)
            
            scope_chan(Scope_ID,'C3','TRIGCHANNEL','POS')
            scope_chan(Scope_ID,'C3','ATTEN','6.03')
            scope_chan(Scope_ID,'C3','TRIGLEVEL', float((3*max_current)/4)) #3/4 is the current level
            scope_chan(Scope_ID,'C3','VOFFSET',f'-{float(3*max_current/4)}')
            scope(Scope_ID,'TDIV',f'{tscale}')
            time.sleep(0.5) #Actually neccessary


            capture_waveforms(Scope_ID,'P1', 100, f'Running Transient Test... \n Step: {hertz_array[count]}Hz 50-100%', popup_label)
            filename = f'Trans_vo_50_100_{hertz_array[count]}Hz'
            scope_screenshot(filepath,filename)


            p1_min = float(scope_chan(Scope_ID,'P1','MEAS','min'))
            p2_mean = float(scope_chan(Scope_ID,'P2','MEAS','mean'))
            p3_max = float(scope_chan(Scope_ID,'P3','MEAS','max'))

            write_to_csv(filepath, count + 24, [f'{p3_max}',f'{p2_mean}', f'{p1_min}', f'{filepath}\\{filename}.png'],'Results')

            count = count+1
            supply(Supply_ID,'OUT','OFF')
            load(Load_ID, 'OUT', 'OFF')
        

        popup_label.config(text = 'Running Transient Test.... \n Step: Input Voltage')

        #Transient load VIN
        load(Load_ID, 'OUT', 'OFF')
        supply(Supply_ID,'OUT','ON')
        time.sleep(0.5)

        load(Load_ID, 'L1', '0')
        load(Load_ID, 'L2', f'{tdc_current}')
        load(Load_ID, 'T1', '0.5ms')
        load(Load_ID, 'T2', '0.5ms')
        load(Load_ID, 'RISE', 'MAX')
        load(Load_ID, 'FALL', 'MAX')
        load(Load_ID, 'REPEAT', '0')
        scope(Scope_ID,'TDIV','0.5ms')

        load(Load_ID, 'OUT', 'ON')
        time.sleep(0.3)
        scope(Scope_ID,'AUTOSETUP')

        
        scope_chan(Scope_ID,'C2','TRACETOGGLE','ON')
        

        scope_chan(Scope_ID,'C3','TRIGCHANNEL','POS')
        scope_chan(Scope_ID,'C3','ATTEN','6.03')
        scope_chan(Scope_ID,'C3','TRIGLEVEL', float(tdc_current/4))
        
        
        scope_chan(Scope_ID,'C1','TRACETOGGLE','OFF')
        #time.sleep(0.3)
        scope(Scope_ID,'TDIV','0.5ms')
        #time.sleep(0.3)


        capture_waveforms(Scope_ID,'P1', 100, 'Running Transient Test.... \n Step: Input Voltage', popup_label)
        filename = '16_Vin_trans'
        scope_screenshot(filepath,filename)


        p4_min = float(scope_chan(Scope_ID,'P4','MEAS','min'))
        p5_max = float(scope_chan(Scope_ID,'P5','MEAS','max'))

        write_to_csv(filepath, 11, [f'{p5_max}', f'{p4_min}', f'{filepath}\\{filename}.png'],'Results')
        supply(Supply_ID,'OUT','OFF')
        load(Load_ID, 'OUT', 'OFF')


    set_wait(False)
    test_text = 'Transient Test Setup'
    listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
    transient_main()




def test_overcurrent(popup_label, popup_button1, popup_button2, testing_progressbar, scope, supply, load, device):
    """
    
    Executes overcurrent test as defined in DC DC testing manual

    Parameters:
        Scope_ID (str): MFG name of scope
        Supply_ID (str): MFG name of supply
        Load_ID (str): MFG name of load
        max_current (float): The maximum current of the DUT
        filepath (str): Path for the testing results folder
        output_voltage_nom (float): Expected nominal output voltage of DUT during normal operation
        

    """

    '''
    Steps:
    0.5: Recall setup 1(in case it got reset)
    1. Set supply current to MAX
    2. Set load mode to CCD
    3. Set L! L2 to 0A to ICCMAX
    4. T1 and T2 to 100ms
    5. Set load slew rate MIN
    6. Load repition to 1
    7. CH1 and CH3 on for scope
    8. Hor scale to 20ms/div
    9. Move horizontal offset to -50ms
    10. Trigger rising edge CH3 at 50% iccmax
    11. Adjust vert scale, put 0V at bottom of screen, and put voltage level in middle of screen
    12. Set scope to normal trigger
    13. Turn load ON, does 1 pulse
    14. If output voltage does not drop below 10%, then increase L2
    15. If ICCMAx>10, 1A steps. <3A, 0.1A steps. Vertical scale of C3 will need to be adjusted
    16. If voltage drops below 10%, capture and record P8

    '''

    def overcurrent_main():
        supply(Supply_ID,'OUT','OFF')
        load(Load_ID, 'OUT', 'OFF')
        maxpow = load(Load_ID, 'POWER', 'CPH') #Finds the max power of the load


        scope(Scope_ID,'RECALL','1')
        supply(Supply_ID,'CURR','MAX')
        load(Load_ID, 'MODE', 'CCDH')
        load(Load_ID, 'T1', '100ms')
        load(Load_ID, 'T2', '100ms')
        load(Load_ID, 'OUT', 'OFF')
        supply(Supply_ID,'OUT','ON')
        time.sleep(0.5)


        load(Load_ID, 'L1', '0')
        load(Load_ID, 'L2', f'{max_current}')
        
        load(Load_ID, 'RISE', 'MIN')
        load(Load_ID, 'FALL', 'MIN')
        load(Load_ID, 'REPEAT', '1')
        scope(Scope_ID,'TDIV','20ms')
        scope_chan(Scope_ID,'C2','TRACETOGGLE','OFF')
        scope_chan(Scope_ID,'C4','TRACETOGGLE','OFF')
        scope(Scope_ID,'TRIGDELAY','-50ms')

        scope_chan(Scope_ID,'C1','VDIV',f'{output_voltage_nom/4}')
        scope_chan(Scope_ID,'C3','VDIV',f'{max_current/3}')
        scope_chan(Scope_ID,'C1','VOFFSET',f'-{output_voltage_nom}')

        scope_chan(Scope_ID,'C1','BANDWIDTH','20MHz')
        scope_chan(Scope_ID,'C2','BANDWIDTH','20MHz')

        scope_chan(Scope_ID,'C3','ATTEN','6.03')
        scope_chan(Scope_ID,'C3','TRIGCHANNEL','POS')
        scope_chan(Scope_ID,'C3','TRIGLEVEL', float(max_current/2))

        scope_chan(Scope_ID,'C3','CHANGEP5','TOP')

        scope(Scope_ID,'TRIGMODE','SINGLE')

        #time.sleep(1)
        load(Load_ID, 'OUT', 'ON')

        time.sleep(1) #Needed pause
        load(Load_ID, 'OUT', 'OFF')
        

        voltage_level = float(scope_chan(Scope_ID,'P1','MEAS','min'))
        overcurrent_level = float(max_current)
        while (voltage_level >= float((output_voltage_nom*0.9))) and ((overcurrent_level+1) < maxpow/output_voltage_nom) and (overcurrent_level < 4*max_current):#350W is max of the chroma load. Overpower prot after that
            stepsize = 0
            if max_current <10:
                stepsize = 0.1
            elif max_current>= 10:
                stepsize = 1

            overcurrent_level = overcurrent_level + stepsize

            popup_label.config(text = f'Running Overcurrent Test... \n Current = {overcurrent_level}A')

            load(Load_ID, 'L2', f'{overcurrent_level}')
            scope_chan(Scope_ID,'C3','VDIV',f'{overcurrent_level/3}')
            scope(Scope_ID,'TRIGMODE','SINGLE')
            #time.sleep(0.8)
            load(Load_ID, 'OUT', 'ON')
            time.sleep(0.8) #Needed pause

            voltage_level = float(scope_chan(Scope_ID,'P1','MEAS','min'))

        
        supply(Supply_ID,'OUT','OFF')
        time.sleep(1)

        filename = 'OverCurrent'
        scope_screenshot(filepath,filename)

        #p8_value = float(scope_chan(Scope_ID,'P8','MEAS','min'))
        p5_value = float(scope_chan(Scope_ID,'P5','MEAS','out'))

        write_to_csv(filepath, 29, [f'{p5_value}', f'{filepath}\\{filename}.png'],'Results')

        scope_chan(Scope_ID,'C2','CHANGEP5','MAX') #Change P5 back to normal




    set_wait(False)
    test_text = 'Overcurrent Test Setup'
    listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
    overcurrent_main()





def test_vds(popup_label, popup_button1, popup_button2, testing_progressbar, scope, supply, load, device):

    """
    
    Executes mosfet VDS as defined in DC DC testing manual

    Parameters:
        Scope_ID (str): MFG name of scope
        Supply_ID (str): MFG name of supply
        Load_ID (str): MFG name of load
        tdc_current (float): Nominal current of the DUT during normal operation
        filepath (str): Path for the testing results folder
        current_testing (list): A list of strings. Contains current operating points to test for
        input_voltage (float): Input voltage for the DUT
        exfets_bool (bool): True if there are external fets. Will prompt user to swap to the high-side mosfet
        transient_load_bool (bool): True if user wants to test transient load cases, false if not. SKips if false
        
        

    """

    '''
    Steps:
    1. Recall setup 2
    2. Turn on supply
    3. Scope trigger on C4, rising
    4. Scope normal mode
    5. Scope sample rate 10G/S
    6. No Bw limit on C4
    !!!7. Lots of graph settings. COME VISIT THIS!!!
    8. Set to min load (OA)
    9. 200 cycles, screenshot. 
    10. Record min and max from CH4. And rise/fall time (mean rise/fall)
    11. Repeat 8-10 at TDC
    12. Set DC load to dynamic, 0A-TDC. 10kHz. Infinite repitition
    13. 500 samples, screenshot. Record min and max voltage
    14. Record the MINimum risisng and falling. 
    15. Turn off supply
    16. Wait for user input, insert probe across high side mosfet. 
    17. Repeat stps 8-15 with high side mosfet
    '''
    popup_label.config(text = f'VDS Test Setup')

    load(Load_ID, 'MODE', 'CCH')
    scope(Scope_ID,'RECALL','2')
    supply(Supply_ID,'OUT','ON')
    scope_chan(Scope_ID,'C4','TRIGCHANNEL','POS')
    scope_chan(Scope_ID,'C4','TRIGLEVEL', float(input_voltage/2))
    scope_chan(Scope_ID,'C4','BANDWIDTH', 'OFF')
    scope_chan(Scope_ID,'C1','TRACETOGGLE','OFF')
    scope(Scope_ID,'SAMPLERATEMAX')

    scope_chan(Scope_ID,'Z1','HORPOS','5')
    scope_chan(Scope_ID,'Z1','VERTMAG','2')
    scope_chan(Scope_ID,'Z2','HORPOS','7.5')
    scope_chan(Scope_ID,'Z2','VERTMAG','2')
    scope_chan(Scope_ID,'Z2','VERTPOS','1')

    scope_chan(Scope_ID,'C1','BANDWIDTH','20MHz')
    scope_chan(Scope_ID,'C2','BANDWIDTH','20MHz')

    #vdslowhigh = ['Low','High']


    def vds_main(vdslowhigh): 

        supply(Supply_ID,'OUT','OFF')
        vds_count = 0
        if vdslowhigh == 'Low':
            vds_count = 0
        else:
            vds_count = 5

        for current in current_testing:
            if current != 'max':
                popup_label.config(text = f'Running VDS {vdslowhigh} Test.... \n Step : {current} Load')
                
                supply(Supply_ID,'OUT','ON')
                load(Load_ID, 'OUT', 'OFF')

                if current == 'min':
                    load(Load_ID,'OUT','OFF')
                    current_count = 0
                elif current == 'tdc':
                    load(Load_ID,'CURR',tdc_current)
                    load(Load_ID,'OUT','ON')
                    current_count = 1
                else:
                    print('Incorrect array inputted for current')

                #time.sleep(0.3)
                capture_waveforms(Scope_ID,'P1', 200, f'Running VDS {vdslowhigh} Test.... \n Step : {current} Load', popup_label)
                filename = f'VDS_{vdslowhigh}_{current}'
                scope_screenshot(filepath,filename)


                p1_min = float(scope_chan(Scope_ID,'P1','MEAS','min'))
                p2_max = float(scope_chan(Scope_ID,'P2','MEAS','max'))

                p3_mean = float(scope_chan(Scope_ID,'P3','MEAS','mean'))
                p4_mean = float(scope_chan(Scope_ID,'P4','MEAS','mean'))

                write_to_csv(filepath, vds_count + current_count+33, [f'{p1_min}',f'{p2_max}', f'{p3_mean}',f'{p4_mean}',f'{filepath}\\{filename}.png'],'Results')
                load(Load_ID,'CURR','0.5')
                load(Load_ID, 'OUT', 'ON') #Turn load on to discharge voltage

            supply(Supply_ID,'OUT','OFF')

        

        if transient_load_bool:
            popup_label.config(text = f'Running VDS {vdslowhigh} Test.... \n Step : Transient Load')
            
            supply(Supply_ID,'OUT','ON')
            time.sleep(0.5)

            load(Load_ID, 'MODE', 'CCDH')
            load(Load_ID, 'L1', '0')
            load(Load_ID, 'L2', f'{tdc_current}')
            load(Load_ID, 'T1', '0.05ms')
            load(Load_ID, 'T2', '0.05ms')
            load(Load_ID, 'RISE', 'MAX')
            load(Load_ID, 'FALL', 'MAX')
            load(Load_ID, 'REPEAT', '0')
            load(Load_ID, 'OUT', 'ON')


            #time.sleep(0.3)
            capture_waveforms(Scope_ID,'P1', 500, f'Running VDS {vdslowhigh} Test.... \n Step : Transient Load', popup_label)
            filename = f'VDS_{vdslowhigh}_trans'
            scope_screenshot(filepath,filename)


            p1_min = float(scope_chan(Scope_ID,'P1','MEAS','min'))
            p2_max = float(scope_chan(Scope_ID,'P2','MEAS','max'))

            p3_min = float(scope_chan(Scope_ID,'P3','MEAS','min'))
            p4_min = float(scope_chan(Scope_ID,'P4','MEAS','min'))

            write_to_csv(filepath,vds_count + 35, [f'{p1_min}',f'{p2_max}', f'{p3_min}',f'{p4_min}',f'{filepath}\\{filename}.png'],'Results')


        supply(Supply_ID,'OUT','OFF')



    set_wait(False)
    test_text = 'VDS Test Setup'
    listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
    vds_main('Low')

    if extfets_bool:
        set_wait(True)
        test_text = 'Move Channel 4 Probe to High-Side Mosfet, then hit Continue'
        listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
        vds_main('High')


                    


def test_deadtime(popup_label, popup_button1, popup_button2, testing_progressbar, scope, supply, load, device):
    """
    
    Executes deadtime test as defined in DC DC testing manual

    Parameters:
        Scope_ID (str): MFG name of scope
        Supply_ID (str): MFG name of supply
        Load_ID (str): MFG name of load
        tdc_current (float): Nominal current of the DUT during normal operation
        filepath (str): Path for the testing results folder
        current_testing (list): A list of strings. Contains current operating points to test for
        input_voltage (float): Input voltage for the DUT
        output_voltage_nom (float): Expected nominal output voltage of DUT during normal operation
        fsw (float): Switching frequency of DUT
        
    """

    '''
    Steps:
    1. Recall setup 4
    2. Turn on supply
    3. C1 is gate drive. Highest voltage is +5 above SWnode voltage. Scale to fit whole screen
    4. Set scaling from C1 to all channels
    5. Set hor scale to show one switching cycle
    6. With load OFF
    7. Capture 200 cycles. Save waveform(?) (Steps don't specify what to do with this)
    8. Trigger scope on rising edge, zoom to show only edge, 200 captures. SCreenshot
    9. Trigger scope fo falling, zoom to only falling edge, 200 captures, screenshot
    10. Set load to TDC and repeat stesp 6-9
    11. Set load dynamic, 0A-TDC, 10kHz. Infinite rep
    12. Trigger on rising edge, zoom, 1000 captures. Screenshot
    13. Same as 12, falling
    #Dead time, turn-on
    1. Increase hor scale, want max timescale possible
    2. Scope trigger 1st rising edge, C4. at 3.3V (usually. Just a low voltage)
    3. Scope single trigger
    4. Power supply turn on
    5. Zoom in on scope to ~10cycles. Screenshot
    6. Zoom in to only 1 switching cycle, screenshot
    7. Zoom in to 2nd switching cycle, screenshot

    '''
    popup_label.config(text = 'Deadtime Test Setup')

    scope(Scope_ID,'RECALL','4')
    load(Load_ID, 'MODE', 'CCH')
    load(Load_ID, 'OUT', 'OFF')

    scope_chan(Scope_ID,'Both','PARAMFIX')
    
    scope_chan(Scope_ID,'C1','VDIV',f'{(output_voltage_nom+5)/4}')
    scope_chan(Scope_ID,'C2','VDIV',f'{(output_voltage_nom+5)/4}')
    scope_chan(Scope_ID,'C3','VDIV',f'{(output_voltage_nom+5)/4}')
    scope_chan(Scope_ID,'C4','VDIV',f'{(output_voltage_nom+5)/4}')

    scope_chan(Scope_ID,'C1','VOFFSET',f'-{(input_voltage)/2}')
    scope_chan(Scope_ID,'C2','VOFFSET',f'-{(input_voltage)/2}')
    scope_chan(Scope_ID,'C3','VOFFSET',f'-{(input_voltage)/2}')
    scope_chan(Scope_ID,'C4','VOFFSET',f'-{(input_voltage)/2}')



    
    trig_type = ['POS','NEG']

    if transient_load_bool:
        current_testing.append('transient')
    
    #Setup
    scope(Scope_ID,'TDIV',float(1/(fsw*11)))
    scope(Scope_ID,'TRIGDELAY',f'-{1/(4*fsw)}')
    load(Load_ID, 'MODE', 'CCH')
    supply(Supply_ID,'OUT','OFF')
    load(Load_ID,'OUT','OFF')
    scope(Scope_ID,'CLEAR')
    scope_chan(Scope_ID,'C4','TRIGCHANNEL','POS')
    load(Load_ID,'CURR',f'{tdc_current}')


    scope_chan(Scope_ID,'F1','HORMAG','1')


    def deadtime_main():

        #If min load is skipped, then full capture is taken at TDC load instead
        if 'min' in current_testing:
            load(Load_ID,'OUT','OFF')
        else:
            load(Load_ID,'OUT','ON')


        popup_label.config(text = 'Running Deadtime Test.... \n Step: Full')

        supply(Supply_ID,'OUT','ON')
        time.sleep(3) #Specified delay for turnon


        capture_waveforms(Scope_ID,'P1', 20, 'Running Deadtime Test.... \n Step: Full', popup_label) #Number reports back as double for some reason

        filename = f'Deadtime_Full'
        scope_screenshot(filepath,filename)

        p1_min = float(scope_chan(Scope_ID,'P1','MEAS','min'))
        p1_mean = float(scope_chan(Scope_ID,'P1','MEAS','mean'))
        p1_max = float(scope_chan(Scope_ID,'P1','MEAS','max'))


        p2_min = float(scope_chan(Scope_ID,'P2','MEAS','min'))
        p2_mean = float(scope_chan(Scope_ID,'P2','MEAS','mean'))
        p2_max = float(scope_chan(Scope_ID,'P2','MEAS','max'))



        write_to_csv(filepath, 4, [f'{p1_min}',f'{p1_mean}',f'{p1_max}',f'{p2_min}',f'{p2_mean}',f'{p2_max}', f'{filepath}\\{filename}.png'],'deadtime')


        for current in current_testing:
            #scope(Scope_ID,'TDIV',float(1/(fsw*11)))
            #scope(Scope_ID,'TRIGDELAY',f'-{1/(3*fsw)}')
            load(Load_ID, 'MODE', 'CCH')
            supply(Supply_ID,'OUT','ON')
            time.sleep(0.5)
            load(Load_ID,'OUT','OFF')
            capture_mult = 1
            if current != 'max':
                if current == 'min':
                    load(Load_ID,'OUT','OFF')
                    current_count = 0
                elif current == 'tdc':
                    load(Load_ID,'CURR',tdc_current)
                    load(Load_ID,'OUT','ON')
                    current_count = 2
                elif current == 'transient':
                    load(Load_ID, 'MODE', 'CCDH')
                    load(Load_ID, 'L1', '0')
                    load(Load_ID, 'L2', f'{tdc_current}')
                    load(Load_ID, 'T1', '0.05ms')
                    load(Load_ID, 'T2', '0.05ms')
                    load(Load_ID, 'RISE', 'MAX')
                    load(Load_ID, 'FALL', 'MAX')
                    load(Load_ID, 'REPEAT', '0')
                    load(Load_ID, 'OUT', 'ON')
                    current_count = 6
                    capture_mult = 5
                else:
                    print('Incorrect array inputted for current')


                for trigger in trig_type:
                    trig_label = 'Full'
                    trig_count = 0
                    if trigger =='POS':
                        scope(Scope_ID,'CLEAR')
                        trig_label = 'Rise'
                        scope(Scope_ID,'TDIV',float(1/(fsw*60)))
                        scope(Scope_ID,'TRIGDELAY','0')
                        scope_chan(Scope_ID,'C4','TRIGCHANNEL','POS')
                        trig_count = 0
                        capture_chan = 'P1'
                    elif trigger == 'NEG':
                        scope(Scope_ID,'CLEAR')
                        trig_label = 'Fall'
                        scope(Scope_ID,'TDIV',float(1/(fsw*60)))
                        scope(Scope_ID,'TRIGDELAY','0')
                        scope_chan(Scope_ID,'C4','TRIGCHANNEL','NEG')
                        trig_count = 1
                        capture_chan = 'P2'
                    else:
                        print('Incorrect trigger input')

                    #time.sleep(1)
                    popup_label.config(text = f'Running Deadtime Test.... \n Step: {current} {trig_label}')

                    capture_waveforms(Scope_ID,capture_chan, capture_mult*20, f'Running Deadtime Test.... \n Step: {current} {trig_label}', popup_label) #Number reports back as double for some reason


                    filename = f'Deadtime_{current}_{trig_label}'
                    scope_screenshot(filepath,filename)
                    p1_min = float(scope_chan(Scope_ID,'P1','MEAS','min'))
                    p1_mean = float(scope_chan(Scope_ID,'P1','MEAS','mean'))
                    p1_max = float(scope_chan(Scope_ID,'P1','MEAS','max'))


                    p2_min = float(scope_chan(Scope_ID,'P2','MEAS','min'))
                    p2_mean = float(scope_chan(Scope_ID,'P2','MEAS','mean'))
                    p2_max = float(scope_chan(Scope_ID,'P2','MEAS','max'))


                    write_to_csv(filepath, 5+current_count+trig_count, [f'{p1_min}',f'{p1_mean}',f'{p1_max}',f'{p2_min}',f'{p2_mean}',f'{p2_max}', f'{filepath}\\{filename}.png'],'deadtime')


        
        supply(Supply_ID,'OUT','OFF')

        popup_label.config(text = f'Running Deadtime Test.... \n Step: Turn-On ')

        #Turn-On Deadtime Test
        scope(Scope_ID,'TDIV',float(5/(fsw)))
        scope(Scope_ID,'TRIGDELAY','0')
        load(Load_ID, 'MODE', 'CCH')
        supply(Supply_ID,'OUT','OFF')
        load(Load_ID,'CURR',f'{tdc_current}')
        load(Load_ID,'OUT','ON')

        scope_chan(Scope_ID,'C4','TRIGCHANNEL','POS')
        scope_chan(Scope_ID,'C4','TRIGLEVEL','3.3')

        scope(Scope_ID,'TRIGMODE','SINGLE')
        #time.sleep(3)
        supply(Supply_ID,'OUT','ON')
        time.sleep(5) #specified 5 sec delay

        filename = f'Deadtime_Turnon'
        scope_screenshot(filepath,filename)
        p1_min = float(scope_chan(Scope_ID,'P1','MEAS','min'))
        p1_mean = float(scope_chan(Scope_ID,'P1','MEAS','mean'))
        p1_max = float(scope_chan(Scope_ID,'P1','MEAS','max'))


        p2_min = float(scope_chan(Scope_ID,'P2','MEAS','min'))
        p2_mean = float(scope_chan(Scope_ID,'P2','MEAS','mean'))
        p2_max = float(scope_chan(Scope_ID,'P2','MEAS','max'))


        write_to_csv(filepath, 15, [f'{p1_min}',f'{p1_mean}',f'{p1_max}',f'{p2_min}',f'{p2_mean}',f'{p2_max}', f'{filepath}\\{filename}.png'],'deadtime')

        scope(Scope_ID,'TDIV',float(1/(60*fsw)))
        #time.sleep(0.5)
        filename = f'Deadtime_Turnon_First'
        scope_screenshot(filepath,filename)
        p1_min = float(scope_chan(Scope_ID,'P1','MEAS','min'))
        p1_mean = float(scope_chan(Scope_ID,'P1','MEAS','mean'))
        p1_max = float(scope_chan(Scope_ID,'P1','MEAS','max'))


        p2_min = float(scope_chan(Scope_ID,'P2','MEAS','min'))
        p2_mean = float(scope_chan(Scope_ID,'P2','MEAS','mean'))
        p2_max = float(scope_chan(Scope_ID,'P2','MEAS','max'))


        write_to_csv(filepath, 16, [f'{p1_min}',f'{p1_mean}',f'{p1_max}',f'{p2_min}',f'{p2_mean}',f'{p2_max}', f'{filepath}\\{filename}.png'],'deadtime')

        scope(Scope_ID,'TRIGDELAY',f'-{2/(20*fsw)}')
        #time.sleep(0.5)
        filename = f'Deadtime_Turnon_Second'
        scope_screenshot(filepath,filename)
        p1_min = float(scope_chan(Scope_ID,'P1','MEAS','min'))
        p1_mean = float(scope_chan(Scope_ID,'P1','MEAS','mean'))
        p1_max = float(scope_chan(Scope_ID,'P1','MEAS','max'))


        p2_min = float(scope_chan(Scope_ID,'P2','MEAS','min'))
        p2_mean = float(scope_chan(Scope_ID,'P2','MEAS','mean'))
        p2_max = float(scope_chan(Scope_ID,'P2','MEAS','max'))


        write_to_csv(filepath, 17, [f'{p1_min}',f'{p1_mean}',f'{p1_max}',f'{p2_min}',f'{p2_mean}',f'{p2_max}', f'{filepath}\\{filename}.png'],'deadtime')

        supply(Supply_ID,'OUT','OFF')


    set_wait(True)
    test_text = 'Deadtime Test Setup: \n Channel 1: HighSide Mosfet Gate \n Channel 2: Input Voltage (Buck) or Output Voltage (Boost) \n Channel 3: LowSide Mosfet Gate \n Channel 4: Low-Side Mosfet (Differential) \n Setup Complete?'
    listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
    deadtime_main()






def test_turnonoff(popup_label, popup_button1, popup_button2, testing_progressbar, scope, supply, load, device):
    """
    
    Executes turn on and turn off tests as defined in DC DC testing manual

    Parameters:
        Scope_ID (str): MFG name of scope
        Supply_ID (str): MFG name of supply
        Load_ID (str): MFG name of load
        tdc_current (float): Nominal current of the DUT during normal operation
        filepath (str): Path for the testing results folder
        current_testing (list): A list of strings. Contains current operating points to test for
        input_voltage (float): Input voltage for the DUT
        output_voltage_nom (float): Expected nominal output voltage of DUT during normal operation
        
    """


    '''
    Steps:
    1. Recall setup 3
    2. Turn on supply 
    3. Scale all 4 signals such that each take up 2 divisions. C1 top, C4 bottom
    4. Trigger rising edge, C4, at half output voltage
    5. Scale hor until all rising edges are shown on screen. Takes multiple tries
    6. Set catprue to single, Take screenshot
    7. Center rising edge of C4, zoom until rising of enable is visible. Screenshot
    8. Zoom back out, Supply OFF
    9. Set load to TDC, turn ON
    10. Set oscilloscope to single
    11. Turn on supply, wait for capture. Disable load. Screenshot
    12. Zoom in on risisng c4 edge. Screenshot
    #turn off steps
    13. Power supply ON. set hor scale to 200ms/div
    14. Trigger on C4, falling, half output. Single trigger
    15. Turn supply off. Wait, then screenshot
    16. Zoom in on falling output voltage edge. Screenshot
    17. Zoom out & Turn supply on. Wait. Set scope to capture again.
    18. Turn off supply. See input voltage falling. Screenshot
    19. Zoom in on falling edge of output voltage, screenshot

    '''
    popup_label.config(text = f'Turn-On Test Setup')
    scope(Scope_ID,'RECALL','3')
    load(Load_ID, 'MODE', 'CCH')
    load(Load_ID, 'OUT', 'OFF')

    supply(Supply_ID,'OUT','OFF')


    #Setting up 2 div per, stacked, for channels
    scope_chan(Scope_ID,'C1','VDIV',f'{(1.1*input_voltage)/2}')
    scope_chan(Scope_ID,'C1','VOFFSET',f'{(1.1*input_voltage)}')

    scope_chan(Scope_ID,'C2','VDIV','2.25')
    scope_chan(Scope_ID,'C2','VOFFSET','0')

    scope_chan(Scope_ID,'C3','VDIV',f'{(1.1*input_voltage)/2}')
    scope_chan(Scope_ID,'C3','VOFFSET',f'-{(2*1.1*input_voltage)/2}')

    scope_chan(Scope_ID,'C4','VDIV',f'{(1.5*output_voltage_nom)/2}')
    scope_chan(Scope_ID,'C4','VOFFSET',f'-{(2*1.5*output_voltage_nom)}')
    scope_chan(Scope_ID,'C4','TRIGCHANNEL','POS')
    scope_chan(Scope_ID,'C4','TRIGLEVEL',f'{output_voltage_nom/2}')



    def turnon_main():
        for current in current_testing:
            #if there is no min or TDC operating point, will skip
            run_test = False
            scope(Scope_ID,'TRIGDELAY','0')
            

            if current == 'min':
                scope(Scope_ID,'TDIV','500ms')
                load(Load_ID, 'OUT', 'OFF')
                current_count = 0
                run_test = True
            elif current == 'tdc':
                scope(Scope_ID,'TDIV','500ms')
                load(Load_ID, 'CURR', tdc_current)
                load(Load_ID, 'OUT', 'ON')
                current_count = 2
                run_test = True



            def run_test_setup(run_test, mode = 'CCH'):
                scope(Scope_ID,'TRIGDELAY','0')
                if run_test:
                    popup_label.config(text = f'Running {current} Turn-On Test')
                    if mode == 'CRL':
                        load(Load_ID, 'MODE', 'CRL')
                        load(Load_ID, 'RESIST', output_voltage_nom/tdc_current)
                        load(Load_ID, 'OUT', 'ON')
                        time.sleep(1)

                    scope(Scope_ID,'TRIGMODE','SINGLE')
                    time.sleep(5) #Neccessary delay. Due to slow aqusistion mode
                    supply(Supply_ID,'OUT','ON')
                    time.sleep(5)
                    supply(Supply_ID,'OUT','OFF')
                    load(Load_ID, 'MODE', 'CCH')

            def rising():
                filename = f'Turn-On_{current}'
                scope_screenshot(filepath,filename)

                p2_rise_ms = float(scope_chan(Scope_ID,'P2','MEAS','out',1000))
                #p2_rise_ms = round(p2_rise*1000,3)
                write_to_csv(filepath, current_count + 3, [f'{p2_rise_ms}',f'{filepath}\\{filename}.png'],'Turn_on_off')
                

            def rising_zoom():
                filename = f'Turn-On_{current}_Zoom'
                scope_screenshot(filepath,filename)

                p2_rise_ms = float(scope_chan(Scope_ID,'P2','MEAS','out',1000))
                #p2_rise_ms = round(p2_rise*1000,3)
                write_to_csv(filepath, current_count + 4, [f'{p2_rise_ms}',f'{filepath}\\{filename}.png'],'Turn_on_off')
                



            run_test_setup(run_test)


            if (run_test == True) and (current == 'tdc'):
                set_wait(True)
                set_skip(True)
                test_text = 'Adjust horizontal delay and scale until all rising edges are visible. Hit Continue when done. \n Press skip to instead re-run in CR mode'
                listener(popup_button1, popup_button2, 'enabled', popup_label, test_text, testing_progressbar)
                if not get_skip():
                    run_test_setup(True, 'CRL')
                    set_wait(True)
                    test_text = 'CR MODE. Adjust horizontal delay and scale until all rising edges are visible. Hit Continue when done'
                    listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
                    set_skip()
                    rising()

                    set_wait(True)
                    test_text = 'CR MODE Adjust horizontal delay and scale until ONLY rising edge of C3 and C4 are visible (Zoom in). Hit Continue when done'
                    listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
                    rising_zoom()
                else:
                    rising()
                    set_wait(True)
                    test_text = 'Adjust horizontal delay and scale until ONLY rising edge of C3 and C4 are visible (Zoom in). Hit Continue when done'
                    listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
                    rising_zoom()


            elif (run_test == True) and (current == 'min'):
                set_wait(True)
                test_text = 'Adjust horizontal delay and scale until all rising edges are visible. Hit Continue when done.'
                listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
                rising()

                set_wait(True)
                test_text = 'Adjust horizontal delay and scale until ONLY rising edge of C3 and C4 are visible (Zoom in). Hit Continue when done'
                listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
                rising_zoom()

        


            


    def turnoff_main(buttontest):
        popup_label.config(text = f'Running Turn-Off Test')
        test_list = ['Button','AC']
        if buttontest == 'ACOnly':
            test_list = ['AC']

        for test_name in test_list:
            #popup_label.config(text = f'Running Turn-Off Test.... \n Step: {test_name}')
            exceloffset = 0
            
            

            scope(Scope_ID,'TRIGDELAY','0')
            if test_name == 'AC':
                scope(Scope_ID,'TDIV','1s')
                supply(Supply_ID,'OUT','OFF') #Resetting after button test
                time.sleep(5)
                supply(Supply_ID,'OUT','ON')
                time.sleep(8)
                scope(Scope_ID,'TRIGMODE','SINGLE')
                time.sleep(8)
                supply(Supply_ID,'OUT','OFF')
                exceloffset = 2
                
            def falling():
                filename = f'Turn-Off_{test_name}'
                scope_screenshot(filepath,filename)

                #time.sleep(0.5)
                p6_fall_ms = float(scope_chan(Scope_ID,'P6','MEAS','out', 1000))
                #p6_fall_ms = p6_fall*1000
                p5_base = float(scope_chan(Scope_ID,'P5','MEAS','out'))
                write_to_csv(filepath, 9 + exceloffset, [f'{p6_fall_ms}',f'{p5_base}',f'{filepath}\\{filename}.png'],'Turn_on_off')

            def falling_zoom():
                filename = f'Turn-Off_{test_name}_Zoom'
                scope_screenshot(filepath,filename)

                p6_fall_ms = float(scope_chan(Scope_ID,'P6','MEAS','out',1000))
                #p6_fall_ms = p6_fall*1000
                p5_base = float(scope_chan(Scope_ID,'P5','MEAS','out'))
                write_to_csv(filepath, 10 + exceloffset, [f'{p6_fall_ms}',f'{p5_base}',f'{filepath}\\{filename}.png'],'Turn_on_off')
               

            time.sleep(4)
            set_wait(True)
            test_text = 'Adjust horizontal delay and scale until all falling edges are visible. Hit Continue when done'
            listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
            falling()

            set_wait(True)
            test_text = 'Adjust horizontal delay and scale until ONLY falling edge of C3 and C4 are visible (Zoom in). Hit Continue when done'
            listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
            falling_zoom()

    set_wait(True)
    test_text = 'Channel 1: Input Voltage \n Channel 2: VCC Voltage \n Channel 3: Enable \n Channel 4: Output Voltage \n Setup Complete?'
    listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
    turnon_main()



    popup_label.config(text = f'Turn-Off Test Setup')
    #Setup for Turnoff test
    scope(Scope_ID,'TDIV','1s')
    scope_chan(Scope_ID,'C4','TRIGCHANNEL','NEG')
    scope_chan(Scope_ID,'C4','CHANGEP5','BASE')
    load(Load_ID, 'OUT', 'OFF')
    supply(Supply_ID,'OUT','ON')
    time.sleep(5) #Specified pause
    scope(Scope_ID,'TRIGMODE','SINGLE')
    time.sleep(3) #Specified pause

    set_wait(True)
    set_skip(True)
    test_text = 'For Power-Button test, hit "Continue" after power button has been pressed. To skip, hit "Skip" '
    listener(popup_button1, popup_button2, 'enabled', popup_label, test_text, testing_progressbar)

    if not get_skip():
        turnoff_main('ACOnly')
    else:
        turnoff_main('Button')
