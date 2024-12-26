import pyvisa
import time
import os


class Scope:
    def __init__(self, rm, connection_ID:str, timeout_ms:int = 100000):

        generic_scope = ['HDO6104A', 'WS4104HD']

        self = rm.open_resource(connection_ID)
        self.timeout = {timeout_ms}
        self.clear()
        self.array = str(self.query('*IDN?')).split(',')

        self.alias = self.array[1]

        self.write('COMM_HEADER OFF')#Ensures that scope messages are in shortest possible return
        self.write(r'HARDCOPY_SETUP DEV,PNG,FORMAT,LANDSCAPE,BCKG,Std,DEST,REMOTE,DIR,"C:\\USERS\\LECROYUSER\\",FILE,"SCREEN--00000.PNG",AREA,DSOWINDOW,PRINTER,"MICROSOFTXPSDOCUMENTWRITER"')


        self.generic = False
        if self.alias in generic_scope:
            self.generic = True


    
    def OPC(self):
        '''
        Completes if scope has executed all commands
        '''
        #This way we can do a listen command IF needed
        self.query('*OPC?')

    
    def clearSweeps(self):
        """
        Clears all sweep data
        """
        self.write('CLEAR_SWEEPS') #Scope.write(r"""vbs 'app.measure.clearsweeps ' """) #Alternative command
        self.OPC()

    def trigMode(self, mode:str):
        '''
        mode:
            'STOP', 'AUTO', 'SINGLE', 'NORMAL'
        '''
        self.write(f'TRIG_MODE {mode}')
        self.OPC()

    def recall(self, recall_num:int):
        self.write(f'*RCL {recall_num}')
        self.OPC()

    def memorySize(self, memory_size:str):
        self.write(f'MSIZ {memory_size}')
        self.OPC()

    def forceCapture(self):
        self.write('FRTR')
        self.OPC()

    def ARM(self):
        self.write('ARM')
        self.OPC()

    def STOP(self):
        self.write('STOP')
        self.OPC()

    def horScale(self, time_per_division):
        self.write(f'TDIV {time_per_division}')
        self.OPC()

    def triggerDelay(self, delay_time:str):
        self.write(f'TRIG_DELAY {delay_time}')
        self.OPC()

    def autoSetup(self):
        self.write('ASET')
        self.OPC()
    
    def sampleRate(self):
        '''
        Sets the sample rate if available. NOTE: As of right now, can only set to maximum
        '''
        self.write("vbs 'app.acquisition.horizontal.maximize =\"FixedSampleRate\"'")

    def persist(self, persist_true:bool):
        self.write(f"vbs 'app.Display.Persisted = {persist_true}'")

    def passFail(self, sweep_num:int):
        self.write(f'PASS_FAIL ON,ALLQ1TOQ4ORALLQ5TOQ8,{sweep_num}')


    #Channel specific commands
    def attenuation(self, channel_main:str, atten:float):
        '''
        channel_main:
            'C1' - 'C4'
        '''
        self.write(f'{channel_main}:ATTENUATION {atten}')

    def bandwidth(self, channel_main:str, bw:str):

        '''
        channel_main:
            'C1' - 'C4'
        bw:
            'OFF','20MHz','200MHz'
        '''
        self.write(f'BWL {channel_main},{bw}')

    def offsetVert(self, channel_main:str, offset:float):
        
        self.write(f'{channel_main}:OFFSET {offset}')

    def setTrigger(self, channel_main:str, slope:str, trig_level:float):
        '''
        channel_main:
            'C1' - 'C4'
        slope:
            'POS','NEG'
        
        '''
        self.write(f'TRIG_SELECT EDGE,SR,{channel_main}')
        self.write(f'{channel_main}:TRIG_SLOPE {slope}')
        self.write(f'{channel_main}:TRIG_LEVEL {trig_level}')


    def vertScale(self, channel_main:str, units_per_division:float):
        self.write(f'{channel_main}:VOLT_DIV {units_per_division}')

    def traceToggle(self, channel_main:str, trace_true:bool):
        value = 'OFF'
        if trace_true:
            value = 'ON'
        self.write(f'{channel_main}:TRACE {value}')

    def meas(self, channel_meas:str, parameter:str = 'out', multiplier:int = 1):
        '''
        channel_meas:
            'P1' - 'P6'
        parameter:
            'out','mean','min','max','sdev','num'

        multiplier:
            Multiplies the result, before rounding to 3 decimal places for readability
        '''
        meas_out = float(self.query((rf"""vbs? 'return=app.measure.{channel_meas}.{parameter}.result.value' """)))
        meas_out_round = round(multiplier*meas_out,3)
        return meas_out_round
    
    def zoomHorDelay(self, channel_zoom:str, delay_time:float):

        self.write(f'{channel_zoom}:HOR_POSITION {delay_time}')

    def zoomHorMagnify(self, channel_zoom:str, magnify_value:float):
        '''
        channel_zoom:
            'Z1' - 'Zn'
        magnify_value:
            Magnifies by this value. 1.0 is no magnification
        '''
        self.write(f'{channel_zoom}:HOR_MAGNIFY {magnify_value}')

    def zoomOffsetVert(self, channel_zoom:str, offset:float):
        self.write(f'{channel_zoom}:VERT_POSITION {offset}')

    def zoomVertMagnify(self, channel_zoom:str, magnify_value:float):
        '''
        channel_zoom:
            'Z1' - 'Zn'
        magnify_value:
            Magnifies by this value. 1.0 is no magnification
        '''
        self.write(f'{channel_zoom}:VERT_MAGNIFY {magnify_value}')

    def setUnit(self, channel_main:str, unit:str):

        raise NotImplementedError
        #Scope.write((rf"""vbs? 'app.Acquisition.{channel}.Unit = "OTHER"' """))
        #Scope.write((rf"""vbs? 'app.Acquisition.{channel}.Type = "ELECTRICAL"' """))
        #Scope.write((rf"""vbs? 'app.Acquisition.{channel}.Units = "AMPERE"' """))

        self.write(f'{channel_main}:UNIT {unit}')

        #print('amps')
        #Scope.write((rf'app.Acquisition.{channel}.Unit = "OTHER"'))
        #Scope.write((rf'app.Acquisition.{channel}.Type = "ELECTRICAL"'))
        #Scope.write((rf'app.Acquisition.{channel}.Units = "AMPERE"'))
    
    def setParamSkew(self, channel_meas:str, channel_source_1:str, slope_1:str, trigpercent_1:int, channel_source_2:str, slope_2:str, trigpercent_2:int):
        '''
        channel_meas:
            'P1' - 'P6'. Parameter to set skew measurement to
        channel_source:
            'C1' - 'C4','F1' - 'Fn'. Source of the first skew
        slope:
            'NEG','POS'
        '''
        self.write(f'PARAMETER_CUSTOM {channel_meas[1:]},SKEW,{channel_source_1},{slope_1},{trigpercent_1} PCT,{channel_source_2},{slope_2},{trigpercent_2} PCT')
        #self.write(f'PARAMETER_CUSTOM 2,SKEW,F1,NEG,50 PCT,C3,POS,50 PCT')

    def setParam(self, channel_meas:str, channel_main:str, measurement:str):
        '''
        channel_main:
            'C1' - 'C4'
        measurement:
            'AMPL','AREA','BASE','DLY','DUTY','FALL','FALL82','FREQ','MAX','MEAN','MIN','NULL','OVSN','OVSP','PKPK','PER','PHASE','RISE','RISE28','RMS','SDEV','TOP','WID','WIDN'
        '''
        self.write(f'PARAMETER_CUSTOM {channel_meas[1:]},{measurement},{channel_main}')


    #Extraneous functions
    def screenshot(self, filepath:str, filename:str):

        self.OPC()
        time.sleep(1) #Delays JUST in case it takes time for traces to turn on/etc
        self.write('SCDP')

        result_str=self.read_raw()

        f=open(f'{filepath}\\{filename}.png','wb')
        f.write(result_str)
        f.flush()
        f.close()

    def captureWaveforms(self, channel_meas:str, waveform_num:int):
        self.clearSweeps()
        self.trigMode('AUTO')

        while int(self.meas(channel_meas,'num') < waveform_num):
            time.sleep(0.5) #Slight delay to prevent infinite calling

        self.STOP()

    
class Supply:
    def __init__(self, rm, connection_ID:str, measurement_delay:float = 0.2):

        generic_supply = [' 9205B', ' 9202B']

        self = rm.open_resource(connection_ID)
        self.clear()
        self.array = str(self.query('*IDN?')).split(',')
        self.alias = self.array[1]
        self.delay = measurement_delay

        self.generic = False
        if self.alias in generic_supply:
            self.generic = True

    def output(self, out:bool):
        value = 'OFF'
        if out:
            value = 'ON'
        self.write(f'OUTP {value}')

    def setVoltage(self, voltage:float):
        self.write(f'VOLT {round(voltage,2)}')

    def setCurrent(self, current:float):
        self.write(f'VOLT {round(current,2)}')

    def meas(self, meas_unit:str):
        '''
        meas_unit:
            'VOLT','CURR'
        '''
        time.sleep(self.delay)  #Delays measurment until it has had time to propogate
        meas_out = float(self.query(f'MEAS:{meas_unit}?'))    
        meas_out_round = round(meas_out,3)
        return meas_out_round
    

class Load:
    def __init__(self, rm, connection_ID:str, measurement_delay:float = 0.2):

        generic_load = ['63004-150-60']

        self = rm.open_resource(connection_ID)
        self.clear()
        self.array = str(self.query('*IDN?')).split(',')
        self.alias = self.array[1]
        self.delay = measurement_delay

        self.generic = False
        if self.alias in generic_load:
            self.generic = True

        self.maxpower = getMaxPower()
        self.maxcurrent = getMaxCurrent()

        def getMaxPower():
            self.write('LOAD OFF')
            self.write(f'MODE CPH')
            output = float(self.query(f'POW:STAT:L1? MAX'))
            self.write('MODE CCH')
            return output
        
        def getMaxCurrent():
            self.write('LOAD OFF')
            self.write(f'MODE CCH')
            output = float(self.query(f'CURR:STAT:L1? MAX'))
            return output


    def output(self, out:bool):
        value = 'OFF'
        if out:
            value = 'ON'
        self.write(f'LOAD {value}')

    def mode(self, mode:str, range:str):
        '''
        mode:
            'CC','CR','CV','CP','CCD','CRD','BAT','UDW'
        range:
            'L','M','H'
        '''
        self.write(f'MODE {mode}{range[0]}')

    def staticCurrent(self, current:float):
        self.write(f'CURR:STAT:L1 {current}')

    def voltageRange(self,range:str):
        self.write(f'CONF:VOLT:RANGE {range[0]}')

    def dynamicLevel(self, level:str, current:float):
        '''
        level:
            'L1','L2'
        '''
        self.write(f'CURR:DYN:{level} {round(current,2)}')

    def __setDyanmicTime(self, duration:float, time:str):
        '''
        duration:
            'T1','T2'
        '''
        self.write(f'CURR:DYN:{duration} {time}')
    
    def dyanmicFrequency(self, frequency_hz:int):
        self.__setDyanmicTime('T1', 1/2*frequency_hz)
        self.__setDyanmicTime('T2', 1/2*frequency_hz)

    def slewRate(self, slew:str|float):
        '''
        slew:
            'MAX','MIN', or a number
        '''
        self.write(f'CURR:DYN:RISE {slew}')
        self.write(f'CURR:DYN:FALL {slew}')

    def repeat(self, repeat_num:int):
        '''
        repeat_num:
            0 is infinite. Otherwise equal to number of repeats
        '''
        self.write(f'CURR:DYN:REP {repeat_num}')


    def dynamicSetup(self, mode_range:str, level_1:float, level_2:float, frequency_hz:int, slewrate:str|float, repeat:int):
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
        meas_out = float(self.query(f'MEAS:{meas_unit}?'))    
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
        self.frequency_kHz = float()

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




import shutil

python_path = os.getcwd()

shutil.copy2(f'{python_path}\\Templates\\VR_LDO_template.xlsm', f'{python_path}\\example')
