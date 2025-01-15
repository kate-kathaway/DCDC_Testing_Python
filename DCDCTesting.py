from Tests import *
from EquipmentClasses import *
import pyvisa

'''
NOTES:

This file houses the initial setup for testing, including creating files and folders
After that, it will then call indiviudal functions from the Tests.py file to run required tests for options selected

This file COULD be run without the GUI for testing purposes. All varables are commented out below

'''


#In order to run debug, uncomment the below variables, and uncomment the function at the end of the file

'''
LDO_bool = False
SWM_bool = True
EFF_bool = True
DEA_bool = False
TRN_bool = False
scope_pos = 2
supply_pos = 0
load_pos = 1
min_load_bool = False
tdc_load_bool = True
max_load_bool = True
transient_load_bool = True
device_name = 'Device Name'
extfets_bool = True
input_voltage = 24.0
output_voltage_max = 21.0
output_voltage_nom = 22.05
iout_max = 6.0
iout_nom = 3.0
fsw = 245000.0

resource_list, resource_alias_list_unused = list_equipment()
'''





#print(scope.alias)


#scope.trigMode('SINGLE')


#test_scope.autoSetup()

#test_scope.setupChannel('C1', float(3.3*1.02), float(3.3*0.98))


#supply.output(True)
#time.sleep(5)


#print(test_supply.alias)
#print(test_load.alias)
#close_equipment()




#Main DC testing function. Gets inputs via the DC DC Gui. Set parameters above for debug purposes
def DCDC_main(window, error_log, start_test_button, popup_label, popup_button1, popup_button2, testing_progressbar, scope_connection_ID:str, supply_connection_ID:str, load_connection_ID:str, device:DUT):
    '''
    The main function to select the proper tests from Tests.py for the selected options by user from the GUI. Could be run indeendently for debug purposes

    Parameters:
        LDO_bool (bool): True if user wants to perform all Low-dropout tests
        SWM_bool (bool): True if user wants to perform all swtich mode regulator tests
        EFF_bool (bool): True if user wants to perform efficiency test
        DEA_bool (bool): True if user wants to perform deadtime test
        TRN_bool (bool): True if user wants to perform turn on / turn off tests
        scope_pos (int): Index position of scope in the resource list
        supply_pos (int): Index position of supply in the resource list
        load_pos (int): Index position of load in the resource list
        min_load_bool (bool): True if user wants to perform tests at minimum load
        tdc_load_bool (bool): True if user wants to perform tests at nominal load
        max_load_bool (bool): True if user wants to perform tests at maximum load
        transient_load_bool (bool): True if user wants to perform tests with a transient load
        device_name (str): Name of the device being tested, names the folder for seperating results
        exfets_bool (bool): True if there are external fets, will prompt an additonal test
        input_voltage (float): Input voltage for the DUT
        output_voltage_max (float): Maximum expected output voltage, used to set current level of the supply
        output_voltage_nom (float): Expected nominal output voltage of DUT during normal operation
        iout_max (float): The maximum current of the DUT
        iout_nom (float): Nominal current of the DUT during normal operation
        fsw (float): Switching frequency of DUT
        resource_list (list): List that holds all information for each device selected. Name, alias, manufactuer, etc

        '''


    
    try:

        #Grab IDs of the equipment
        #Loadname_array, Supplyname_array, Scopename_array = initialize_equipment(resource_list[load_pos], resource_list[supply_pos], resource_list[scope_pos])
        #Load_ID = Loadname_array[1]
        #Supply_ID = Supplyname_array[1]
        #Scope_ID = Scopename_array[1]




        scope, supply, load = initialize_equipment(scope_connection_ID, supply_connection_ID, load_connection_ID)


        supply.output(False)
        supply.setCurrent(device.getSupplyCurrent())
        supply.setVoltage(device.supply_input_voltage)

        #Create folder in current python path
        device.folder_name_path, device.python_path = create_folder(device.supply_input_voltage, device.name, device)


        #Sets up and prints the test_Conditions file. This could probably be changed over to the "copy and move" file function created later
        test_conditions = []
        test_conditions.append('Regulator Name')
        test_conditions.append(f'{device.name}')
        test_conditions.append('Nominal Vout')
        test_conditions.append(f'{device.output_voltage_nom}')
        test_conditions.append('Nominal Vin')
        test_conditions.append(f'{device.device_input_voltage}')
        test_conditions.append('ICCmax')
        test_conditions.append(f'{device.output_current_max}')
        test_conditions.append('ICC TDC')
        test_conditions.append(f'{device.output_current_nom}')
        test_conditions.append('Transient Current')
        test_conditions.append(f'{device.output_current_nom/2}')
        test_conditions.append('Transient Slew Rate')
        test_conditions.append('3')
        test_conditions.append('Switching Frequency khz (Design)')
        test_conditions.append(f'{device.frequency/1000}')

        with open(f'{device.folder_name_path}\\test_conditions.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for line in test_conditions:
                writer.writerow([line])
            csvfile.close()


        #Copies the rest of the CSV files
        copy_csv(device.python_path,device.folder_name_path,'Results')
        copy_csv(device.python_path,device.folder_name_path,'deadtime')
        copy_csv(device.python_path,device.folder_name_path,'Turn_on_off')





        #Eff, RippleJitter, Transient, Overcurrent, VDS, Deadtime, Turnon-off

        for test_count, test_value in enumerate(device.test_list):
            supply.output(False)
            if test_value:
                if test_count == 0:
                    test_eff(error_log, popup_label, popup_button1, popup_button2, testing_progressbar, scope, supply, load, device)
                    discharge(device)
                elif test_count == 1:
                    test_ripple_jitter(popup_label, popup_button1, popup_button2, testing_progressbar, scope, supply, load, device)
                    discharge(device)
                elif test_count == 2:
                    if 'transient' in device.load_list:
                        test_transient(popup_label, popup_button1, popup_button2, testing_progressbar, scope, supply, load, device)
                    discharge(device)
                elif test_count == 3:
                    test_overcurrent(popup_label, popup_button1, popup_button2, testing_progressbar, scope, supply, load, device)
                    discharge(device)
                elif test_count == 4:
                    test_vds(popup_label, popup_button1, popup_button2, testing_progressbar, scope, supply, load, device)
                    discharge(device)
                elif test_count == 5:
                    test_deadtime(popup_label, popup_button1, popup_button2, testing_progressbar, scope, supply, load, device)
                    discharge(device)
                elif test_count == 6: 
                    test_turnonoff(popup_label, popup_button1, popup_button2, testing_progressbar, scope, supply, load, device)
                    discharge(device)
                else:
                    continue      
            else:
                continue
        window.quit()
        close_equipment()


    
    except Exception as e:
        start_test_button.config(state = 'enabled')
        popup_label.config(background = 'red')
        discharge(device)
        error_update(error_log, e)
        #raise Exception('Error in DC DC Testing Main Script')



#Runs the function, if debugging
#DCDC_main(LDO_bool, SWM_bool, EFF_bool, DEA_bool, TRN_bool, scope_pos, supply_pos, load_pos, min_load_bool, tdc_load_bool, max_load_bool, transient_load_bool, device_name, extfets_bool, input_voltage, output_voltage_max, output_voltage_nom, iout_max, iout_nom, fsw, resource_list)

