import pyvisa
import time

'''
NOTES:

This file handles all functions directly related to the insturments.

This was done to abstract the controls from the actual commands, in case other equipment have different command structures

If a new piece of equipment is used, the ID will need to be added to the name parameter if the commands are the same. Or new command structure added


list_equipment: Lists all connected equipment and returns a list of the Alias (This is what the "name_ID" parameters see), and the resource_list which has the connection information

initlaize_equipment: Starts resource manager and connects to the selected load supply and scopes


supply: Houses all commands to communicate with the DC supply

load: Houses all commands to communicate with the DC load (This is most likely to need additonal commands for other loads used)

scope: Houses all general commands for the scope that do not interact with a specific channel

scope_chan: interfaces with the C1-C4, and occasionaly the P1-P8 measurement channels

scope_screenshot: Takes a picture of the scope screen and saves it to the filepath

capture_Waveforms: Sets scope to auto trigger, and waits to stop until it has obtained he required number of captures

close_equipment: Closes the instruments and instrument manager, best practice to avoid errors

'''

#Arbitrary value such that load does not read the voltage/current before it has changed
supply_load_meas_delay = 0.1


def list_equipment():
    """

    Lists all connected ports & equipment

    Return:
       list of equipment IDs for connection.

       list of equipment alias for ease of human reading.

    """


    global rm
    rm = pyvisa.ResourceManager()
    resource_array = rm.list_resources()

    resource_list = []
    resource_alias_list = []

    for x in resource_array:
        counter = resource_array.index(x)
        resource_info = rm.resource_info(resource_array[counter])
        #print(resource_info.alias)
        resource_list.append(resource_info.resource_name)
        resource_alias_list.append(resource_info.alias)
        #print(f'Equipment {counter}: {resource_info.alias}')
    
    rm.close()
    
    return resource_list, resource_alias_list


    




def initialize_equipment(load_id:str,supply_id:str,scope_id:str):
    """
    
    Connects to specified load, supply, and scope

    Parameters:
        load_id (str): Manufacturer name of the load. 
        supply_id (str): Manufacturer name of the supply. 
        scope_id (str): Manufacturer name of the scope. 

    """
    global rm
    rm = pyvisa.ResourceManager()
    
        
    global Load
    #Load = rm.open_resource('USB0::0x0A69::0x0880::630041500253::INSTR')
    Load = rm.open_resource(f'{load_id}')
    Loadname_string=str(Load.query('*IDN?'))
    Loadname_array=Loadname_string.split(',')
    global Supply
    #Supply = rm.open_resource('USB0::0x2EC7::0x9200::800886011777110059::INSTR')
    Supply = rm.open_resource(f'{supply_id}')
    #print(Supply.query('IDN?'))
    Supplyname_string=str(Supply.query('*IDN?'))
    Supplyname_array=Supplyname_string.split(',')
    global Scope
    #Scope = rm.open_resource('TCPIP0::10.10.11.76::inst0::INSTR')
    #Scope = rm.open_resource(f'{scope_id}', write_termination='\n', read_termination='\n')
    Scope = rm.open_resource(f'{scope_id}')
    Scope.timeout = 100000
    Scope.clear()
    Scopename_string=str(Scope.query('*IDN?'))
    Scopename_array=Scopename_string.split(',')

    #Ensures that scope messages are in shortest possible return
    Scope.write('COMM_HEADER OFF')

    return Loadname_array, Supplyname_array, Scopename_array




#Operations: OUTP, VOLT, CURR, MEAS
def supply(supply_name:str,operation:str,value):
    """
    
    Sends commands to the designated DC power supply

    Parameters:
        supply_name (str): MFG name of supply
        operation (str): Desired operation. All operations can be seen below
        value: Can be any value, command parses to string. See valid values for each operation

    """

    generic_supply_names = [' 9205B', ' 9202B']

    if supply_name in generic_supply_names:
        match operation:
            case str(operation) if 'OUT' in operation:
                #Turns output of supply on or off
                #value: 'ON', 'OFF'
                Supply.write(f'OUTP {value}')
            case str(operation) if 'VOLT' in operation:
                #Changes voltage level of supply
                #value: Any integer or double
                Supply.write(f'VOLT {value}')
            case str(operation) if 'CURR' in operation:
                #Changes current limit of supply
                #value: Any integer or double
                Supply.write(f'CURR {value}')
            case str(operation) if 'MEAS' in operation:
                #Takes measurement of current or voltage on supply
                #value: 'VOLT','CURR'
                time.sleep(supply_load_meas_delay)  #Delays measurment until it has had time to propogate
                output = Supply.query(f'MEAS:{value}?')
                return float(output)
            case _:
                print('Unknown Supply Command')
    else:
        raise Exception('Unknown DC Supply. Check that equipment is chosen correctly, or contact Kate H to add new equipment')





def load(load_name:str,operation:str,value):
    """
    
    Sends commands to the designated DC load

    Parameters:
        load_name (str): MFG name of load
        operation (str): Desired operation. All operations can be seen below
        value: Can be any value, command parses to string. See valid values for each operation

    """
    generic_load_names = ['63004-150-60']

    if load_name in generic_load_names:
        match operation:
            case str(operation) if 'OUT' in operation:
                #Turns load on or off
                #Value: 'ON','OFF'
                Load.write(f'LOAD {value}')
            case str(operation) if 'CURR' in operation:
                #Sets current limit of load
                #Value: Any integer or double
                Load.write(f'CURR:STAT:L1 {value}')
            case str(operation) if 'RESIST' in operation:
                #Sets resistance limit of load
                #Value: Any integer or double
                Load.write(f'RESISTANCE:STAT:L1 {value}')
            case str(operation) if 'MEAS' in operation:
                #Measures voltage or current of load
                #Value: 'VOLT','CURR'
                time.sleep(supply_load_meas_delay)  #Delays measurement such that command propogates before measurement taken
                output = Load.query(f'MEAS:{value}?')
                return float(output)
            case str(operation) if "MODE" in operation:
                #Sets mode of load. CC is current control. 
                #Value: 'CCH','CCL', 'CCDH', 'CCDL'. More on Chroma datasheet
                Load.write(f'MODE {value}')
            case str(operation) if "VRANGE" in operation:
                #Sets voltage range of load
                #Value: 'H','M','L'
                Load.write(f'CONF:VOLT:RANGE {value}')
            case str(operation) if "L1" in operation:
                #Sets Current value of L1, in dynamic mode
                #Value: Any integer or double
                Load.write(f'CURR:DYN:L1 {value}')
            case str(operation) if "L2" in operation:
                #Sets Current value of L2, in dynamic mode
                #Value: Any integer or double
                Load.write(f'CURR:DYN:L2 {value}')
            case str(operation) if "T1" in operation:
                #Sets time value of T1, in dynamic mode
                #Value: String, with 'ms' at the end works best. Technically any value
                Load.write(f'CURR:DYN:T1 {value}')
            case str(operation) if "T2" in operation:
                #Sets time value of T2, in dynamic mode
                #Value: String, with 'ms' at the end works best. Technically any value
                Load.write(f'CURR:DYN:T2 {value}')
            case str(operation) if "REPEAT" in operation:
                #Number of times to repeat in dynamic mode. 0 is infinite
                #Value: '0','1' 
                Load.write(f'CURR:DYN:REP {value}')
            case str(operation) if "RISE" in operation:
                #Sets slew rate up
                #Value: 'MAX', 'MIN', or any integer or double
                Load.write(f'CURR:DYN:RISE {value}')
            case str(operation) if "FALL" in operation:
                #Sets slew rate down
                #Value: 'MAX', 'MIN', or any integer or double
                Load.write(f'CURR:DYN:FALL {value}')
            case str(operation) if "POWER" in operation:
                #Gets the max power of the load in watts
                #Value: 'MAX', 'MIN', or any integer or double
                Load.write(f'MODE CPH')
                output = Load.query(f'POW:STAT:L1? MAX')
                return float(output)
            case _:
                print('Unknown Load Command')
    else:
        raise Exception('Unknown DC Load. Check that equipment is chosen correctly, or contact Kate H to add new equipment')



def scope(scope_name:str,operation:str,value=None):
    """
    
    Sends general commands to the designated oscilloscope

    Parameters:
        scopename (str): MFG name of scope
        operation (str): Desired operation. All operations can be seen below
        value: Can be any value, command parses to string. See valid values for each operation

    """

    generic_scope_names = ['HDO6104A', 'WS4104HD']

    if scope_name in generic_scope_names:
        match operation:
            case str(operation) if "TRIGMODE" in operation:
                #Sets trigger mode for captures
                #value: 'STOP', 'AUTO', 'SINGLE', 'NORMAL'
                Scope.write(f'TRIG_MODE {value}')
                Scope.query('*OPC?')
            case str(operation) if "RECALL" in operation:
                #Recalls a specific setup
                #value: Integer,, from 1 to 6
                Scope.write(f'*RCL {value}')
                Scope.query('*OPC?')
            case str(operation) if "MEM" in operation:
                #Defines memory used for captures
                #value: 'MAX', or large integer
                Scope.write(f'MSIZ {value}')
            case str(operation) if "FORCE" in operation:
                #Forces trigger mode for captures
                #value: 'STOP', 'AUTO', 'SINGLE', 'NORMAL'
                Scope.write('CLEAR_SWEEPS') #Scope.write(r"""vbs 'app.measure.clearsweeps ' """) #Alternative command
                Scope.query('*OPC?')
                Scope.write(f'TRMD {value};ARM;FRTR')
                Scope.query('*OPC?')
            case str(operation) if "ARM" in operation:
                #Takes a single capture
                Scope.write('ARM')
                Scope.query('*OPC?')
            case str(operation) if "STOP" in operation:
                #Stops the current capture, if mode is in AUTO or NORMAL
                Scope.write('STOP')
            case str(operation) if "CLEAR" in operation:
                #Clears all sweep data
                Scope.write('CLEAR_SWEEPS') #Scope.write(r"""vbs 'app.measure.clearsweeps ' """) #Alternative command
                Scope.query('*OPC?')
            case str(operation) if "TDIV" in operation:
                #Sets horizontal timescale
                #String, with 'ms' at the end works best. Technically any value. 5us, 2ms, 1s, etc
                Scope.write(f'TDIV {value}')
                Scope.query('*OPC?')
            case str(operation) if "TRIGDELAY" in operation:
                #Sets trigger delay in time
                #String, with 'ms' at the end works best. Technically any value. 5us, 2ms, 1s, etc. Negatives are possible
                Scope.write(f'TRIG_DELAY {value}')
                Scope.query('*OPC?')
            case str(operation) if "OPC" in operation:
                #Returns only when last command is complete. Or timeout ocurs
                Scope.query('*OPC?')
            case str(operation) if "AUTOSETUP" in operation:
                #Auto-sets up the scope. Then waits. Built-in
                Scope.write('C1:ASET')
                Scope.query('*OPC?')
                Scope.write('C2:ASET')
                Scope.query('*OPC?')
                Scope.write('C3:ASET')
                Scope.query('*OPC?')
                Scope.write('C4:ASET')
                Scope.query('*OPC?')
            case str(operation) if "SAMPLERATEMAX" in operation:
                #Sets the samplerate of catures to the maximum. No specific setting is available
                Scope.write("vbs 'app.acquisition.horizontal.maximize =\"FixedSampleRate\"'")
            case str(operation) if "PERSIST" in operation:
                #Sets scope to persist, or not
                #value: 'TRUE', 'FALSE'
                Scope.write(f"vbs 'app.Display.Persisted = {value}'")
            case str(operation) if "PASSFAIL" in operation:
                #Sets number of sweeps for pass/fail mode, then runs
                #value: Large integer
                Scope.write(f'PASS_FAIL ON,ALLQ1TOQ4ORALLQ5TOQ8,{value}')
            case _:
                print('Unknown Scope Command')
    else:
        raise Exception('Unknown Scope. Check that equipment is chosen correctly, or contact Kate H to add new equipment')




def scope_chan(scope_name:str,channel:str,operation:str,value=None, mult = float(1)):
    """
    
    Sends commands to individual channels of oscilloscope

    Parameters:
        scopename (str): MFG name of scope
        channel (str): Desired channel. C1-C4, sometimes P1-P8 depending on operation
        operation (str): Desired operation. All operations can be seen below
        value: Can be any value, command parses to string. See valid values for each operation

    """
    generic_scope_names = ['HDO6104A', 'WS4104HD']

    if scope_name in generic_scope_names:
        match operation:
            case str(operation) if "ATTEN" in operation:
                #Sets attenuation of channel. Only can be changed for channels with BNC, otherwise is automatic
                #channel: C1-C4
                #value: Doulbe or integer
                Scope.write(f'{channel}:ATTENUATION {value}')
            case str(operation) if "BANDWIDTH" in operation:
                #Sets bandwidth limit of probe/channel
                #channel: C1-C4
                #value: 'OFF', '20MHz'
                Scope.write(f'BWL {channel},{value}')
            case str(operation) if "VOFFSET" in operation:
                #Sets vertical offset
                #channel: C1-C4
                #value: Doulbe or integer. Can add 'mv" after if desired.'0.5V', '500mV', etc
                Scope.write(f'{channel}:OFFSET {value}')
            case str(operation) if "TRIGLEVEL" in operation:
                #Sets vertical level of trigger
                #channel: C1-C4
                #value: Doulbe or integer. Can add 'mv" after if desired.'0.5V', '500mV', etc
                Scope.write(f'{channel}:TRIG_LEVEL {value}')
            case str(operation) if "TRIGCHANNEL" in operation:
                #Sets trigger channel, and slope
                #channel: C1-C4
                #value: 'POS','NEG'
                Scope.write(f'TRIG_SELECT EDGE,SR,{channel}')
                Scope.write(f'{channel}:TRIG_SLOPE {value}')
                Scope.query('*OPC?')
            case str(operation) if "VDIV" in operation:
                #Sets vertical scale
                #channel: C1-C4
                #value: Doulbe or integer. Can add 'mv' after if desired.'0.5V', '500mV', etc
                Scope.write(f'{channel}:VOLT_DIV {value}')
                Scope.query('*OPC?')
            case str(operation) if "TRACETOGGLE" in operation:
                #turns the trace visiblility on or off
                #channel: C1-C4
                #value: 'ON', 'OFF'
                Scope.write(f'{channel}:TRACE {value}')
                Scope.query('*OPC?')
            case str(operation) if "MEAS" in operation:
                #Measures and returns specific value of measurement channel
                #channel: P1-P8
                #value: 'out','mean','min','max','sdev','num'
                Scope.query('*OPC?')
                meas_out = mult * float(Scope.query((rf"""vbs? 'return=app.measure.{channel}.{value}.result.value' """)))

                meas_out_round = round(meas_out,3)
                return meas_out_round
            case str(operation) if "HORPOS" in operation:
                #Sets horizontal position of zoom channel
                #channel: Z1-Zn (Zoom channels)
                #value: Doulbe or integer.
                Scope.write(f'{channel}:HOR_POSITION {value}')
            case str(operation) if "HORMAG" in operation:
                #Sets horizontal magnification of zoom channel
                #channel: Z1-Zn (Zoom channels)
                #value: Doulbe or integer.
                Scope.write(f'{channel}:HOR_MAGNIFY {value}')
            case str(operation) if "VERTPOS" in operation:
                #Sets verticall position of zoom channel
                #channel: Z1-Zn (Zoom channels)
                #value: Doulbe or integer.
                Scope.write(f'{channel}:VERT_POSITION {value}')
            case str(operation) if "VERTMAG" in operation:
                #Sets vertical magnification of zoom channel
                #channel: Z1-Zn (Zoom channels)
                #value: Doulbe or integer.
                Scope.write(f'{channel}:VERT_MAGNIFY {value}')

            case str(operation) if "UNIT" in operation:
                #Changes unit of channel (MAY NOT WORK)
                #channel: C1-C4
                #Scope.write((rf"""vbs? 'app.Acquisition.{channel}.Unit = "OTHER"' """))
                #Scope.write((rf"""vbs? 'app.Acquisition.{channel}.Type = "ELECTRICAL"' """))
                #Scope.write((rf"""vbs? 'app.Acquisition.{channel}.Units = "AMPERE"' """))

                Scope.write(f'{channel}:UNIT {value}')

                #print('amps')
                #Scope.write((rf'app.Acquisition.{channel}.Unit = "OTHER"'))
                #Scope.write((rf'app.Acquisition.{channel}.Type = "ELECTRICAL"'))
                #Scope.write((rf'app.Acquisition.{channel}.Units = "AMPERE"'))
            case str(operation) if "PARAMFIX" in operation:
                #Fixes parameter 1 and 2 in deadtime test
                Scope.write('PARAMETER_CUSTOM 1,SKEW,C3,NEG,50 PCT,F1,POS,50 PCT')
                Scope.write('PARAMETER_CUSTOM 2,SKEW,F1,NEG,50 PCT,C3,POS,50 PCT')
                Scope.query('*OPC?')
            case str(operation) if "CHANGEP5" in operation:
                #Sets measurement channel parameters
                #channel: C1-C4
                #value: 'TOP', 'MAX', etc
                Scope.write(f'PARAMETER_CUSTOM 5,{value},{channel}')
                Scope.query('*OPC?')
            case _:
                print('Unknown Scope Channel Command')
    else:
        raise Exception('Unknown Scope. Check that equipment is chosen correctly, or contact Kate H to add new equipment')



def scope_screenshot(filepath:str,filename:str):
    """
    
    Causes the scope to take a screenshot of whatever is on screen, and then saves the image

    Parameters:
        filepath (str): Where to save the image
        filename (str): The name of the image when saved

    """
    Scope.write('STOP')
    Scope.query('*OPC?')
    
    Scope.write(r'HARDCOPY_SETUP DEV,PNG,FORMAT,LANDSCAPE,BCKG,Std,DEST,REMOTE,DIR,"C:\\USERS\\LECROYUSER\\",FILE,"SCREEN--00000.PNG",AREA,DSOWINDOW,PRINTER,"MICROSOFTXPSDOCUMENTWRITER"')

    Scope.write('SCDP')

    result_str=Scope.read_raw()

    f=open(f'{filepath}\\{filename}.png','wb')
    f.write(result_str)
    f.flush()
    f.close()


def capture_waveforms(Scope_ID:str,channel:str,numwaveforms:int, test_text, popup_label):
    """
    
    Causes scope to take a set number of captures, based on a specific measurement channel

    Parameters:
        Scope_ID (str): MFG name of scope
        channel (str): Channel to check number of waveforms captured. Must be P1-P8
        numwaveforms (int): Number of waveforms to capture

    """

    #Must be a P measurement channel
    scope(Scope_ID, 'CLEAR')
    scope(Scope_ID, 'OPC')

    scope(Scope_ID, 'TRIGMODE','AUTO')
    #scope(Scope_ID, 'ARM')
    while(int(scope_chan(Scope_ID,channel,'MEAS','num')) <= numwaveforms):
        time.sleep(0.4) #slight delay so loop doesn't run all the time
        current_waveform = int(scope_chan(Scope_ID,channel,'MEAS','num'))
        new_text = test_text + f' \n {current_waveform} / {numwaveforms} Waveforms'
        popup_label.config(text = new_text)

    scope(Scope_ID,'STOP')
    scope(Scope_ID, 'OPC')
    popup_label.config(text = test_text)



def close_equipment(): 
    """
    
    Closes out all remote equipment, and resouce manager

    """
    try:
        Load.write(f'MODE CCH')
        Load.write(f'CURR:STAT:L1 0.1')
        Load.write(f'LOAD ON')
        Supply.write(f'OUTP OFF')
        Supply.close()
        Load.close()
        Scope.close()
        
    except  Exception as e:
        exit

    try:
        rm.close()
    except Exception as e:
        exit