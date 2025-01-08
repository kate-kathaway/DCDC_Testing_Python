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
        Tells the scope to wait until the current 
        '''
        self.__write(f'WAIT {timeout}')
        self.OPC()
        

    def waitUntilTrig(self, timeout:int|float = 15):
        #Timeout is in seconds

        time_elapsed = 0.0
        while self.__query('TRIG_MODE?') != 'STOP':
            time.sleep(0.1)
            time_elapsed += 0.1
            if time_elapsed >= timeout:
                break
            if 'STOP' in self.__query('TRIG_MODE?'):
                break
        
    
    def clearSweeps(self):
        """
        Clears all sweep data
        """
        self.__write('CLEAR_SWEEPS') #Scope.write(r"""vbs 'app.measure.clearsweeps ' """) #Alternative command
        self.OPC()

    def trigMode(self, mode:str):
        '''
        mode:
            'STOP', 'AUTO', 'SINGLE', 'NORMAL'
        '''
        self.__write(f'TRIG_MODE {mode}')
        self.OPC()

    def recall(self, recall_num:int):
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
        self.__write(f'MSIZ {memory_size}')
        self.OPC()

    def forceCapture(self):
        self.__write('TRMD SiNGLE;ARM;FRTR')
        self.WAIT()
        self.OPC()

    def ARM(self):
        self.__write('ARM')
        self.OPC()

    def STOP(self):
        self.__write('STOP')
        self.OPC()

    def timeScale(self, time_per_division):
        self.__write(f'TDIV {time_per_division}')
        self.OPC()

    def triggerDelay(self, delay_time):
        self.__write(f'TRIG_DELAY {delay_time}')
        self.OPC()

    def autoSetup(self):
        self.__write('C1:ASET')
        self.__write('C2:ASET')
        self.__write('C3:ASET')
        self.__write('C4:ASET')
        self.OPC()

    def sampleRate(self):
        '''
        Sets the sample rate if available. NOTE: As of right now, can only set to maximum
        '''
        self.__write("vbs 'app.acquisition.horizontal.maximize =\"FixedSampleRate\"'")
        self.OPC()

    def persist(self, persist_true:bool):
        self.__write(f"vbs 'app.Display.Persisted = {persist_true}'")
        self.OPC()

    def passFail(self, sweep_num:int):
        self.__write(f'PASS_FAIL ON,ALLQ1TOQ4ORALLQ5TOQ8,{sweep_num}')
        self.OPC()


    #Channel specific commands
    def attenuation(self, channel_main:str, atten:float):
        '''
        channel_main:
            'C1' - 'C4'
        '''
        self.__write(f'{channel_main}:ATTENUATION {atten}')
        self.OPC()

    def bandwidth(self, channel_main:str, bw:str):

        '''
        channel_main:
            'C1' - 'C4'
        bw:
            'OFF','20MHz','200MHz'
        '''
        self.__write(f'BWL {channel_main},{bw}')
        self.OPC()

    def offsetVert(self, channel_main:str, offset):
        
        self.__write(f'{channel_main}:OFFSET {offset}')
        self.OPC()

    def setTrigger(self, channel_main:str, slope:str, trig_level:float):
        '''
        channel_main:
            'C1' - 'C4'
        slope:
            'POS','NEG'
        
        '''
        self.__write(f'TRIG_SELECT EDGE,SR,{channel_main}')
        self.__write(f'{channel_main}:TRIG_SLOPE {slope}')
        self.__write(f'{channel_main}:TRIG_LEVEL {trig_level}')
        self.OPC()


    def vertScale(self, channel_main:str, units_per_division:float):
        self.__write(f'{channel_main}:VOLT_DIV {units_per_division}')
        self.OPC()

    def traceToggle(self, channel_main:str, trace_true:bool):
        value = 'OFF'
        if trace_true:
            value = 'ON'
        self.__write(f'{channel_main}:TRACE {value}')
        self.OPC()
        time.sleep(0.4)

    def meas(self, channel_meas:str, parameter:str = 'out', multiplier:int = 1):
        '''
        channel_meas:
            'P1' - 'P6'
        parameter:
            'out','mean','min','max','sdev','num'

        multiplier:
            Multiplies the result, before rounding to 3 decimal places for readability
        '''
        meas_out = float(self.__query((rf"""vbs? 'return=app.measure.{channel_meas}.{parameter}.result.value' """)))
        meas_out_round = round(multiplier*meas_out,3)
        return meas_out_round
    
    def zoomHorDelay(self, channel_zoom:str, delay_time:float):

        self.__write(f'{channel_zoom}:HOR_POSITION {delay_time}')
        self.OPC()

    def zoomHorMagnify(self, channel_zoom:str, magnify_value:float):
        '''
        channel_zoom:
            'Z1' - 'Zn'
        magnify_value:
            Magnifies by this value. 1.0 is no magnification
        '''
        self.__write(f'{channel_zoom}:HOR_MAGNIFY {magnify_value}')
        self.OPC()

    def zoomOffsetVert(self, channel_zoom:str, offset:float):
        self.__write(f'{channel_zoom}:VERT_POSITION {offset}')
        self.OPC()

    def zoomVertMagnify(self, channel_zoom:str, magnify_value:float):
        '''
        channel_zoom:
            'Z1' - 'Zn'
        magnify_value:
            Magnifies by this value. 1.0 is no magnification
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
        channel_meas:
            'P1' - 'P6'. Parameter to set skew measurement to
        channel_source:
            'C1' - 'C4','F1' - 'Fn'. Source of the first skew
        slope:
            'NEG','POS'
        '''
        self.__write(f'PARAMETER_CUSTOM {channel_meas[1:]},SKEW,{channel_source_1},{slope_1},{trigpercent_1} PCT,{channel_source_2},{slope_2},{trigpercent_2} PCT')
        self.OPC()
        #self.write(f'PARAMETER_CUSTOM 2,SKEW,F1,NEG,50 PCT,C3,POS,50 PCT')

    def setParam(self, channel_meas:str, channel_main:str, measurement:str):
        '''
        channel_main:
            'C1' - 'C4'
        measurement:
            'AMPL','AREA','BASE','DLY','DUTY','FALL','FALL82','FREQ','MAX','MEAN','MIN','NULL','OVSN','OVSP','PKPK','PER','PHASE','RISE','RISE28','RMS','SDEV','TOP','WID','WIDN'
        '''
        self.__write(f'PARAMETER_CUSTOM {channel_meas[1:]},{measurement},{channel_main}')
        self.OPC()


    #Extraneous functions
    def screenshot(self, filepath:str, filename:str):

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
        #Sets up channel. Takes up 6 of 8 vertical divisions
        mean = ((high_val-low_val)/2)+low_val

        self.offsetVert(channel_main, f'-{mean}')
        self.vertScale(channel_main, f'{(high_val-low_val)/6}')
        self.OPC()

    def setupChannelPercent(self,channel_main:str, value:float, percent:float):
        self.setupChannel(channel_main, value*(1-(percent/100)), value*(1+(percent/100)))

    
class SUPPLY:
    def __init__(self, rm, connection_ID, measurement_delay:float = 0.2):

        generic_supply = [' 9205B', ' 9202B']




        self.instr = rm.open_resource(connection_ID)

      
        self.array = str(self.instr.query('*IDN?')).split(',')
        self.alias = self.array[1]
        self.delay = measurement_delay

        self.generic = False
        if self.alias in generic_supply:
            self.generic = True


    def __write(self, string:str):
        self.instr.write(string)
    def __query(self, string:str):
        out = self.instr.query(string)
        return out
    


    def output(self, out:bool):
        value = 'OFF'
        if out:
            value = 'ON'
        self.__write(f'OUTP {value}')

    def setVoltage(self, voltage:float|str):
        self.__write(f'VOLT {voltage}')

    def setCurrent(self, current:float|str):
        self.__write(f'CURR {current}')

    def meas(self, meas_unit:str):
        '''
        meas_unit:
            'VOLT','CURR'
        '''
        time.sleep(self.delay)  #Delays measurment until it has had time to propogate
        meas_out = float(self.__query(f'MEAS:{meas_unit}?'))    
        meas_out_round = round(meas_out,3)
        return meas_out_round
    

class LOAD:
    def __init__(self, rm, connection_ID:str, measurement_delay:float = 0.2):

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
        self.instr.write(string)
    def __query(self, string:str):
        out = self.instr.query(string)
        return out


    def getMaxPower(self):
        self.__write('LOAD OFF')
        self.__write(f'MODE CPH')
        output = float(self.__query(f'POW:STAT:L1? MAX'))
        self.__write('MODE CCH')
        return output
    
    def getMaxCurrent(self, range:str):
        self.__write('LOAD OFF')
        self.mode('CC',{range})
        output = float(self.__query(f'CURR:STAT:L1? MAX'))
        return output


    def output(self, out:bool):
        value = 'OFF'
        if out:
            value = 'ON'
        self.__write(f'LOAD {value}')

    def mode(self, mode:str, range:str):
        '''
        mode:
            'CC','CR','CV','CP','CCD','CRD','BAT','UDW'
        range:
            'L','M','H'
        '''
        self.output(False)
        self.__write(f'MODE {mode}{range}')

    def staticResist(self, resistance:float):
        self.__write(f'RESISTANCE:STAT:L1 {resistance}')

    def autoCCMode(self,device):
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
        self.__write(f'CURR:STAT:L1 {current}')

    def voltageRange(self,range:str):
        self.__write(f'CONF:VOLT:RANGE {range[0]}')

    def dynamicLevel(self, level:str, current:float):
        '''
        level:
            'L1','L2'
        '''
        self.__write(f'CURR:DYN:{level} {current}')

    def setDyanmicTime(self, duration:str, time:float):
        '''
        duration:
            'T1','T2'
        '''
        self.__write(f'CURR:DYN:{duration} {time}')
    
    def dyanmicFrequency(self, frequency:int|str):

        if 'k' in str(frequency):
            frequency = frequency[:-1]
            frequency = float(frequency) * 1000

        self.setDyanmicTime('T1', 1/(2*float(frequency)))
        self.setDyanmicTime('T2', 1/(2*float(frequency)))

    def slewRate(self, slew:str|float):
        '''
        slew:
            'MAX','MIN', or a number
        '''
        self.__write(f'CURR:DYN:RISE {slew}')
        self.__write(f'CURR:DYN:FALL {slew}')

    def repeat(self, repeat_num:int):
        '''
        repeat_num:
            0 is infinite. Otherwise equal to number of repeats
        '''
        self.__write(f'CURR:DYN:REP {repeat_num}')


    def dynamicSetup(self, mode_range:str, level_1:float, level_2:float, frequency_hz:int|str, slewrate:str|float, repeat:int):
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
        meas_unit:
            'VOLT','CURR'
        '''
        time.sleep(self.delay)  #Delays measurment until it has had time to propogate
        meas_out = float(self.__query(f'MEAS:{meas_unit}?'))    
        meas_out_round = round(meas_out,3)
        return meas_out_round


class DUT:
    def __init__(self):
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
        match self.dut_type:
            case 'Load Switch':
                return 'Load_Switch_template.xlsm'
            case 'LDO': 
                return 'VR_LDO_template.xlsm'
            case 'Converter': 
                self.jitter_bool = True
                return 'VR_Converter_template.xlsm'
            case 'External Fet Converter': 
                self.jitter_bool = True
                return 'VR_External_FET_template.xlsm'
            case _:
                return ''

    def getSupplyCurrent(self):
        if self.device_input_voltage == self.supply_input_voltage:
            self.supply_current = round(1 + (self.output_voltage_max*self.output_current_max)/(0.7*self.supply_input_voltage),2)
            return self.supply_current
        else:
            return str('MAX')
        
    def makeLoadPointList(self, exclude = []):
        output_list = []
        for _, load_point in enumerate(self.load_list):
            if load_point in exclude:
                pass
            else:
                output_list.append(load_point)
        return output_list

    def getCurrentStep(self):
        #Want to make the current step as close to 24ish as possible. NEVER over 24. 23 for rounding safety
        for step_10x in range(1,100):
            if (10 * self.output_current_max / step_10x) < 23:
                self.current_step = float(step_10x/10)
            else:
                exit

        raise Exception('Current above 230A')









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
        exit

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
