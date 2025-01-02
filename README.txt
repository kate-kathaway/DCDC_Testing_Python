#Description
These files are made for DC DC Testing for circuits

#NOTE
As of 12/31/25, program has not been verified to work for Jitter, VDS, and Deadtime tests. 
LDOs and Load Switches should be fine to test

#Dependencies
Before running, must install Python 3+
After, in command line type: pip install pvyisa-py

#How To Run
Run the "DCDC_GUI.py" file. Either by command prompt or via double-clicking to run

#Turn source code to EXE (If Edit's are made)
1. open cmd as admin

2. Type:
>pip install Pyinstaller

3. change cd to python path. Type:
>cd (Directory. Copy and paste folder file path)

4. Type : (Note: Capital P and I in PyInstaller)
>python -m PyInstaller -w DCDC_GUI.py

5. Can delete spec and build. Only the EXE  and internal folder matter. Located in dist folder
