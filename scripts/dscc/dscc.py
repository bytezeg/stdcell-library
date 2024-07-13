

import sys
import os
import argparse
import numpy as np
import glob
import subprocess
from PyLTSpice import RawRead as RawRead
from tabulate import tabulate

# --------------------------------------------------------------------------------------------
#
# TOOL BANNER
#
# --------------------------------------------------------------------------------------------

print("""
                    ___           ___           ___     
     _____         /\__\         /\__\         /\__\    
    /::\  \       /:/ _/_       /:/  /        /:/  /    
   /:/\:\  \     /:/ /\  \     /:/  /        /:/  /     
  /:/  \:\__\   /:/ /::\  \   /:/  /  ___   /:/  /  ___ 
 /:/__/ \:|__| /:/_/:/\:\__\ /:/__/  /\__\ /:/__/  /\__\\
 \:\  \ /:/  / \:\/:/ /:/  / \:\  \ /:/  / \:\  \ /:/  /
  \:\  /:/  /   \::/ /:/  /   \:\  /:/  /   \:\  /:/  / 
   \:\/:/  /     \/_/:/  /     \:\/:/  /     \:\/:/  /  
    \::/  /        /:/  /       \::/  /       \::/  /   
     \/__/         \/__/         \/__/         \/__/    
""")

print("""DIGITAL STANDARD CELL CHARACTERIZER""")

print("""
Author: Nelson Rodriguez
Status: The tool only characterizes combinational cells.
""")

# --------------------------------------------------------------------------------------------
# 
# COMMAND LINE ARGUMENTS PROCESSING
#
# --------------------------------------------------------------------------------------------

# Warning if bad use 
if len(sys.argv) < 2:
  print("Please provide file name as command line argument")
  sys.exit()

# Create the argument parser
parser = argparse.ArgumentParser(description='Process input arguments.')

# Add the input file argument
parser.add_argument('cell_file', type=str, help='Magic file of cell layout')
parser.add_argument('--sky130-root', type=str, default='/usr/local', help='Spice models for sky130 pdk')
parser.add_argument('--output-loads', type=str, required=True, help='Comma-separated list of output loads')
parser.add_argument('--slew-rates', type=str, required=True, help='Comma-separated list of slew rates')

args = parser.parse_args()

input_file = args.cell_file
output_loads = [x for x in args.output_loads.split(',')]
slew_rates = [x for x  in args.slew_rates.split(',')]
sky130_root = args.sky130_root


# --------------------------------------------------------------------------------------------
#
# CELL EXTRACTION
#  
# --------------------------------------------------------------------------------------------

filename = input_file
# print(input_file)
if filename.endswith(".mag"):
    filename = filename[:-4]

useless_cat_call = subprocess.Popen(["magic", "-dnull", "-noconsole", input_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) # run file

output, errors = useless_cat_call.communicate(
    input="extract do local\nextract all\n\next2sim labels on\next2sim\n\nextresist tolerance 1000000\nextresist\n\next2spice lvs\next2spice cthresh 0\next2spice extresist on\next2spice\n\nquit\n")
useless_cat_call.wait()
# print(output)
# print(errors)


# Set the file extensions and filenames to delete
extensions_to_delete = [".ext"]
files_to_delete = [filename+".nodes", filename+".sim"]

# Delete files with the specified extensions
for ext in extensions_to_delete:
    for file in os.listdir():
        if file.endswith(ext):
            os.remove(file)

# Delete the specified files
for file in files_to_delete:
    try:
        os.remove(file)
    except OSError:
        pass


# --------------------------------------------------------------------------------------------
#
# SPICE PARSER
# 
# --------------------------------------------------------------------------------------------

with open(f'{filename}.spice') as f:
  content = f.readlines() # read file

  subckt_line = content[2].strip() # removes leading/trailing whitespaces
  cell = subckt_line.split()[1] 
  inputs = subckt_line.split()[2:-3] # a list with the inputs
  output = subckt_line.split()[-3] # a list with the outputs
  vdd_node = subckt_line.split()[-2]
  gnd_node = subckt_line.split()[-1]

print("\n\n")
print(">>> Cell: ", cell)
print(">>> Input Ports: ", inputs)
print(">>> Output Ports: ", output)
print(">>> VDD node: ", vdd_node)
print(">>> GND node: ", gnd_node)
print(">>> Slew Rates: ", slew_rates)
print(">>> Output Loads: ", output_loads)







# --------------------------------------------------------------------------------------------
#
# LOGIC IDENTIFICATION
# 
# --------------------------------------------------------------------------------------------

out_node = output

if len(inputs) == 1:
    num_pmos = 0
    for line in content:
        if line.startswith('X') and 'pfet' in line: # identifies lines of PMOS devices
            num_pmos += 1
    if num_pmos%2 == 0: # If the number of pmos devices is even, then it is a buffer
        boolean_function = f'{inputs[0]}'
        print(f">>> Boolean Function: {boolean_function}")
    else:  # If the number of pmos devices is odd, then it is an inverter
        boolean_function = f'!{inputs[0]}'
        print(f">>> Boolean Function: {boolean_function}")
else:
    # Create the dictionary of PMOS
    p_dict = {}
    for line in content:
        if line.startswith('X') and 'pfet' in line: # identifies lines of PMOS devices
            split_line = line.split()
            key = split_line[2].split('.')[0] # The [2nd] string is the gate. The logic variable is before the dot.
            # print('KEY:', key)
            value = [split_line[1], split_line[3]] # Drain[1] and Source[3] nodes
            # print(value,'\n')
            nodes = []
            for element in value: # This for replaces nodes as VPWR.t0, VPWR.t3, etc to just VPWR. The same for Y.t3, Y.t2 to just Y.
                if "VPWR" in element: nodes.append("VPWR")
                elif "Y" in element: nodes.append("Y")
                else: nodes.append(element)
            # print(nodes,'\n')
            p_dict[key] = nodes # Gate ID = [Drain, Source]

    # print(">>> Original: ", p_dict, '\n\n')

    # Do the replacements per logical operation
    operation = 0 # even to parallel, odd to serie
    end_while = False

    while len(p_dict) != 1:
    # for i in range(10):
        flag_parallel = False
        flag_serie = False

        for i, (dev1, nodes1) in enumerate(p_dict.items()): # Takes one device

            for j, (dev2, nodes2) in enumerate(p_dict.items()): # And compare it with this one

                flag_serie_next = False # When it's true, the next operation to be evaluated will be a series array

                if dev1 != dev2 and set(nodes1) == set(nodes2) and operation%2 == 0: # It's a flag: when operation is 0,2,4,6 the current operation to evaluate is parallel

                    # print(f"Devices to multiply: {dev1} and {dev2} with common nodes {nodes1}")

                    # String game to write the logical expression:
                    if '|' in dev1 and '|' in dev2:
                        p_dict[f"({dev1}) & ({dev2})"] = nodes1
                    elif '|' in dev1:
                        p_dict[f"({dev1}) & {dev2}"] = nodes1
                    elif '|' in dev2:
                        p_dict[f"{dev1} & ({dev2})"] = nodes1
                    else:
                        p_dict[f"{dev1} & {dev2}"] = nodes1


                    # if '&' in dev1 and '|' in dev1 and '&' in dev2 and '|' in dev2:
                    #     p_dict[f"({dev1}) & ({dev2})"] = nodes1
                    # # if set(nodes1) == {'VDD', 'out'}:
                    # #     p_dict[f"({dev1}) & ({dev2})"] = nodes1
                    # elif '&' in dev1 and '|' in dev1: 
                    #     p_dict[f"({dev1}) & {dev2}"] = nodes1
                    # elif '&' in dev2 and '|' in dev2: 
                    #     p_dict[f"{dev1} & ({dev2})"] = nodes1
                    # else:
                    #     p_dict[f"{dev1} & {dev2}"] = nodes1
                        
                    # print(f"Product found: {dev1} & {dev2}")
                    del p_dict[dev1]
                    del p_dict[dev2]
                    flag_parallel = True
                    # print(f">>>> DICTIONARY: {p_dict}\n\n")
                    break 

                common_node = list(set(nodes1).intersection(set(nodes2))) # When it reaches this point is because the second device is not in parallel with the first one

                if dev1 != dev2 and len(common_node) == 1 and vdd_node not in common_node[0].split('.')[0] and out_node not in common_node[0].split('.')[0] and operation%2 != 0:
                    for dev3, nodes3 in p_dict.items():
                        if dev1 != dev3 and dev2 != dev3 and common_node[0] in nodes3: # if found a third device connected
                            flag_serie_next = True
                            break
                    if flag_serie_next:
                        continue # change dev2
                    # print(f"Devices to sum: {dev1} and {dev2} with common node {common_node}")
                    # print('Device that cause the error:', dev3, ' with nodes:', nodes3)
                    nodes1.remove(common_node[0])
                    nodes2.remove(common_node[0])
                    p_dict[f"{dev1} | {dev2}"] = nodes1 + nodes2
                    # print(f"Series found: {dev1} | {dev2}")
                    del p_dict[dev1]
                    del p_dict[dev2]
                    flag_serie = True
                    # print(f">>>> DICTIONARY: {p_dict}\n\n")
                    break

                if i+j == 2*(len(p_dict)-1): # Life of change of operation
                    operation += 1
                    # print(i,j, "**** CHANGE OF OPERATION **** \n\n")
                    end_while = True

                if flag_serie == True:
                    break                

                if flag_serie_next:
                    continue

            if flag_parallel or flag_serie:
                break # Each time the script founds a parallel or series array it starts from the beginning like working with a new schematic

    # print(">>> Final dictionary:", p_dict, "\n\n")
    # print(f"Logical Function of Cell: Y = {[key for key in p_dict.keys()]}\n\n")
    # print(f"!({list(p_dict.keys())[0]})")
    boolean_function = f"!({list(p_dict.keys())[0]})"
    print(f">>> Boolean Function: {boolean_function}")


# --------------------------------------------------------------------------------------------
#
# FOLDER CREATION TO SAVE THE CHARACTERIZATION DATA
#
# --------------------------------------------------------------------------------------------

if not os.path.exists(cell):
  os.makedirs(cell) # create directory for output files
  print(">>> Characterization folder '",cell, "' has been created to save output data.")

# --------------------------------------------------------------------------------------------
#
# NGSPICE FILES CREATION
#
# Using a for loop, this section creates an ngspice file per pin that:
# 1. Find the input combination that makes the output a function of only that pin: Y = F(PIN)
# 2. Calculates the rise time, fall time, propagation delay when pin transition from 0 to 1.8v
# 3. Calculates the power .... ????
# 4. Export all this data into a file .raw for post-processing.
#
# --------------------------------------------------------------------------------------------


# 1.NETLIST CREATION      
#####################

# 1.1 FILE CREATION PER PIN
############################

for pin in inputs:

  # Naming output file per pin
  pin_file = os.path.join(cell, f"{cell}_{pin}.spice") 

  # Creates a file per pin
  with open(pin_file, "w") as f: 
    f.write(f"* Characterization pin {pin} of cell {cell}")
  
# 1.2 MODELS   
#############

    f.write(f"""

******************
* Model libraries
******************

.lib {sky130_root}/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice tt
.param mc_mm_switch = 0
.param mc_pr_switch = 1
.include ../{cell}.spice

******************
* Circuit Netlist
******************

""")

# 1.3 NETLIST 
##############

    # Power supplies
    f.write("vpwr vdd 0 dc 1.8\n")
    f.write("vgnd vss 0 dc 0\n")

    # Parameter
    f.write(".param sr = 1n\n")

    # Pulse voltage source for the pin to characterize
    f.write(f"v{pin} {pin} vss dc 0 pulse(0 1.8 0 'sr' 'sr' 100n 200n 0)\n")

    # Voltage source at 0 for remaining pins
    for other in inputs:
      if other != pin:
        f.write(f"v{other} {other} vss dc 0\n")    

    # Cell instance in the netlist
    f.write(f"xcell {' '.join(inputs)} out vdd vss {cell}\n")

    # Load capacitance
    f.write("cl out vss 1p\n")

# 1.4 CONTROL
##############

    f.write("""
**********
* Control
**********

""")
    
    ###########################################################################
    # INPUT ASSIGNATIONS

    f.write(".control\n")
    other_pins = [other for other in inputs if other != pin] # list with remaining input pins
    f.write(f"let remaining_ports = {len(other_pins)}\n") # vector equals to the quantity of remaining pins
    f.write("let combinations = 2^remaining_ports\n") # vector equals to the possible logical combinations of remaining pins
    f.write("let n = 0\n") # vector to index in vectors: tr_table, tf_table, td_table
    f.write("echo I entered in the control section\n")

# Constant vectors

    f.write(f"""
let v_steady = 1.8
let per10 = v_steady * 0.1
let per90 = v_steady * 0.9
let per50 = v_steady * 0.5

* Initialization of scalars and size of iteration.
let total_c_values = {len(output_loads)} 
let total_slew_rates = {len(slew_rates)} 
let total_values_table = total_c_values * total_slew_rates

* Vector declarations to save the data of each iteration.
let table_tr = unitvec($&total_values_table)
let table_tf = unitvec($&total_values_table)
let table_tphl = unitvec($&total_values_table)
let table_tplh = unitvec($&total_values_table)
let loop = 0\n""")

# Loop for combinations
    if len(other_pins) > 0:
      f.write("while n < combinations\n")
      f.write("  tran 1n 200n\n")
      for other in other_pins:
        f.write(f"  print {other}[0]\n")
      f.write("  meas tran avg_out avg out from=0 to=200n\n")
      f.write("  if avg_out > 0.2 and avg_out < 1.7\n")
      f.write(f"    plot {pin} out avg_out\n")
      f.write("    echo THIS IS THE ANSWER\n")
      for other in other_pins:
        f.write(f"    print {other}[0]\n")
      f.write("    break\n")
      f.write("  end\n")

      # Combinations
      f.write("\n")
      f.write("* Combinations\n")
      f.write(f"  alter v{other_pins[-1]} = vdd\n") # assign vdd to the latest reamining pin
      for index, other in enumerate(other_pins[1:]): # takes all remaining pins except the first (0 index), to avoid errors in the last line in this block.
        f.write(f"  if {' = vdd & '.join(other_pins[-index-1:])} = vdd\n") # sets AND condition from one port before the current, up to the last one.
        for j, other in enumerate(other_pins[-index-1:]): # takes from one port before the current, up to the last one.
          f.write(f"    alter v{other_pins[-j-1]} = 0\n") # assign 0 to them.
        f.write(f"    alter v{other_pins[-index-1-1]} = vdd\n") # assign vdd to the port 2 times ahead of the current one.
        f.write("  end\n\n")

      f.write("  let n = n + 1\n")
      f.write("end\n")

###########################################################################
# TIMING DATA


# Loops

    f.write(f"""
* Start loop for input net transition (slew rates)
foreach slew_rate_varloop {'n '.join(slew_rates)}n

* Modify input slew rate
  echo
  echo ********************************* Slew Rate $slew_rate_varloop *********************************
  echo
  alterparam sr = $slew_rate_varloop
  reset

* Start loop for load capacitances
  foreach cload_varloop {'p '.join(output_loads)}p

  * Modify load capacitance
    echo
    echo ********************************** Cload $cload_varloop **********************************
    echo
    alter cl = $cload_varloop

* Run transient analysis\n""")

# Transient analysis

    for other in other_pins:
      f.write(f"    alter v{other} = {other}\n")

    f.write(f"""
    TRAN 1n 400n $ 3 periods

* Find rise, fall and delay times
    echo
    meas TRAN t_rise  TRIG v(out) VAL=per10 RISE=2 TARG v(out) VAL=per90 RISE=2
    meas TRAN t_fall  TRIG v(out) VAL=per90 FALL=2 TARG v(out) VAL=per10 FALL=2
    meas TRAN t_phl TRIG v({pin}) VAL=per50 RISE=1 TARG v(out) VAL=per50 FALL=1
    meas TRAN t_plh TRIG v({pin}) VAL=per50 FALL=1 TARG v(out) VAL=per50 RISE=1
    echo
    echo TRAN measurement
    print t_rise
    print t_fall
    print t_phl
    print t_plh
    echo

* Save t_rise, t_fall and t_delay in vectors 
    let table_tr[loop] = t_rise 
    let table_tf[loop] = t_fall
    let table_tphl[loop] = t_phl
    let table_tplh[loop] = t_plh

* Counter increment
    let loop = loop + 1

* End loops
  end

end


echo
echo ********************************** End of Simulation **********************************
echo
echo This characterization was made for the pin {pin} of the cell {cell} under the input combination:\n""")

    for other in other_pins:
      f.write(f"print {other}[0]\n")

    f.write(f"""

* Export vector data into raw file
write {cell}/data_{cell}_{pin}_tt.raw table_tr table_tf table_tphl table_tplh
""")

    f.write(".endc\n")
    f.write(".end")


# --------------------------------------------------------------------------------------------
#
# RAW FILES CREATION (NGSPICE RUN)
#
# This section runs each ngspice file per pin, generating the respective raw files.
#
# --------------------------------------------------------------------------------------------

# print(f">>> Simulations has been started....")

# 2. RUNNING FILE CREATED
  with open('output.log', 'w') as f:
    subprocess.run(["ngspice", "-b", f"{cell}/{cell}_{pin}.spice"], stdout=f, stderr=f)
  print(f">>> Pin {pin} characterized. Files created: {cell}_{pin}.spice, data_{cell}_{pin}_tt.raw")
  
# 3. FINAL MESSAGE
print(f">>> Simulations has been completed.\n\n")


# --------------------------------------------------------------------------------------------
#
# TIMING DATA TABLES CREATION
#
# --------------------------------------------------------------------------------------------

with open(f'{cell}/{cell}_tt_table.txt', 'w') as f:
  f.write(f"""*****************************************
Characterization Data of Cell {cell}
*****************************************""")

  for pin in inputs:
    f.write(f"\n\n---------------- Timing Data for pin {pin} ----------------")
    data = RawRead(f"{cell}/data_{cell}_{pin}_tt.raw")
    tr = data.get_trace('table_tr').get_wave(0) 
    tf = data.get_trace('table_tf').get_wave(0) 
    tphl = data.get_trace('table_tphl').get_wave(0) 
    tplh = data.get_trace('table_tplh').get_wave(0) 
    tr = tr.reshape((len(slew_rates),len(output_loads)))
    tf = tf.reshape((len(slew_rates),len(output_loads)))
    tphl = tphl.reshape((len(slew_rates),len(output_loads)))
    tplh = tplh.reshape((len(slew_rates),len(output_loads)))
    times = [tr, tf, tphl, tplh]
    time_labels = ['Rise Time', 'Fall Time', 'Propagation High-Low', 'Propagation Low-High']

    for i, t in enumerate(times):
      table = []
      f.write(f"\n\n{time_labels[i]}\n")
      for i in range(len(t)):
        row = [slew_rates[i]] + list(t[i])
        table.append(row)
      f.write(tabulate(table, headers=output_loads))

   

# --------------------------------------------------------------------------------------------
#
# LIB FILE CREATION
#
# --------------------------------------------------------------------------------------------

with open(f'{cell}/{cell}_tt.lib', 'w') as f:

  f.write(f'cell ("{cell}")' + "{\n")
  f.write(f'\tpin ("{output}")' + "{\n")
  f.write(f'\t\tdirection : "output";\n')
  f.write(f'\t\tfunction : "{boolean_function}";\n')

  for pin in inputs:
    data = RawRead(f"{cell}/data_{cell}_{pin}_tt.raw")
    tr = data.get_trace('table_tr').get_wave(0) 
    tf = data.get_trace('table_tf').get_wave(0) 
    tphl = data.get_trace('table_tphl').get_wave(0) 
    tplh = data.get_trace('table_tplh').get_wave(0) 
    tr = tr.reshape((len(slew_rates),len(output_loads)))
    tf = tf.reshape((len(slew_rates),len(output_loads)))
    tphl = tphl.reshape((len(slew_rates),len(output_loads)))
    tplh = tplh.reshape((len(slew_rates),len(output_loads)))
    times = [tr, tf, tphl, tplh]
    time_labels = ['cell_fall', 'cell_rise', 'fall_transition', 'rise_transition']

    f.write("\t\ttiming () {\n")
    for i, t in enumerate(times):
      f.write(f"\t\t\t{time_labels[i]} ()" + "{\n")
      f.write(f'\t\t\t\tindex_1("{", ".join(slew_rates)}");\n')
      f.write(f'\t\t\t\tindex_2("{", ".join(output_loads)}");\n')
      inner_list = [", ".join(map(str,x)) for x in t]
      outter_list = '"' + '" \ \n\t\t\t\t\t"'.join(inner_list)
      f.write(f'\t\t\t\tvalues({outter_list}");\n')
      f.write("\t\t\t}\n") # time_parameter }
    f.write(f'\t\t\trelated_pin : "{pin}";\n')
    f.write(f'\t\t\ttiming_type : "combinational";\n')
    f.write("\t\t}\n") # timing }
  f.write("\t}\n") # output pin }
  f.write("}") # cell }
   
print(f"\n\n>>> LIB files has been created.")
print(f">>> Cell {cell} has been characterized.\n\n")
