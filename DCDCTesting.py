from EquipmentFuncs import *
from Tests import *

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




#Main DC testing function. Gets inputs via the DC DC Gui. Set parameters above for debug purposes
def DCDC_main(window, start_test_button, popup_label, popup_button1, popup_button2, testing_progressbar, LDO_bool, SWM_bool, EFF_bool, DEA_bool, TRN_bool, scope_pos, supply_pos, load_pos, min_load_bool, tdc_load_bool, max_load_bool, transient_load_bool, device_name, extfets_bool, input_voltage, supply_voltage, output_voltage_max, output_voltage_nom, iout_max, iout_nom, fsw, resource_list):
    """
    
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

        
    """
   



    try:

        #Grab IDs of the equipment
        Loadname_array, Supplyname_array, Scopename_array = initialize_equipment(resource_list[load_pos], resource_list[supply_pos], resource_list[scope_pos])
        Load_ID = Loadname_array[1]
        Supply_ID = Supplyname_array[1]
        Scope_ID = Scopename_array[1]




        #ensure supply is off, then set base parameters
        supply_current_limit = round(1 + (output_voltage_max*iout_max)/(0.7*input_voltage))


        if supply_voltage != input_voltage:
            supply_current_limit = 'MAX'

        supply(Supply_ID, 'OUT', 'OFF')
        supply(Supply_ID, 'CURR', supply_current_limit)
        supply(Supply_ID, 'VOLT', supply_voltage)    



        #Create folder in current python path
        folder_name_path, python_path = create_folder(supply_voltage, device_name)


        #Sets up and prints the test_Conditions file. This could probably be changed over to the "copy and move" file function created later
        test_conditions = []
        test_conditions.append('Regulator Name')
        test_conditions.append(f'{device_name}')
        test_conditions.append('Nominal Vout')
        test_conditions.append(f'{output_voltage_nom}')
        test_conditions.append('Nominal Vin')
        test_conditions.append(f'{input_voltage}')
        test_conditions.append('ICCmax')
        test_conditions.append(f'{iout_max}')
        test_conditions.append('ICC TDC')
        test_conditions.append(f'{iout_nom}')
        test_conditions.append('Transient Current')
        test_conditions.append(f'{iout_nom/2}')
        test_conditions.append('Transient Slew Rate')
        test_conditions.append('3')
        test_conditions.append('Switching Frequency khz (Design)')
        test_conditions.append(f'{fsw/1000}')

        with open(f'{folder_name_path}\\test_conditions.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for line in test_conditions:
                writer.writerow([line])
            csvfile.close()


        #Copies the rest of the CSV files
        copy_csv(python_path,folder_name_path,'Results')
        copy_csv(python_path,folder_name_path,'deadtime')
        copy_csv(python_path,folder_name_path,'Turn_on_off')



        #Create current testing points list
        current_testing_list = []
        current_testing_list_bool = [min_load_bool, tdc_load_bool, max_load_bool]

        for index, value in enumerate(current_testing_list_bool):
            if value and index == 0:
                current_testing_list.append('min')
            elif value and index == 1:
                current_testing_list.append('tdc')
            elif value and index == 2:
                current_testing_list.append('max')
            else:
                continue
        


        test_list = [EFF_bool, LDO_bool, SWM_bool, DEA_bool, TRN_bool]
    
        
        for test_count, test_value in enumerate(test_list):
            supply(Supply_ID,'OUT','OFF')
            if test_value:
                if test_count == 0:
                    test_eff(window, popup_label, popup_button1, popup_button2, testing_progressbar, Scope_ID, Load_ID, Supply_ID,iout_max,iout_nom)

                elif test_count == 1:
                    jitter_bool = False
                    #test_ripple_jitter(window, popup_label, popup_button1, popup_button2, testing_progressbar, Scope_ID, Supply_ID, Load_ID, fsw, iout_nom, iout_max, folder_name_path, current_testing_list,input_voltage, jitter_bool)
                    if transient_load_bool:
                        test_transient(window, popup_label, popup_button1, popup_button2, testing_progressbar, Scope_ID, Supply_ID, Load_ID, iout_nom, iout_max, folder_name_path)
                    test_overcurrent(window, popup_label, popup_button1, popup_button2, testing_progressbar, Scope_ID, Supply_ID, Load_ID, iout_max, folder_name_path, output_voltage_nom)
                    supply(Supply_ID, 'CURR', supply_current_limit) #Resets current of supply
                    supply(Supply_ID,'OUT','OFF')
                    load(Load_ID, 'CURR','0.5')
                    load(Load_ID, 'OUT','ON') #discharges any remaining voltage from supply
                elif test_count == 2:
                    jitter_bool = True
                    test_ripple_jitter(window, popup_label, popup_button1, popup_button2, testing_progressbar, Scope_ID, Supply_ID, Load_ID, fsw, iout_nom, iout_max, folder_name_path, current_testing_list,input_voltage, jitter_bool)
                    if transient_load_bool:
                        test_transient(window, popup_label, popup_button1, popup_button2, testing_progressbar, Scope_ID, Supply_ID, Load_ID, iout_nom, iout_max, folder_name_path)
                    test_overcurrent(window, popup_label, popup_button1, popup_button2, testing_progressbar, Scope_ID, Supply_ID, Load_ID, iout_max, folder_name_path, output_voltage_nom)
                    supply(Supply_ID, 'CURR', supply_current_limit) #Resets current of supply
                    test_vds(window, popup_label, popup_button1, popup_button2, testing_progressbar, Scope_ID, Supply_ID, Load_ID, iout_nom, folder_name_path, current_testing_list, input_voltage, extfets_bool, transient_load_bool)
                    supply(Supply_ID,'OUT','OFF')
                    load(Load_ID, 'CURR','0.5')
                    load(Load_ID, 'OUT','ON') #discharges any remaining voltage from supply
                elif test_count == 3:
                    supply(Supply_ID,'OUT','OFF')
                    test_deadtime(window, popup_label, popup_button1, popup_button2, testing_progressbar, Scope_ID, Supply_ID, Load_ID, iout_nom, folder_name_path, current_testing_list, input_voltage, output_voltage_nom, fsw, transient_load_bool)
                    supply(Supply_ID,'OUT','OFF')
                    load(Load_ID, 'CURR','0.5')
                    load(Load_ID, 'OUT','ON') #discharges any remaining voltage from supply
                elif test_count == 4: 
                    supply(Supply_ID,'OUT','OFF')
                    test_turnonoff(window, popup_label, popup_button1, popup_button2, testing_progressbar, Scope_ID, Supply_ID, Load_ID, iout_nom, folder_name_path, current_testing_list, input_voltage, output_voltage_nom)
                    supply(Supply_ID,'OUT','OFF')
                    load(Load_ID, 'CURR','0.5')
                    load(Load_ID, 'OUT','ON') #discharges any remaining voltage from supply
                else:
                    continue      
            else:
                continue
        
        window.quit()
        close_equipment()


    
    except Exception as e:
        popup_label.config(text = f'Whoops! Error in DCDC Testing: \n {e}')
        popup_label.config(background = 'red')
        start_test_button.config(state = 'enabled') 
    
        close_equipment()



#Runs the function, if debugging
#DCDC_main(LDO_bool, SWM_bool, EFF_bool, DEA_bool, TRN_bool, scope_pos, supply_pos, load_pos, min_load_bool, tdc_load_bool, max_load_bool, transient_load_bool, device_name, extfets_bool, input_voltage, output_voltage_max, output_voltage_nom, iout_max, iout_nom, fsw, resource_list)

