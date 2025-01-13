from datetime import datetime
from EquipmentClasses import *
import os
import csv
import time
import tkinter as tk
import tkinter.ttk as ttk #this is for THEMED widgets. Explicitly calls them out
import shutil



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
  



def create_folder(input_voltage:float, device_under_test:str, device:DUT):
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
    #print(python_path)
    folder_name_path = f'{python_path}\\{results_folder_name}'
    os.makedirs(folder_name_path)


    template_name = device.getDeviceReport()

    filled_template_name = f'{device.dut_type} - {device.name} - {round(device.supply_input_voltage,1)}V Input'

    if template_name != '':
        shutil.copy2(f'{python_path}\\Templates\\{template_name}', f'{folder_name_path}\\{filled_template_name}.xlsm')



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
        time.sleep(0.3)
        load.output(False)

        scope.recall(1)
        #scope.autoSetup()
        scope.setTrigger('C2','POS', device.device_input_voltage)
        scope.setupChannelPercent('C1', device.output_voltage_nom , 20)
        scope.setupChannelPercent('C2', device.device_input_voltage, 20)
        scope.setParam('P5','C2','MEAN')



        time.sleep(30)#Sleeps for 30 sec to get accurate 0 load data
        first_loop = True
        for linspace in range(0,26):

            meas_result = []

            scope.clearSweeps()

            current_set = round(float(linspace*(device.output_current_nom/25)),3)
            load.staticCurrent(current_set)
            time.sleep(1)
            scope.forceCapture()

            meas_result.append(current_set)
            meas_result.append(scope.meas('P2','out'))

            if device.jitter_bool:
                meas_result.append(supply.meas('VOLT'))                
            else:
                meas_result.append(scope.meas('P5','out'))
            meas_result.append(supply.meas('CURR'))
        
            efficiency_results.append(meas_result)

            if first_loop:
                for repeat in range(18):
                    efficiency_results.append([])
                first_loop = False
                load.output(True)
                time.sleep(0.5)


        meas_result = []
        scope.clearSweeps()

        meas_result.append(device.output_current_max)
        load.staticCurrent(device.output_current_max)
        time.sleep(0.5)
        scope.forceCapture()

        meas_result.append(scope.meas('P2','out'))
        if device.jitter_bool:
            meas_result.append(supply.meas('VOLT'))           
        else:
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
        scope.timeScale(float(1/device.frequency))
        scope.sampleRate()
        scope.setTrigger('C4','POS',float(device.device_input_voltage/2))

        scope.traceToggle('C1', True)
        scope.traceToggle('C2', True)
        scope.traceToggle('C3', True)
        scope.traceToggle('C4', True)

        scope.setupChannelPercent('C1',device.output_voltage_nom,6)
        scope.setupChannelPercent('C2',device.device_input_voltage,6)
        scope.setupChannel('C4', 0, device.device_input_voltage)

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
            p2_mean = scope.meas('P2','mean')
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

                #scope.setParam('P5','C3','MAX') #Change to max?? Maybe
                scope.setParam('P5','C4','DUTY')

                scope.captureWaveforms('P5', 2000, f'Running Jitter Test.... \n Step: {current} Load', popup_label, 30)
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
                scope.setParam('P5','C2','MAX')
   

            scope.traceToggle('C1', True)
            scope.traceToggle('C2', True)
            scope.traceToggle('C3', True)
            scope.traceToggle('C4', True)
        discharge(device)


    set_wait(True)
    if device.test_list[0]:
        set_wait(False)
    test_text = 'Ripple & Jitter Test Setup: \n Channel 1: Output Voltage \n Channel 2: Input Voltage \n Channel 3: Load Current (BNC) \n Channel 4: Low-Side Mosfet (Differential) \n Setup Complete?'
    listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
    ripple_jitter_main()




def test_transient(popup_label, popup_button1, popup_button2, testing_progressbar, scope:SCOPE, supply:SUPPLY, load:LOAD, device:DUT):
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

        supply.output(True)
        load.output(False)
        load.mode('CCD','H')

        scope.recall(1)

        scope.setupChannelPercent('C1',device.output_voltage_nom,6)
        scope.setupChannelPercent('C2',device.device_input_voltage,6)
        scope.traceToggle('C2',False)
        scope.traceToggle('C4',False)

        L2_array = [50,100]
        current_array = [0, device.output_current_max/2, device.output_current_max]
        hertz_array = ['100','1k','10k']
        
        for count, hertz in enumerate(hertz_array):
            load.output(False)
            if 'k' in hertz:
                hertz= float(hertz[:-1])*1000

            scope.timeScale(1/(2*float(hertz)))

            for L2_count,L1 in enumerate([0, 50]):

                popup_label.config(text = f'Running Transient Test... \n Step: {hertz_array[count]}Hz {L1}-{L2_array[L2_count]}%')

                load.output(False)

                load.dynamicSetup('H',current_array[L2_count],current_array[L2_count+1], hertz, 'MAX', 0)

                scope.setupChannel('C3', current_array[L2_count],current_array[L2_count+1])
                scope.setTrigger('C3','POS', ((2*L2_count)+1)*device.output_current_max/4)
                
                time.sleep(0.3)
                load.output(True)

                scope.captureWaveforms('P1', 100, f'Running Transient Test... \n Step: {hertz_array[count]}Hz {L1}-{L2_array[L2_count]}% ', popup_label)
                filename = f'Trans_vo_{L1}_{L2_array[L2_count]}_{hertz_array[count]}Hz'
                scope.screenshot(device.folder_name_path,filename)

                p1_min = scope.meas('P1','min')
                p2_mean = scope.meas('P2','mean')
                p3_max = scope.meas('P3','max')


                write_to_csv(device.folder_name_path, 5*L2_count + count + 19, [f'{p3_max}',f'{p2_mean}', f'{p1_min}', f'{device.folder_name_path}\\{filename}.png'],'Results') #swapped order


            '''

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
            '''
        

        popup_label.config(text = 'Running Transient Test.... \n Step: Input Voltage')

        load.output(False)

        

        load.dynamicSetup('H',0, device.output_current_nom, '1k', 'MAX', 0)

        scope.setupChannel('C3', 0, device.output_current_nom)
        scope.setTrigger('C3','POS', device.output_current_nom/4)

        scope.traceToggle('C2',True)
        scope.setupChannelPercent('C2',device.device_input_voltage, 6)
        scope.traceToggle('C1',False)

        scope.timeScale('0.5ms')

        time.sleep(0.3)
        load.output(True)


        scope.captureWaveforms('P1', 100, 'Running Transient Test.... \n Step: Input Voltage', popup_label)
        filename = '16_Vin_trans'
        scope.screenshot(device.folder_name_path,filename)

        p4_min = scope.meas('P4','min')
        p5_max = scope.meas('P5','max')

        write_to_csv(device.folder_name_path, 11, [f'{p5_max}', f'{p4_min}', f'{device.folder_name_path}\\{filename}.png'],'Results')
        discharge(device)


    set_wait(False)
    test_text = 'Transient Test Setup'
    listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
    transient_main()




def test_overcurrent(popup_label, popup_button1, popup_button2, testing_progressbar, scope:SCOPE, supply:SUPPLY, load:LOAD, device:DUT):
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

        load.output(False)
        supply.output(True)


        scope.recall(1)
        supply.setCurrent('MAX')
  
        load.dynamicSetup('H',0, device.output_current_max, 5, 'MIN', 1)

        scope.timeScale('20ms')

        scope.traceToggle('C2',False)
        scope.traceToggle('C4',False)

        scope.setTrigger('C3', 'POS', device.output_current_max/2)

        scope.triggerDelay('-50ms')

        scope.vertScale('C1', device.output_voltage_nom/4)
        scope.offsetVert('C1', f'-{device.output_voltage_nom}')
        scope.vertScale('C3', device.output_current_max/3)

        scope.setParam('P5','C3','MAX') #Changing from TOP to MAX. top never seems to work

        

        scope.trigMode('SINGLE')
        time.sleep(0.2)
        load.output(True)
        scope.WAIT()


        scope.meas('P1','min')

        stepsize = 0
        voltage_level = scope.meas('P1','min')
        overcurrent_level = float(device.output_current_max)

        if device.output_current_max <10:
            stepsize = 0.1
        elif device.output_current_max>= 10:
            stepsize = 1

        while (voltage_level >= float((device.output_voltage_nom*0.9))) and ((overcurrent_level+1) < load.max_power/device.output_voltage_nom):# and (overcurrent_level < 4*device.output_current_max):    #350W is max of the chroma load. Overpower prot after that
            overcurrent_level = overcurrent_level + stepsize

            popup_label.config(text = f'Running Overcurrent Test... \n Current = {round(overcurrent_level,2)}A')

            load.dynamicLevel('L2', overcurrent_level)

            scope.vertScale('C3', overcurrent_level/3)

            scope.trigMode('SINGLE')
            time.sleep(0.2)
            load.output(True)
            scope.WAIT()

            voltage_level = scope.meas('P1','min')
            current_level = scope.meas('P5','out')


            if voltage_level < float(device.output_voltage_nom*0.9):
                oc_reason = 'Voltage < 90%'
                break
            if (overcurrent_level+(2*stepsize)) > load.max_power/device.output_voltage_nom:
                oc_reason = 'Max Load Power'
                break
            if current_level < (overcurrent_level*0.7):
                oc_reason = 'DUT Current Limiting'
                break


        
        supply.output(False)
        filename = 'OverCurrent'
        scope.screenshot(device.folder_name_path,filename)

       
        p5_value = voltage_level = scope.meas('P5','out')

        write_to_csv(device.folder_name_path, 29, [f'{p5_value}', f'{device.folder_name_path}\\{filename}.png', oc_reason],'Results')


    set_wait(False)
    test_text = 'Overcurrent Test Setup'
    listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
    overcurrent_main()





def test_vds(popup_label, popup_button1, popup_button2, testing_progressbar, scope:SCOPE, supply:SUPPLY, load:LOAD, device:DUT):

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


    load.mode('CC','H')

    scope.recall(2)


    scope.setTrigger('C4','POS',device.device_input_voltage/2)
    scope.bandwidth('C4','OFF')
    scope.traceToggle('C1','OFF')


    scope.sampleRate()


    scope.zoomHorDelay('Z1',5)
    scope.zoomVertMagnify('Z1',2)
    scope.zoomHorDelay('Z2',5)
    scope.zoomVertMagnify('Z2',2)
    scope.zoomOffsetVert('Z2',1)

    #vdslowhigh = ['Low','High']

    current_testing = device.makeLoadPointList(['max','transient'])

    def vds_main(vdslowhigh): 

        vds_count = 0
        if vdslowhigh == 'Low':
            vds_count = 0
        else:
            vds_count = 5

        for current in current_testing:
            
            popup_label.config(text = f'Running VDS {vdslowhigh} Test.... \n Step : {current} Load')
            load.output(False)
            supply.output(True)

            if current == 'min':
                current_count = 0
            elif current == 'tdc':
                load.staticCurrent(device.output_current_nom)
                load.output(True)
                current_count = 1

            #time.sleep(0.3)
            scope.captureWaveforms('P1', 200, f'Running VDS {vdslowhigh} Test.... \n Step : {current} Load', popup_label)
            filename = f'VDS_{vdslowhigh}_{current}'
            scope.screenshot(device.folder_name_path,filename)

            scope.meas('P1','min')

            p1_min = scope.meas('P1','min')
            p2_max = scope.meas('P2','max')

            p3_mean = scope.meas('P3','mean', 10**9)
            p4_mean = scope.meas('P4','mean', 10**9)

            write_to_csv(device.folder_name_path, vds_count + current_count+33, [f'{p1_min}',f'{p2_max}', f'{p3_mean}ns',f'{p4_mean}ns',f'{device.folder_name_path}\\{filename}.png'],'Results')
            discharge(device)

        

        if 'transient' in device.load_list:
            popup_label.config(text = f'Running VDS {vdslowhigh} Test.... \n Step : Transient Load')
            
            supply.output(True)
    
            time.sleep(0.5)

            load.dynamicSetup('H',0, device.output_current_nom, 10000, 'MAX', 0)

            load.output(True)
          


            #time.sleep(0.3)
            scope.captureWaveforms('P1', 500, f'Running VDS {vdslowhigh} Test.... \n Step : Transient Load', popup_label)
            filename = f'VDS_{vdslowhigh}_trans'
            scope.screenshot(device.folder_name_path,filename)


            p1_min = scope.meas('P1','min')
            p2_max = scope.meas('P2','max')

            p3_min = scope.meas('P3','min', 10**9)
            p4_min = scope.meas('P4','min', 10**9)
            write_to_csv(device.folder_name_path,vds_count + 35, [f'{p1_min}',f'{p2_max}', f'{p3_min}ns',f'{p4_min}ns',f'{device.folder_name_path}\\{filename}.png'],'Results')


        supply.output(False)



    set_wait(False)
    test_text = 'VDS Test Setup'
    listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
    vds_main('Low')

    if device.extfets:
        set_wait(True)
        test_text = 'Move Channel 4 Probe to High-Side Mosfet, then hit Continue'
        listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
        vds_main('High')


                    


def test_deadtime(popup_label, popup_button1, popup_button2, testing_progressbar, scope:SCOPE, supply:SUPPLY, load:LOAD, device:DUT):
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

    scope.recall(4)
    load.output(False)
    load.mode('CC','H')
    supply.output(False)


    scope.zoomHorMagnify('F1',1)
    
    #Changes scaling if device is boost or buck
    if device.device_input_voltage < device.output_voltage_nom:
        for channel in ['C1','C2','C3','C4']:
            scope.vertScale(channel,(device.output_voltage_nom+5)/4)
            scope.offsetVert(channel, f'-{device.output_voltage_nom/2}')
        trig_level = device.output_voltage_nom/2
    else:
        for channel in ['C1','C2','C3','C4']:
            scope.vertScale(channel,(device.device_input_voltage+5)/4)
            scope.offsetVert(channel, f'-{device.device_input_voltage/2}')
        trig_level = device.device_input_voltage/2

    trig_type = ['POS','NEG']

    #Setup

    scope.timeScale(1/(device.frequency*11))
    

    scope.setTrigger('C1','POS',trig_level)

    load.staticCurrent(device.output_current_nom)

    scope.setParam('P6','C4','WID')

    def deadtime_main():

        #If min load is skipped, then full capture is taken at TDC load instead
        supply.output(True)
        time.sleep(0.3)
        if 'min' in device.load_list:
            load.output(False)
        else:
            load.output(True)

        c4_width = scope.meas('P6','out',10**9)

        scope.triggerDelay(f'-{c4_width/(2*(10**9))}')

        popup_label.config(text = 'Running Deadtime Test.... \n Step: Full')

        
        time.sleep(3) #Specified delay for turnon


        scope.captureWaveforms('P1', 200, 'Running Deadtime Test.... \n Step: Full', popup_label) #Number reports back as double for some reason

        filename = f'Deadtime_Full'
        scope.screenshot(device.folder_name_path,filename)

        p1_min = scope.meas('P1','min', 10**9)
        p1_mean = scope.meas('P1','mean', 10**9)
        p1_max = scope.meas('P1','max', 10**9)


        p2_min = scope.meas('P2','min', 10**9)
        p2_mean = scope.meas('P2','mean', 10**9)
        p2_max = scope.meas('P2','max', 10**9)



        write_to_csv(device.folder_name_path, 4, [f'{p1_min}ns',f'{p1_mean}ns',f'{p1_max}ns',f'{p2_min}ns',f'{p2_mean}ns',f'{p2_max}ns', f'{device.folder_name_path}\\{filename}.png'],'deadtime')

        current_testing = device.makeLoadPointList('max')

        for current in current_testing:
            load.mode('CC','H')
            load.output(False)
            load.staticCurrent(device.output_current_nom)
            supply.output(True)
            time.sleep(0.3)
            capture_mult = 1

            if current == 'min':
                current_count = 0
            elif current == 'tdc':
                load.output(True)
                current_count = 2
            elif current == 'transient':
                load.dynamicSetup('H',0, device.output_current_nom,10000,'MAX',0)
                load.output(True)
                current_count = 6
                capture_mult = 5
            else:
                print('Incorrect array inputted for current')


            for trigger in trig_type:
                trig_label = 'Full'
                trig_count = 0
                scope.timeScale(1/(device.frequency*60))
                scope.triggerDelay(0)
                if trigger =='POS':
                    trig_label = 'Rise'
                    scope.setTrigger('C1','POS',trig_level)
                    trig_count = 0
                    capture_chan = 'P1'
                elif trigger == 'NEG':
                    trig_label = 'Fall'
                    scope.setTrigger('C1','NEG',trig_level)
                    trig_count = 1
                    capture_chan = 'P2'

                #time.sleep(1)
                popup_label.config(text = f'Running Deadtime Test.... \n Step: {current} {trig_label}')

                scope.captureWaveforms(capture_chan, capture_mult*200, f'Running Deadtime Test.... \n Step: {current} {trig_label}', popup_label) #Number reports back as double for some reason


                filename = f'Deadtime_{current}_{trig_label}'
                scope.screenshot(device.folder_name_path,filename)
                scope.meas('P1','min')
                p1_min = scope.meas('P1','min', 10**9)
                p1_mean = scope.meas('P1','mean', 10**9)
                p1_max = scope.meas('P1','max', 10**9)

                p2_min = scope.meas('P2','min', 10**9)
                p2_mean = scope.meas('P2','mean', 10**9)
                p2_max = scope.meas('P2','max', 10**9)


                write_to_csv(device.folder_name_path, 5+current_count+trig_count, [f'{p1_min}ns',f'{p1_mean}ns',f'{p1_max}ns',f'{p2_min}ns',f'{p2_mean}ns',f'{p2_max}ns', f'{device.folder_name_path}\\{filename}.png'],'deadtime')


        
        supply.output(False)

        popup_label.config(text = f'Running Deadtime Test.... \n Step: Turn-On ')

        #Turn-On Deadtime Test

        scope.timeScale(5/device.frequency)
        scope.triggerDelay(0)
        load.mode('CC','H')
        load.staticCurrent(device.output_current_nom)
        load.output(True)
        scope.setTrigger('C4','POS',3.3)

        scope.trigMode('SINGLE')
        supply.output(True)
        time.sleep(5) #specified 5 sec delay
        c4_width = scope.meas('P6','out',10**9)

        scope.triggerDelay(f'-{c4_width/(2*(10**9))}')

        filename = f'Deadtime_Turnon'
        scope.screenshot(device.folder_name_path,filename)
        p1_min = scope.meas('P1','min', 10**9)
        p1_mean = scope.meas('P1','mean', 10**9)
        p1_max = scope.meas('P1','max', 10**9)

        p2_min = scope.meas('P2','min', 10**9)
        p2_mean = scope.meas('P2','mean', 10**9)
        p2_max = scope.meas('P2','max', 10**9)



        write_to_csv(device.folder_name_path, 15, [f'{p1_min}ns',f'{p1_mean}ns',f'{p1_max}ns',f'{p2_min}ns',f'{p2_mean}ns',f'{p2_max}ns', f'{device.folder_name_path}\\{filename}.png'],'deadtime')

        scope.timeScale(1/(55*device.frequency))

        filename = f'Deadtime_Turnon_First'
        scope.screenshot(device.folder_name_path,filename)
        p1_min = scope.meas('P1','min', 10**9)
        p1_mean = scope.meas('P1','mean', 10**9)
        p1_max = scope.meas('P1','max', 10**9)

        p2_min = scope.meas('P2','min', 10**9)
        p2_mean = scope.meas('P2','mean', 10**9)
        p2_max = scope.meas('P2','max', 10**9)


        write_to_csv(device.folder_name_path, 16, [f'{p1_min}ns',f'{p1_mean}ns',f'{p1_max}ns',f'{p2_min}ns',f'{p2_mean}ns',f'{p2_max}ns', f'{device.folder_name_path}\\{filename}.png'],'deadtime')

 
        scope.timeScale(5/(60*device.frequency))

        supply.output(False)

        set_wait(True)
        test_text = 'Adjust horizontal delay of C1 until second turn-on is visible. Hit Continue when done.'
        listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)

        filename = f'Deadtime_Turnon_Second'
        scope.screenshot(device.folder_name_path,filename)
        p1_min = scope.meas('P1','min', 10**9)
        p1_mean = scope.meas('P1','mean', 10**9)
        p1_max = scope.meas('P1','max', 10**9)

        p2_min = scope.meas('P2','min', 10**9)
        p2_mean = scope.meas('P2','mean', 10**9)
        p2_max = scope.meas('P2','max', 10**9)


        write_to_csv(device.folder_name_path, 17, [f'{p1_min}ns',f'{p1_mean}ns',f'{p1_max}ns',f'{p2_min}ns',f'{p2_mean}ns',f'{p2_max}ns', f'{device.folder_name_path}\\{filename}.png'],'deadtime')

        supply.output(False)


    set_wait(True)
    test_text = 'Deadtime Test Setup: \n Channel 1: HighSide Mosfet Gate \n Channel 2: Input Voltage (Buck) or Output Voltage (Boost) \n Channel 3: LowSide Mosfet Gate \n Channel 4: Low-Side Mosfet (Differential) \n Setup Complete?'
    listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
    deadtime_main()






def test_turnonoff(popup_label, popup_button1, popup_button2, testing_progressbar, scope:SCOPE, supply:SUPPLY, load:LOAD, device:DUT):
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

    scope.recall(3)
    supply.output(False)
    load.output(False)
    load.mode('CC','H')


    #Setting up 2 div per, stacked, for channels
    scope.vertScale('C1', 1.1*device.device_input_voltage/2)
    scope.offsetVert('C1', 1.1*device.device_input_voltage)

    scope.vertScale('C2', '2.25')
    scope.offsetVert('C2', 0)

    scope.vertScale('C3', '2.25')
    scope.offsetVert('C3', -2*2.25)

    scope.vertScale('C4', 1.5*device.output_voltage_nom/2)
    scope.offsetVert('C4', f'-{2*1.3*device.output_voltage_nom}')

   
    scope.setTrigger('C4','POS',device.output_voltage_nom/2)

    current_testing = device.makeLoadPointList(['max','transient'])

    def turnon_main():
        for current in current_testing:
            #if there is no min or TDC operating point, will skip
            scope.triggerDelay(0)
            scope.timeScale('500ms')
            if current == 'min':
                load.output(False)
                current_count = 0
            elif current == 'tdc':
                load.staticCurrent(device.output_current_nom)
                load.output(True)
                current_count = 2



            def run_test_setup(mode = 'CCH'):
                scope.triggerDelay(0)
                popup_label.config(text = f'Running {current} {mode} Turn-On Test')
                if mode == 'CRL':
                    load.mode('CR','L')
                    load.staticResist(device.output_voltage_nom/device.output_current_nom)
                    load.output(True)


                scope.trigMode('SINGLE')
                time.sleep(5)
                supply.output(True)
                scope.WAIT(10) #Waits until capture is taken
                supply.output(False)
                load.mode('CC','H')

            def rising():
                filename = f'Turn-On_{current}'
                scope.screenshot(device.folder_name_path,filename)

                p2_rise_ms = scope.meas('P2','out',1000)
                write_to_csv(device.folder_name_path, current_count + 3, [f'{p2_rise_ms}ms',f'{device.folder_name_path}\\{filename}.png'],'Turn_on_off')
                

            def rising_zoom():
                filename = f'Turn-On_{current}_Zoom'
                scope.screenshot(device.folder_name_path,filename)

                p2_rise_ms = scope.meas('P2','out',1000)

                write_to_csv(device.folder_name_path, current_count + 4, [f'{p2_rise_ms}ms',f'{device.folder_name_path}\\{filename}.png'],'Turn_on_off')
                

            run_test_setup()


            if (current == 'tdc'):
                load.output(True)
                set_wait(True)
                set_skip(True)
                test_text = 'Adjust horizontal delay and scale until all rising edges are visible. Hit Continue when done. \n Press skip to instead re-run in CR mode'
                listener(popup_button1, popup_button2, 'enabled', popup_label, test_text, testing_progressbar)
                if not get_skip():
                    time.sleep(0.3)
                    run_test_setup('CRL')
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


            elif (current == 'min'):
                set_wait(True)
                test_text = 'Adjust horizontal delay and scale until all rising edges are visible. Hit Continue when done.'
                listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
                rising()

                set_wait(True)
                test_text = 'Adjust horizontal delay and scale until ONLY rising edge of C3 and C4 are visible (Zoom in). Hit Continue when done'
                listener(popup_button1, popup_button2, 'disabled', popup_label, test_text, testing_progressbar)
                rising_zoom()

        


            


    def turnoff_main(buttontest):
        test_list = ['Button','AC']
        if buttontest == 'ACOnly':
            test_list = ['AC']

        for test_name in test_list:
            #popup_label.config(text = f'Running Turn-Off Test.... \n Step: {test_name}')
            exceloffset = 0
            
            popup_label.config(text = f'Running {test_name} Turn-Off Test')
            if test_name == 'AC':
                scope.triggerDelay(0)
                scope.timeScale(2)
                supply.output(False)
                load.mode('CC','H')
                load.staticCurrent(0.1)
                load.output(True)
                time.sleep(3)
                load.output(False)
                supply.output(True)
                time.sleep(5) #Specified delay
                

                scope.trigMode('SINGLE')
                time.sleep(15)
                supply.output(False)
                scope.WAIT()

                exceloffset = 2
                
            def falling():
                filename = f'Turn-Off_{test_name}'
                scope.screenshot(device.folder_name_path,filename)

                #time.sleep(0.5)
                p6_fall_ms = scope.meas('P6','out',1000)
                scope.meas('P6','out',1000)
                #p6_fall_ms = p6_fall*1000
                p5_base = scope.meas('P5','out')
                write_to_csv(device.folder_name_path, 9 + exceloffset, [f'{p6_fall_ms}ms',f'{p5_base}',f'{device.folder_name_path}\\{filename}.png'],'Turn_on_off')

            def falling_zoom():
                filename = f'Turn-Off_{test_name}_Zoom'
                scope.screenshot(device.folder_name_path,filename)

                p6_fall_ms = scope.meas('P6','out',1000)
                #p6_fall_ms = p6_fall*1000
                p5_base = scope.meas('P5','out')
                write_to_csv(device.folder_name_path, 10 + exceloffset, [f'{p6_fall_ms}ms',f'{p5_base}',f'{device.folder_name_path}\\{filename}.png'],'Turn_on_off')
               

            scope.WAIT(120)
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
    scope.timeScale(2)
    #scope.setTrigger('C3', 'NEG', 0.9)
    scope.setTrigger('C4','NEG',device.output_voltage_nom/2)
    scope.setParam('P5','C4','BASE')

    load.output(False)
    supply.output(True)
    time.sleep(5) #Specified pause

    scope.trigMode('SINGLE')
    time.sleep(10)
    set_wait(True)
    set_skip(True)
    test_text = 'For Power-Button test, hit "Continue" after power button has been pressed. To skip, hit "Skip" '
    listener(popup_button1, popup_button2, 'enabled', popup_label, test_text, testing_progressbar)

    if not get_skip():
        turnoff_main('ACOnly')
    else:
        turnoff_main('Button')
