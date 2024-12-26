import pyvisa
import os
from datetime import datetime

def debug_config():
    rm = pyvisa.ResourceManager()
    resource_array = rm.list_resources()

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