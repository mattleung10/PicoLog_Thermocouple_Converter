#Picolog Thermocouple Conversion
#Created by Matthew Leung
#Conversion fomulas according to NIST and ITS-90

#For use with the Pico Technology Picolog ADC-20 and ADC-24

import os
import csv

#######################################################################################
# THERMOCOUPLE CONVERSION FUNCTIONS

#converts raw voltage (mV) to temperature (°C) (accurate range: -200°C to 400°C)
def v_to_temp(v):
    c_n_0 = [0.0000000E+00,
             2.5949192E+01,
             -2.1316967E-01,
             7.9018692E-01,
             4.2527777E-01,
             1.3304473E-01,
             2.0241446E-02,
             1.2668171E-03]
    c_n_pos = [0.000000E+00,
               2.592800E+01,
               -7.602961E-01,
               4.637791E-02,
               -2.165394E-03,
               6.048144E-05,
               -7.293422E-07,
               0.000000E+00]
    poly = 0.000000E+00
    
    if v >= 0: #if voltage is positive
        for n in range(0, len(c_n_pos), 1):
            poly += c_n_pos[n] * v ** n
    else: #if voltage is negative
        for n in range(0,len(c_n_0),1):
            poly += c_n_0[n] * v ** n
    return poly

#converts voltage (mV), v, to temperature (°C) based on reference temperature, ref
def calculate_temp(v, ref):
    return v_to_temp(temp_to_v(ref) + v)

#converts raw temperature (°C) to voltage (mV)
def temp_to_v(t):
    a_n_pos = [0.000000000000E+00,
               0.387481063640E-01,
               0.332922278800E-04,
               0.206182434040E-06,
               -0.218822568460E-08,
               0.109968809280E-10,
               -0.308157587720E-13,
               0.454791352900E-16,
               -0.275129016730E-19]
    poly = 0.000000E+00
    for n in range(0, len(a_n_pos), 1):
        poly += a_n_pos[n] * t ** n
    return poly

#converts temperature (°C) to voltage (mV)
def calculate_voltage(t, ref):
    return temp_to_v(t) - temp_to_v(ref)

#######################################################################################
# THERMOCOUPLE CONVERSION MODES

def TC_direct_converter_vtot():
    error = False
    while True:
        try:
            r = float(input("Enter reference temperature (°C): "))
            v = float(input("Enter voltage (mV): "))
            error = False
        except:
            error = True
            print("ERROR: Invalid input")
        if error == False:
            break
    print("Temperature:", calculate_temp(v, r), "°C")
    a = input("Press any key to continue.")
    return True

def TC_direct_converter_ttov():
    error = False
    while True:
        try:
            r = float(input("Enter the reference temperature (°C): "))
            t = float(input("Enter the measured temperature (°C): "))
        except:
            error = True
            print("ERROR: Invalid input")
        if error == False:
            break
    print("Voltage:", calculate_voltage(t, r), "mV")
    a = input("Press any key to continue.")
    return True

#######################################################################################
# RTD CONVERSION FUNCTIONS

def R_to_T_positive(rt):
    a = +3.9083E-03
    b = -5.7750E-07
    #c = -4.1830E-12 #for negative values
    r0 = 1000
    return (-1 * r0 * a + ((r0 * a)**2 - 4 * r0 * b * (r0 - rt))**0.5) / (2 * r0 * b)

def voltage_divider(v_r, v_t, r_s):
    return v_r * r_s / (v_t - v_r)

# Circuit:
#                       + v_r -
#   + v_t ------<>--------<>----------  _GND
#              r_s        r
#

#######################################################################################
# RTD CONVERSION MODES

def RTD_direct_converter():
    try:
        r = float(input("Enter RTD resistance (Ω): "))
    except:
        print("ERROR: Invalid input")
        return False
    print("The temperature is", R_to_T_positive(r), "°C")
    a = input("Press any key to continue.")
    return True

def RTD_voltdivide_converter():
    try:
        r_s = float(input("Enter series resistor value (Ω): "))
        v_t = float(input("Enter input voltage (V): "))
        v_r = float(input("Enter measured RTD voltage (V): "))
        r_therm = voltage_divider(v_r, v_t, r_s)
    except:
        print("ERROR: Invalid input")
        return False
    print("The RTD has resistance", r_therm, "corresponding to a temperature of", R_to_T_positive(r_therm), "°C")
    a = input("Press any key to continue.")
    return True

#######################################################################################
# CSV FUNCTIONS

#Prompts user to enter a valid filename (i.e. a csv file)
def getFileName():
    while True:
        error = False
        try:
            s = str(input("Enter file name: "))
            if len(s) >= 4:
                if s[len(s)-4:len(s)] != ".csv":
                    error = True
                else:
                    error = False
            else:
                error = True
            if not os.path.exists(s):
                error = True
        except:
            error = True

        if error == False:
            break
        else:
            print("ERROR: Invalid file name")
            
    return s

#Prompts user to enter the fieldname (title) of the reference temperature field, and returns [index in fieldnames, fieldname]
def get_reference_temp_field(fieldnames, filename):
    while True:
        error = False
        try:
            s = str(input("Enter the fieldname (title) of the reference temperature field in " + filename + ": "))
        except:
            print("ERROR: Invalid input\n")
            error = True
        if error == False:
            for i in range(0, len(fieldnames), 1):
                if s == fieldnames[i]:
                    return [i, s]
            error = True

def csv_convert_picolog():
    filename = getFileName()
    
    r_s = float(input("Enter series resistor value (Ω): "))
    v_t = float(input("Enter input voltage (V): "))
    
    data = []
    #open csv
    try:
        with open(filename, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                data += [row]
    except:
        print("ERROR: Could not open", filename)
        return False
    
    #get fieldnames (titles) in csv file
    fieldnames = []
    for key, value in data[0].items():
        fieldnames += [key]
    
    #reference is a length 2 array containing the index of the reference fieldname in the fieldnames array, and the reference fieldname
    reference = get_reference_temp_field(fieldnames, filename)
    #v_fieldnames is a copy of the fieldnames array but without the reference fieldname
    v_fieldnames = fieldnames[0:reference[0]] + fieldnames[reference[0]+1:len(fieldnames)]
    
    #convert voltage (V) to temperature (°C)
    #for each ordered dictionary (obj) in data (iterating through the rows)
    for obj in data:
        #ref is the reference temperature
        ref = R_to_T_positive(voltage_divider(float(obj[reference[1]]), v_t, r_s))
        #first column contains timestamp, do not convert this, so start for loop at 1
        for i in range(1, len(v_fieldnames), 1):
            #Note: In the csv file, voltage is given in V, not mV, so multiply by 1000
            obj[v_fieldnames[i]] = str(calculate_temp(float(obj[v_fieldnames[i]])*1000, ref))
        obj[reference[1]] = ref
    
    #check if csv file with converted values already exists, and if it does, overwrite
    new_path = filename[0:len(filename)-4] + "_converted" + ".csv"
    try:
        if os.path.exists(new_path):
            os.remove(new_path)
    except:
        print("ERROR: WinError 32; please close", new_path, "if open.")
        return False
    
    #create a new csv file for converted values
    with open(new_path, mode='w', newline = '') as csv_output:
        writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
        writer.writeheader()
        for d in data:
            writer.writerow(d)

    a = input("Convert successful. Press any key to continue.")
    return True

#######################################################################################
# OTHER CSV FUNCTIONS

def csv_convert_thermocouple_only():
    error = False
    while True:
        try:
            r = float(input("Enter fixed reference temperature (°C): "))
            error = False
        except:
            print("ERROR: Invalid Temperature")
            error = True
        if error == False:
            break

    filename = getFileName()
    data = []
    #open csv
    try:
        with open(filename, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                data += [row]
    except:
        print("ERROR: Could not open", filename)
        return False
    
    #get fieldnames (titles) in csv file
    fieldnames = []
    for key, value in data[0].items():
        fieldnames += [key]
    
    #convert voltage (mV) to temperature (°C)
    for obj in data:
        #first column contains timestamp, do not convert this, so start for loop at 1
        for i in range(1, len(fieldnames), 1):
            #Note: In the csv file, voltage is given in V, not mV, so multiply by 1000
            obj[fieldnames[i]] = str(calculate_temp(float(obj[fieldnames[i]])*1000, r))
    
    #check if csv file with converted values already exists, and if it does, overwrite
    new_path = filename[0:len(filename)-4] + "_converted_" + str(r) + ".csv"
    try:
        if os.path.exists(new_path):
            os.remove(new_path)
    except:
        print("ERROR: WinError 32; please close", new_path, "if open.")
        return False
    
    #create a new csv file for converted values
    with open(new_path, mode='w', newline = '') as csv_output:
        writer = csv.DictWriter(csv_output, fieldnames=fieldnames)
        writer.writeheader()
        for d in data:
            writer.writerow(d)

    a = input("Convert successful. Press any key to continue.")
    return True

#######################################################################################
# MAIN

def filler():
    print("Sorry, function is unavailable at the moment.")
    a = input("Press any key to continue.")
    return True

def main():
    print("-------------------------------------------")
    print("      PICOLOG DATA CONVERSION PROGRAM")
    print("         Created by Matthew Leung")
    print("-------------------------------------------")

    s = range(0, 8, 1)
    while True:
        selection = -1
        error = False
        while True:
            print("Select mode:")
            print("--------------------------------------------------------------------")
            print("THERMOCOUPLE")
            print("0 - Direct Conversion - Type T Thermocouple mV to °C (NIST)")
            print("1 - Direct Conversion - Type T Thermocouple °C to mV (NIST)")
            print("2 - csv Conversion - with fixed known reference temperature")
            print("--------------------------------------------------------------------")
            print("RTD")
            print("3 - Direct Conversion - Pt1000 RTD Ω to °C (ITS-90)")
            print("4 - Conversion - Pt1000 RTD with resistor in series (voltage divider)")
            print("5 - csv Conversion - with resistor in series (voltage divider)")
            print("--------------------------------------------------------------------")
            print("6 - csv Conversion - Picolog Data")
            print("7 - Quit")
            try:
                selection = int(input(""))
                if selection not in s:
                    print("ERROR: Invalid input\n")
                    error = True
                else:
                    error = False
            except:
                print("ERROR: Invalid input\n")
                error = True
            if error == False:
                if selection == 7:
                    print("End of program.")
                    return True
                break
        
        if selection == 0:
            TC_direct_converter_vtot()
        elif selection == 1:
            TC_direct_converter_ttov()
        elif selection == 2:
            csv_convert_thermocouple_only()
        elif selection == 3:
            RTD_direct_converter()
        elif selection == 4:
            RTD_voltdivide_converter()
        elif selection == 5:
            filler()
        elif selection == 6:
            csv_convert_picolog()
        elif selection == 7:
            break
        print("\n")

    return True

if __name__ == "__main__":
    main()
