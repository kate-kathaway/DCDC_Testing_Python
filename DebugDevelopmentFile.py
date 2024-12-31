import pyvisa
import os
from datetime import datetime
from EquipmentClasses import *
import time


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

#debug_config()
'''

global rm
rm = pyvisa.ResourceManager()

global Scope
#Scope = rm.open_resource('TCPIP0::10.10.11.76::inst0::INSTR')
#Scope = rm.open_resource(f'{scope_id}', write_termination='\n', read_termination='\n')
Scope = rm.open_resource('TCPIP0::10.10.10.128::inst0::INSTR')
Scope.timeout = 100000
Scope.clear()




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