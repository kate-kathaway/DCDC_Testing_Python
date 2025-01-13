import pyvisa
import time

def list_equipment():
    """
    Lists all connected ports & equipment

    Return:
       resource_list: list of equipment IDs for connection.

       resource_alias_list: list of equipment alias for ease of human reading.
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

def initialize_equipment(scope_id:str,supply_id:str,load_id:str):
    """
    Connects to specified load, supply, and scope

    Parameters:
        load_id: Manufacturer name of the load. 
        supply_id: Manufacturer name of the supply. 
        scope_id: Manufacturer name of the scope. 

    Return:
        scope: SCOPE class object
        supply: SUPPLY class object
        load: LOAD class object
    """
    global rm
    rm = pyvisa.ResourceManager()

    global scope
    global supply
    global load
    scope = SCOPE(rm, scope_id)
    supply = SUPPLY(rm, supply_id)
    load = LOAD(rm, load_id)

    return scope, supply, load


class SCOPE:
    def __init__(self, rm, connection_ID, timeout_ms = 30000):
        """
        Creates a SCOPE object. For remote control of oscilloscopes

        Parameters:
            rm: Pyvisa resource manager object
            connection_ID: String that contains the resource connection for the scope
            timeout+_ms: Number of millise3conds until scope times out and throws an error. 30sec by default
        """
        self.instr = rm.open_resource(connection_ID)

        generic_scope = ['HDO6104A', 'WS4104HD']

        #instr = rm.open_resource(connection_ID)
        self.instr.timeout = timeout_ms
        self.instr.clear()

        self.array = str(self.instr.query('*IDN?')).split(',')

        self.alias = self.array[1]

        self.instr.write('COMM_HEADER OFF')#Ensures that scope messages are in shortest possible return
        self.instr.write(r'HARDCOPY_SETUP DEV,PNG,FORMAT,LANDSCAPE,BCKG,Std,DEST,REMOTE,DIR,"C:\\USERS\\LECROYUSER\\",FILE,"SCREEN--00000.PNG",AREA,DSOWINDOW,PRINTER,"MICROSOFTXPSDOCUMENTWRITER"')


        self.generic = False
        if self.alias in generic_scope:
            self.generic = True


    def __write(self, string:str):
        '''
        Internal command. Writes to the instrument

        Parameters:
            string: Any string, will be written directly to the instrument
        '''
        self.instr.write(string)
    
    def __query(self, string:str):
        '''
        Internal command. Asks for data from the instrument, and returns it

        Parameters:
            string: Any string, will be written directly to the instrument
        '''
        out = self.instr.query(string)
        return out
    

    def OPC(self):
        '''
        Completes if scope has executed all commands
        '''
        #This way we can do a listen command IF needed
        self.__query('*OPC?')

    def WAIT(self, timeout:int = 20):
        '''
        Tells the scope to wait until trigger is complete

        Parameters:
            timeout: Timeout in seconds, scope will wait until the timeout then continue
        '''
        self.__write(f'WAIT {timeout}')
        self.OPC()
        
    def clearSweeps(self):
        """
        Clears all sweep data
        """
        self.__write('CLEAR_SWEEPS') #Scope.write(r"""vbs 'app.measure.clearsweeps ' """) #Alternative command
        self.OPC()

    def trigMode(self, mode:str):
        '''
        Sets the trigger mode of the scope

        Parameters:
            mode: 'STOP', 'AUTO', 'SINGLE', 'NORMAL'
        '''
        self.__write(f'TRIG_MODE {mode}')
        self.OPC()

    def recall(self, recall_num:int):
        '''
        Recalls the specified setup, and changes some channel settings to fix DC DC testing setups

        Parameters:
            recall_num: 1-6, which specific setup to recall
        '''
        self.__write(f'*RCL {recall_num}')
        if recall_num == 1:
            self.bandwidth('C1', '20MHz')
            self.bandwidth('C2', '20MHz')
            self.attenuation('C3', '6.03')
        elif recall_num == 2:
            self.bandwidth('C1', '20MHz')
        elif recall_num == 4:
            scope.setParamSkew('P1','C3', 'NEG',50,'F1','POS',50)
            scope.setParamSkew('P2','F1', 'NEG',50,'C3','POS',50)
        self.OPC()

    def memorySize(self, memory_size:str):
        '''
        Changes the capture memory size. Does not always work

        Parameters:
            memory_size: Size of memory. Can enter with "MS" at the end
        '''
        self.__write(f'MSIZ {memory_size}')
        self.OPC()

    def forceCapture(self):
        '''
        Forces a single capture, and waits until the capture is complete
        '''
        self.__write('TRMD SiNGLE;ARM;FRTR')
        self.WAIT()
        self.OPC()

    def ARM(self):
        '''
        Arms the trigger, will trigger if called again
        '''
        self.__write('ARM')
        self.OPC()

    def STOP(self):
        '''
        Stops current aquistion
        '''
        self.__write('STOP')
        self.OPC()

    def timeScale(self, time_per_division:float|str):
        '''
        Sets horizontal timescale of all channels

        Parameters:
            time_per_division: How many seconds per division, of 10 divisions total
        '''
        self.__write(f'TDIV {time_per_division}')
        self.OPC()

    def triggerDelay(self, delay_time:float|str):
        '''
        Moves the trigger along the time axis

        Parameters:
            delay_time: Negative numbers move left, positive move right. Can enter with any "us","ms",etc at the end
        '''
        self.__write(f'TRIG_DELAY {delay_time}')
        self.OPC()

    def autoSetup(self):
        '''
        Uses autosetup command on all channels. Takes a long time
        '''
        self.__write('C1:ASET')
        self.__write('C2:ASET')
        self.__write('C3:ASET')
        self.__write('C4:ASET')
        self.OPC()

    def sampleRate(self):
        '''
        Sets the sample rate if available. As of right now, can only set to maximum
        '''
        self.__write("vbs 'app.acquisition.horizontal.maximize =\"FixedSampleRate\"'")
        self.OPC()

    def persist(self, persist_bool:bool):
        '''
        Turns persistance mode on or off

        Parameters:
            persist_bool: True is persistence is on, false if not
        '''
        self.__write(f"vbs 'app.Display.Persisted = {persist_bool}'")
        self.OPC()

    def passFail(self, sweep_num:int):
        '''
        Turns on pass-fail for DC DC testing, should limit it to the sweep number. May not fully work

        Parameters:
            sweep_num: Number of sweeps for pass-fail to run through before stopping
        '''
        self.__write(f'PASS_FAIL ON,ALLQ1TOQ4ORALLQ5TOQ8,{sweep_num}')
        self.OPC()


    #Channel specific commands
    def attenuation(self, channel_main:str, atten:float):
        '''
        Changes attenuation of selected channel

        Parameters:
           channel_main: 'C1' - 'C4'
           atten: What to set atteniuation as. If atten is 6, signal is multiplied by 6
        '''
        self.__write(f'{channel_main}:ATTENUATION {atten}')
        self.OPC()

    def bandwidth(self, channel_main:str, bw:str):
        '''
        Changes bandwidth limit of selected channel

        Parameters:
           channel_main: 'C1' - 'C4'
           bw: Sets channel bandwidth. 'OFF','20MHz','200MHz'
        '''
        self.__write(f'BWL {channel_main},{bw}')
        self.OPC()

    def offsetVert(self, channel_main:str, offset):
        '''
        Sets vertical offset for selected channel

        Parameters:
           channel_main: 'C1' - 'C4'
           offset: Number of units to offset. Negative will move the channel down, positive moves it up. If output is 12V, set offset to -12V to center
        '''
        self.__write(f'{channel_main}:OFFSET {offset}')
        self.OPC()

    def setTrigger(self, channel_main:str, slope:str, trig_level:float):
        '''
        Configures trigger for aquistion capture

        Parameters:
           channel_main: 'C1' - 'C4'
           slope: 'POS', 'NEG'
           trig_level: The level of V/A that the unit will trigger on
        '''
        self.__write(f'TRIG_SELECT EDGE,SR,{channel_main}')
        self.__write(f'{channel_main}:TRIG_SLOPE {slope}')
        self.__write(f'{channel_main}:TRIG_LEVEL {trig_level}')
        self.OPC()


    def vertScale(self, channel_main:str, units_per_division:float):
        '''
        Sets vertical scale for selected channel

        Parameters:
           channel_main: 'C1' - 'C4'
           units_per_division: How many units per division vertically, out of 8 total
        '''
        self.__write(f'{channel_main}:VOLT_DIV {units_per_division}')
        self.OPC()

    def traceToggle(self, channel_main:str, trace_bool:bool):
        '''
        Turns selected trace on or off

        Parameters:
           channel_main: 'C1' - 'C4'
           trace_bool: True if trace is turned on, False if turned off
        '''
        value = 'OFF'
        if trace_bool:
            value = 'ON'
        self.__write(f'{channel_main}:TRACE {value}')
        self.OPC()
        time.sleep(0.4)

    def meas(self, channel_meas:str, parameter:str = 'out', multiplier:int = 1):
        '''
        Turns selected trace on or off

        Parameters:
           channel_meas: 'P1' - 'P6'
           parameter: What output of measure channel to get. 'out','mean','min','max','sdev','num'
           multiplier: Multiplies the result, before rounding to 3 decimal places for readability
        '''
        meas_out = float(self.__query((rf"""vbs? 'return=app.measure.{channel_meas}.{parameter}.result.value' """)))
        meas_out_round = round(multiplier*meas_out,3)
        return meas_out_round
    
    def zoomHorDelay(self, channel_zoom:str, delay_time:float):
        '''
        Changes horizontal delay of a zoom channel

        Parameters:
           channel_zoom:  'Z1' - 'Zn'
           delay_time: How much time to delay zoom channel
        '''
        self.__write(f'{channel_zoom}:HOR_POSITION {delay_time}')
        self.OPC()

    def zoomHorMagnify(self, channel_zoom:str, magnify_value:float):
        '''
        Changes horizontal magnification of a zoom channel

        Parameters:
           channel_zoom:  'Z1' - 'Zn'
           magnify_value: Magnifies by this value. 1.0 is no magnification
        '''
        self.__write(f'{channel_zoom}:HOR_MAGNIFY {magnify_value}')
        self.OPC()

    def zoomOffsetVert(self, channel_zoom:str, offset:float):
        '''
        Changes vertical offset of zoom channel

        Parameters:
           channel_zoom:  'Z1' - 'Zn'
           offset: number of units to offset vertically
        '''
        self.__write(f'{channel_zoom}:VERT_POSITION {offset}')
        self.OPC()

    def zoomVertMagnify(self, channel_zoom:str, magnify_value:float):
        '''
        Changes vertical magnicfication of a zoom channel

        Parameters:
           channel_zoom:  'Z1' - 'Zn'
           magnify_value: Magnifies by this value. 1.0 is no magnification
        '''
        self.__write(f'{channel_zoom}:VERT_MAGNIFY {magnify_value}')
        self.OPC()

    def setUnit(self, channel_main:str, unit:str):

        raise NotImplementedError
        #Scope.write((rf"""vbs? 'app.Acquisition.{channel}.Unit = "OTHER"' """))
        #Scope.write((rf"""vbs? 'app.Acquisition.{channel}.Type = "ELECTRICAL"' """))
        #Scope.write((rf"""vbs? 'app.Acquisition.{channel}.Units = "AMPERE"' """))

        self.__write(f'{channel_main}:UNIT {unit}')

        #print('amps')
        #Scope.write((rf'app.Acquisition.{channel}.Unit = "OTHER"'))
        #Scope.write((rf'app.Acquisition.{channel}.Type = "ELECTRICAL"'))
        #Scope.write((rf'app.Acquisition.{channel}.Units = "AMPERE"'))
        self.OPC()
    
    def setParamSkew(self, channel_meas:str, channel_source_1:str, slope_1:str, trigpercent_1:int, channel_source_2:str, slope_2:str, trigpercent_2:int):
        '''
        Sets a skew parameter. Different from normal, since it is much more complicated

        Parameters:
           channel_meas: 'P1' -' P6'
           channe_source_1: Source of the first skew. 'C1' - 'C4'
           slope_1: Trigger slope for first source. 'NEG','POS'
           trigpercent_1: Trigger percent for first source. 0-100
           channe_source_2: Source of the second skew. 'C1' - 'C4'
           slope_2: Trigger slope for second source. 'NEG','POS'
           trigpercent_2: Trigger percent for second source. 0-100
        '''

        self.__write(f'PARAMETER_CUSTOM {channel_meas[1:]},SKEW,{channel_source_1},{slope_1},{trigpercent_1} PCT,{channel_source_2},{slope_2},{trigpercent_2} PCT')
        self.OPC()
        #self.write(f'PARAMETER_CUSTOM 2,SKEW,F1,NEG,50 PCT,C3,POS,50 PCT')

    def setParam(self, channel_meas:str, channel_main:str, measurement:str):
        '''
        Sets a measurement parameter

        Parameters:
           channel_meas: 'P1' - 'P6'
           channel_main: Which channel to take measurement of. 'C1' - 'C4'
           measurement: 'AMPL','AREA','BASE','DLY','DUTY','FALL','FALL82','FREQ','MAX','MEAN','MIN','NULL','OVSN','OVSP','PKPK','PER','PHASE','RISE','RISE28','RMS','SDEV','TOP','WID','WIDN'
        '''

        self.__write(f'PARAMETER_CUSTOM {channel_meas[1:]},{measurement},{channel_main}')
        self.OPC()


    #Extraneous functions
    def screenshot(self, filepath:str, filename:str):
        '''
        Takes a screenshot of the current scope screen

        Parameters:
            filepath: Location of where to save the screenshot
            filename: Name of the file to be saved. do NOT append with .jpg/.png/etc
        '''

        #self.__write(r'HARDCOPY_SETUP DEV,PNG,FORMAT,LANDSCAPE,BCKG,Std,DEST,REMOTE,DIR,"C:\\USERS\\LECROYUSER\\",FILE,"SCREEN--00000.PNG",AREA,DSOWINDOW,PRINTER,"MICROSOFTXPSDOCUMENTWRITER"')
        self.OPC()
        time.sleep(1) #Delays JUST in case it takes time for traces to turn on/etc
        self.STOP()
        self.__write('SCDP')

        result_str=self.instr.read_raw()

        f=open(f'{filepath}\\{filename}.png','wb')
        f.write(result_str)
        f.flush()
        f.close()

    def captureWaveforms(self, channel_meas:str, waveform_num:int, test_text:str, popup_label, timeout:float = 70):
        '''
        Captures a specified number of waveforms and then stops

        Parameters:
            channel_meas: 'P1' - 'P6'
            waveform_num: How many waveforms to capture
            test_text: What the current popup label text is displaying
            popup_label: Popup label object, updates with current waveform count during this function
            timeout: Number in seconds, if time passes the timeout, the waveform capture will stop wherever it is. Added in case of bad signals
        '''

        time.sleep(1)
        self.clearSweeps()
        self.trigMode('AUTO')

        time_elapsed = 0.0
        while int(self.meas(channel_meas,'num') < waveform_num) and time_elapsed<timeout:
            time.sleep(0.5) #Slight delay to prevent infinite calling
            time_elapsed += 0.5
            current_waveform = int(self.meas(channel_meas,'num'))
            new_text = test_text + f' \n {current_waveform} / {waveform_num} Waveforms'
            popup_label.config(text = new_text)

        self.STOP()
        self.OPC()
        popup_label.config(text = test_text)

    def setupChannel(self, channel_main:str, low_val:float, high_val:float):
        '''
        Sets up a main channel based on the highest and lowest values, scaling to 6/8 total vertical divisions

        Parameters:
            channel_main: 'C1' - 'C4'
            low_val: The lowest value that the channel is expected to be
            high_val: The highest value that the channel is expected to be
        '''
        #Sets up channel. Takes up 6 of 8 vertical divisions
        mean = ((high_val-low_val)/2)+low_val

        self.offsetVert(channel_main, f'-{mean}')
        self.vertScale(channel_main, f'{(high_val-low_val)/6}')
        self.OPC()

    def setupChannelPercent(self,channel_main:str, value:float, percent:float):
        '''
        Sets up a main channel based on middle value, and a percent max/min

        Parameters:
            channel_main: 'C1' - 'C4'
            value: The expected value. Will be centered on the screen
            percent: How much percent +/- for the signal. Will display % as the 1st ant 7th divsion, giving 1 division space on each side
        '''
        self.setupChannel(channel_main, value*(1-(percent/100)), value*(1+(percent/100)))



class SUPPLY:
    def __init__(self, rm, connection_ID:str, measurement_delay:float = 0.2):
        """
        Creates a SUPPLY object. For remote control of DC power supplies

        Parameters:
            rm: Pyvisa resource manager object
            connection_ID: String that contains the resource connection for the scope
            measurement_delay: Time to delay current/voltage measurements. To allow changes to propogate
        """
        generic_supply = [' 9205B', ' 9202B']

        self.instr = rm.open_resource(connection_ID)
      
        self.array = str(self.instr.query('*IDN?')).split(',')
        self.alias = self.array[1]
        self.delay = measurement_delay

        self.generic = False
        if self.alias in generic_supply:
            self.generic = True


    def __write(self, string:str):
        '''
        Internal command. Writes to the instrument

        Parameters:
            string: Any string, will be written directly to the instrument
        '''
        self.instr.write(string)
    def __query(self, string:str):
        '''
        Internal command. Asks for data from the instrument, and returns it

        Parameters:
            string: Any string, will be written directly to the instrument
        '''
        out = self.instr.query(string)
        return out
    


    def output(self, out:bool):
        '''
        Turns the output on or off

        Parameters:
            out: Output is on if True, out if False
        '''
        value = 'OFF'
        if out:
            value = 'ON'
        self.__write(f'OUTP {value}')

    def setVoltage(self, voltage:float|str):
        '''
        Sets the output voltage

        Parameters:
            voltage: Level for the voltage output. A number, of 'MAX'
        '''
        self.__write(f'VOLT {voltage}')

    def setCurrent(self, current:float|str):
        '''
        Sets the current limit

        Parameters:
            current: Level for the current limit. A number, of 'MAX'
        '''
        self.__write(f'CURR {current}')

    def meas(self, meas_unit:str):
        '''
        Measures the voltage or current of the supply

        Parameters:
            meas_unit: 'VOLT','CURR'
        Returns:
            meas_out_round: The output from the supply, rounded to 3 digits for readability
        '''
        time.sleep(self.delay)  #Delays measurment until it has had time to propogate
        meas_out = float(self.__query(f'MEAS:{meas_unit}?'))    
        meas_out_round = round(meas_out,3)
        return meas_out_round
    

class LOAD:
    def __init__(self, rm, connection_ID:str, measurement_delay:float = 0.2):
        """
        Creates a LOAD object. For remote control of DC loads

        Parameters:
            rm: Pyvisa resource manager object
            connection_ID: String that contains the resource connection for the scope
            measurement_delay: Time to delay current/voltage measurements. To allow changes to propogate
        """
        generic_load = ['63004-150-60']

        self.instr = rm.open_resource(connection_ID)


        self.array = str(self.instr.query('*IDN?')).split(',')
        self.alias = self.array[1]
        self.delay = measurement_delay

        self.generic = False
        if self.alias in generic_load:
            self.generic = True
        
        self.l_current = self.getMaxCurrent('L')
        self.m_current = self.getMaxCurrent('M')
        self.h_current = self.getMaxCurrent('H')

        self.max_power = float(0)

        self.max_power = self.getMaxPower()

    def __write(self, string:str):
        '''
        Internal command. Writes to the instrument

        Parameters:
            string: Any string, will be written directly to the instrument
        '''
        self.instr.write(string)
    def __query(self, string:str):
        '''
        Internal command. Asks for data from the instrument, and returns it

        Parameters:
            string: Any string, will be written directly to the instrument
        '''
        out = self.instr.query(string)
        return out


    def getMaxPower(self):
        '''
        Finds and returns the maximum power of the DC load

        Returns:
            output: The maximum power in Watts of the load
        '''
        self.__write('LOAD OFF')
        self.__write(f'MODE CPH')
        output = float(self.__query(f'POW:STAT:L1? MAX'))
        self.__write('MODE CCH')
        return output
    
    def getMaxCurrent(self, range:str):
        '''
        Finds and returns the maximum current of the load

        Returns:
            output: The maximum current in amps
        '''
        self.__write('LOAD OFF')
        self.mode('CC',{range})
        output = float(self.__query(f'CURR:STAT:L1? MAX'))
        return output


    def output(self, out:bool):
        '''
        Turns the output on or off

        Parameters:
            out: Output is on if True, out if False
        '''
        value = 'OFF'
        if out:
            value = 'ON'
        self.__write(f'LOAD {value}')

    def mode(self, mode:str, range:str):
        '''
        Sets the load mode, and range of the mode

        Parameters:
            mode: 'CC','CR','CV','CP','CCD','CRD','BAT','UDW'
            range: 'L','M','H'
        '''
        self.output(False)
        self.__write(f'MODE {mode}{range}')

    def staticResist(self, resistance:float):
        '''
        While in constant resistance mode, sets the resistance level

        Parameters:
            resistance: resistance measured in ohms
        '''
        self.__write(f'RESISTANCE:STAT:L1 {resistance}')

    def autoCCMode(self,device):

        raise NotImplementedError

        max_current = device.output_current_max
        if max_current > self.h_current:
            raise Exception('Current max too high for load')
        elif self.m_current < max_current <= self.h_current:
            self.mode('CC','H')
        elif self.l_current < max_current <= self.m_current:
            self.mode('CC','M')
        else:
            self.mode('CC','L')


    def staticCurrent(self, current:float):
        '''
        While in constant current mode, sets the current level

        Parameters:
            current: Current level in amps
        '''
        self.__write(f'CURR:STAT:L1 {current}')

    def voltageRange(self,range:str):
        '''
        While in constant current mode, sets the current level

        Parameters:
            'L','M','H'
        '''
        self.__write(f'CONF:VOLT:RANGE {range}')

    def dynamicLevel(self, level:str, current:float):
        '''
        While in dynamic current mode, sets the specified current level.

        Parameters:
            level: 'L1','L2'
            current: Current in amps to set L1 or L2 at
        '''
        self.__write(f'CURR:DYN:{level} {current}')

    def setDyanmicTime(self, duration:str, time:float):
        '''
        While in dynamic current mode, high and low time. Aka L1 and L2 time

        Parameters:
            duration: 'T1','T2'
            time: Time to stay at L1 or L2
        '''
        self.__write(f'CURR:DYN:{duration} {time}')
    
    def dyanmicFrequency(self, frequency:int|str):
        '''
        While in dynamic current mode, sets dynamic time using frequency

        Parameters:
            frequency: Frequency in hertz or khrtz. For khrts, append with "k" only
        '''
        if 'k' in str(frequency):
            frequency = frequency[:-1]
            frequency = float(frequency) * 1000

        self.setDyanmicTime('T1', 1/(2*float(frequency)))
        self.setDyanmicTime('T2', 1/(2*float(frequency)))

    def slewRate(self, slew:str|float):
        '''
        While in dynamic current mode, sets rise and fall slew rate

        Parameters:
            slew: 'MAX','MIN', or a number
        '''
        self.__write(f'CURR:DYN:RISE {slew}')
        self.__write(f'CURR:DYN:FALL {slew}')

    def repeat(self, repeat_num:int):
        '''
        While in dynamic current mode, sets number of times to repeat load ON event

        Parameters:
            repeat_num: 0 is infinite. Otherwise equal to number of repeats
        '''
        self.__write(f'CURR:DYN:REP {repeat_num}')


    def dynamicSetup(self, mode_range:str, level_1:float, level_2:float, frequency_hz:int|str, slewrate:str|float, repeat:int):
        '''
        Fully sets up the load in dynamic current mode with all params

        Parameters:
            mode_range. 'L','M','H'
            level_1: Current level for first point
            level_2: Current level for second point
            frequency_hz: Frequency in hertz or kHz. For kHz, append with "k" only
            slewrate: 'MAX','MIN', or a number
            repeat: 0 is infinite. Otherwise equal to number of repeats
        '''
        self.output(False)
        self.mode('CCD', mode_range)
        self.dynamicLevel('L1', level_1)
        self.dynamicLevel('L2', level_2)
        self.dyanmicFrequency(frequency_hz)
        self.slewRate(slewrate)
        self.repeat(repeat)
        time.sleep(0.2) #Delay to make sure changes occur
  

    def meas(self, meas_unit:str):
        '''
        Measures the voltage or current of the load

        Parameters:
            meas_unit: 'VOLT','CURR'
        Returns:
            meas_out_round: The output from the load, rounded to 3 digits for readability
        '''

        time.sleep(self.delay)  #Delays measurment until it has had time to propogate
        meas_out = float(self.__query(f'MEAS:{meas_unit}?'))    
        meas_out_round = round(meas_out,3)
        return meas_out_round


class DUT:
    def __init__(self):
        """
        Creates a DUT object. Holds information for the device under test. for DC DC testing
        """
        self.test_list = []
        self.load_list = []
        self.name = ''
        self.ic_type = ''
        self.extfets = False
        self.device_input_voltage = float(0)
        self.supply_input_voltage = float(0)
        self.output_voltage_max = float(0)
        self.output_voltage_nom = float(0)
        self.output_current_max = float(0)
        self.output_current_nom = float(0)
        self.frequency = float(0)
        self.supply_current = float(0)

        self.dut_type = ''

        self.jitter_bool = False

        self.folder_name_path = str('')
        self.python_path = str('')

    def getDeviceReport(self):
        """
        Retreives the correct report template based on the device type

        Returns:
            Returns either a string of the file name, or a blank string
        """
        match self.dut_type:
            case 'Load Switch':
                return 'Load_Switch_template.xlsm'
            case 'LDO': 
                return 'VR_LDO_template.xlsm'
            case 'Converter': 
                return 'VR_Converter_template.xlsm'
            case 'External Fet Converter': 
                return 'VR_External_FET_template.xlsm'
            case _:
                return ''

    def getSupplyCurrent(self):
        """
        Gets the correct supply current, based on the input and output power of the device.

        Returns:
            Returns ither a float number to set the supply current to, or 'MAX' if the supply and device input voltage are different
        """
        if self.device_input_voltage == self.supply_input_voltage:
            self.supply_current = round(1 + (self.output_voltage_max*self.output_current_max)/(0.7*self.supply_input_voltage),2)
            return self.supply_current
        else:
            return str('MAX')
        
    def makeLoadPointList(self, exclude = []):
        """
        Makes a list of load points, based on all selected points. Can also choose to exclude any specific tests if unneeded

        Parameters:
            exclude: Which test to exclude. 'min','tdc','max','transient'

        Returns:
            output_list: A list of strings with the desired tests, minus any exluded
        """
        output_list = []
        for _, load_point in enumerate(self.load_list):
            if load_point in exclude:
                pass
            else:
                output_list.append(load_point)
        return output_list










def close_equipment(): 
    """    
    Closes out all remote equipment, and resouce manager
    """
    try:
        load.mode('CC','H')
        load.staticCurrent(float(0.1))
        load.output(True)
        supply.output(False)

        load.instr.close()
        supply.instr.close()
        scope.instr.close()
        
    except  Exception as e:
        #print(e)
        pass

    try:
        rm.close()
    except Exception as e:
        #print(e)
        exit


def discharge(device:DUT):
    """
    Discharges the device under test, and resets supply and load
    """
    try:
        supply.setCurrent(device.getSupplyCurrent())
        supply.output(False)
        load.mode('CC','H')
        load.staticCurrent(0.1)
        load.output(True)
    except Exception as e:
        exit
