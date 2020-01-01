# PicoLog_Thermocouple_Converter
This program is used to obtain thermocouple temperature readings (Type T), based on voltage readings, and a reference thermocouple junction temperature measured by a RTD. This program was created when I was working as a research assistant at the National University of Singapore Department of Electrical and Computer Engineering.

## Overview

For use with Pico Technology [PicoLog ADC-20/ADC-24 Data Loggers](https://www.picotech.com/data-logger/adc-20-adc-24/precision-data-acquisition). The RTD is put in a voltage divider circuit (input voltage +2.5V), in series with a resistor, and the voltage across the RTD is measured. Based on these parameters, the program calculates a temperature reading, which is the reference thermocouple junction temperature. The program then takes voltage values (mV) from the CSV output files of the PicoLog, and converts them into temperature values (°C) based on the junction reference temperature, using polynomial approximation formulas from [NIST and ITS-90](https://srdata.nist.gov/its90/download/type_t.tab).


There are options to do a direct conversion (mV to °C, or °C to mV) or to convert all values inside a CSV file.

## Usage

Simply run the ```Picolog_Conversion.py``` file; Or download the ```Picolog_Conversion``` folder and run the ```Picolog_Conversion.exe``` standalone executable. The main menu of the program is showed below.


![](https://github.com/mattleung10/PicoLog_Thermocouple_Converter/blob/master/sample/example/mainscreen.png)


After the conversion, the program creates a new CSV file with the converted temperature values, called ```<filename>_converted.csv```. See the example CSV files in the [sample](https://github.com/mattleung10/PicoLog_Thermocouple_Converter/tree/master/sample) folder.

## Example

Input CSV (values are in mV)
![](https://github.com/mattleung10/PicoLog_Thermocouple_Converter/blob/master/sample/example/demo.png)


Output CSV (values are in °C)
![](https://github.com/mattleung10/PicoLog_Thermocouple_Converter/blob/master/sample/example/demo_converted.png)
