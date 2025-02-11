import pyvisa
import os
from datetime import datetime
from EquipmentClasses import *
import time
import threading


def debug_config():
    rm = pyvisa.ResourceManager()
    resource_array = rm.list_resources()

    #print(resource_array)

    resource_list = []
    resource_alias_list = []
    python_path = os.getcwd()
    #print(python_path)

    f = open(f"{python_path}\\NewInstrumentConfig.txt", 'w')


    f.write('Alias    User ID     Instrument Connection ID \n')
    f.write('---------------------------------------- \n')
    #print('Alias    User ID     Instrument Connection ID')
    #print('----------------------------------------')
    for x in resource_array:
        
        counter = resource_array.index(x)
        resource_info = rm.resource_info(resource_array[counter])

        user_ID_split = ['Not Found', 'Not Found', 'Not Found']
        try:
            resource = rm.open_resource(resource_info.resource_name)
            user_ID = resource.query(('*IDN?'))
            #print(user_ID)
            user_ID_split = user_ID.split(',')
            resource.close()
        except Exception as e:
            pass

        try:
            #print(f'{resource_info.alias}   {user_ID_split[1]}   {resource_info.resource_name}')
            f.write(f'{resource_info.alias}   {user_ID_split[1]}   {resource_info.resource_name} \n')
        except Exception as e:
            #print(f'{resource_info.alias}   {'Unavailable'}   {resource_info.resource_name}')
            f.write(f'{resource_info.alias}   {'Unavailable'}   {resource_info.resource_name} \n')
        

    f.close()
    rm.close()


def debugscope_screenshot(scope_ID:str, filename:str):
    rm = pyvisa.ResourceManager()

    debugScope = SCOPE(rm, scope_ID, 10000)

    filepath = os.getcwd()

    debugScope.screenshot(filepath, filename)

    debugScope.instr.close()
    rm.close()
#debug_config()

def TestScript():
    rm = pyvisa.ResourceManager()
    scope_ID = 'TCPIP0::10.10.15.175::inst0::INSTR'
    supply_ID = 'USB0::0x2EC7::0x9200::800886011777110059::0::INSTR'
    load_ID = 'USB0::0x0A69::0x0880::630041500253::0::INSTR'

    debugScope = SCOPE(rm, scope_ID, 10000)
    debugSupply = SUPPLY(rm, supply_ID)
    debugLoad = LOAD(rm,load_ID)

    def func1():
        debugSupply.output(False)
        voltage = 24
        debugSupply.setVoltage(voltage)
        debugSupply.output(True)

        percent_vary = 5
        per_pos = 1 + (percent_vary/100)
        per_neg = 1 - (percent_vary/100)

        while True:
            debugSupply.setVoltage(voltage*per_pos)
            time.sleep(0.01)
            debugSupply.setVoltage(voltage*per_neg)
            time.sleep(0.01)





    #testing_thread_1 = threading.Thread(target = func1)
    #testing_thread_1.start()
    supply.system('LOCAL')
    time.sleep(3)

    #print('x')

    close_equipment()

'''
rm = pyvisa.ResourceManager()

debugScope = SCOPE(rm, 'TCPIP0::10.10.15.175::inst0::INSTR')


filepath = os.getcwd()

now = datetime.now()
date_time_str = now.strftime(r'%Y-%m-%d--%H-%M-%S')


debugScope.screenshot(filepath, 'Capture_12Vin_MAX_Secondary')
'''





'''

meas_out = float(Scope.query((rf"""vbs? 'return=app.measure.p5.out.result.value' """)))

print(meas_out)

print(round(meas_out,3))


Scope.write('STOP')
Scope.query('*OPC?')

Scope.write(r'HARDCOPY_SETUP DEV,PNG,FORMAT,LANDSCAPE,BCKG,Std,DEST,REMOTE,DIR,"C:\\USERS\\LECROYUSER\\",FILE,"SCREEN--00000.PNG",AREA,DSOWINDOW,PRINTER,"MICROSOFTXPSDOCUMENTWRITER"')

Scope.write('SCDP')

result_str=Scope.read_raw()

filepath = os.getcwd()

now = datetime.now()
date_time_str = now.strftime(r'%Y-%m-%d--%H-%M-%S')

f=open(f'{filepath}\\Capture_{date_time_str}.png','wb')
f.write(result_str)
f.flush()
f.close()


Scope.close()
rm.close()

'''



#woo more debug



#end = 1.8

#Want this to take 24 steps. To the TDC current. LAst two are TDC and max.... well i guess lets see how good the steps are

#for x in range(0,25):
#
#    step = round(float(x*(end/24)),3)
#    print(step)


'''

rm = pyvisa.ResourceManager()

scope = SCOPE(rm, 'TCPIP0::10.10.10.128::inst0::INSTR')

scope.write('*CLS')
x = f'{int(scope.query('INR?')):016b}'[2]
print(x)

scope.STOP()

scope.timeScale(2)
scope.OPC()
scope.write('*CLS')
scope.trigMode('SINGLE')




time_elapsed = 0.0
while time_elapsed < 10:
    time.sleep(0.2)
    time_elapsed += 0.1
    x_raw = scope.query('INR?')
    print(x_raw)
    x = f'{int(x_raw):016b}'[2]
    print(x)

    if x == '1':
        print('Broken')
        break

#while (f'{int(scope.query('INR?')):016b}')[2] != 1:
#    time.sleep(0.2)
#    print('Waiting...')
#print('Trig!')
    



rm.close()
'''