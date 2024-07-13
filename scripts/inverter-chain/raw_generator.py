import subprocess

corners = [
"VACIO",
"tt",
"sf",
"ff",
"ss",
"fs",
"ll",
"hh",
"hl",
"lh",
]


def change_file(old_value,new_value):
  """
  This function receives the characters of the old and next corner as strings.
  It extracts the file lines and save them in a list. 
  Once finds specific lines with old corner, then replaces it with the next corner.
  Finally, it writes all the list elements into the file.
  """

  with open("tb_realistic_source.spice", "r") as file:
    lines = file.readlines() # saves all file lines as a list.
        
    for i, line in enumerate(lines):
      if (".lib /home/nelson/cad/share/pdk/sky130A/libs.tech/ngspice/sky130.lib.spice "+old_value) in line:
        lines[i] = line.replace(old_value, new_value)
      if "write data_rs_"+old_value+".raw wnv wpv trv tfv" in line:
        lines[i] = line.replace("data_rs_"+old_value+".raw", "data_rs_"+new_value+".raw")

  with open("tb_realistic_source.spice", "w") as file:
    file.writelines(lines) # write all list elements into the file.


#Cambio de archivo y ejecución del programa


for i in range(len(corners)): # runs over the 18 corners to apply the function "change_file"
  if i>0:
    print("Corriendo para el corner: "+corners[i])    
    change_file(corners[i-1],corners[i]) # modify file
    subprocess.run(["ngspice", "-b", "tb_realistic_source.spice"]) # run file


change_file("lh","VACIO") # resets the original spice file.

