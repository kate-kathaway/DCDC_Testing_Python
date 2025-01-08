from EquipmentClasses import *
import time
import pyvisa
from datetime import datetime
import csv

rm = pyvisa.ResourceManager()

supply = SUPPLY(rm, 'USB0::0x2EC7::0x9200::800886011777110059::0::INSTR')

supply.setCurrent('MAX')

now = datetime.now()
date_time_str = now.strftime(r'%Y-%m-%d--%H-%M-%S')

#data = f'Start Time {date_time_str}'
data = ['Start Time', date_time_str]

with open('document.csv','a', newline='') as fd:
    writer = csv.writer(fd)
    writer.writerow(data)

counter = 0

try:
    while True:
        counter+=1
        supply.output(True)
        time.sleep(15)
        current = supply.meas('CURR')
        now = datetime.now()
        date_time_str = now.strftime(r'%Y-%m-%d--%H-%M-%S')

        #data = f'{counter}, {date_time_str}, {current}'
        data = [counter, date_time_str, current]
        time.sleep(0.4)

        with open('document.csv','a', newline='') as fd:
            writer = csv.writer(fd)
            writer.writerow(data)



        supply.output(False)
        time.sleep(5)


except:
    supply.output(False)