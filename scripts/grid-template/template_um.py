import sys

tech = input('Choose tech: sky130/gf180: ')

if (tech == "sky130"):
  hp = input("Enter height pitch [um]: ")
  if hp:
    hp = float(hp)
  else:
    hp = 0.34 # minimum height pitch in sky130
  wp = input("Enter width pitch [um]: ")
  if wp:
    wp = float(wp)
  else:
    wp = 0.46 # minimum width pitch in sky130
  print(f'>> Width pitch: {wp} um')
  print(f'>> Height pitch: {hp} um')
  
  ht = int(input("Enter cell height [tracks]: ")) + 1 # Draw an additional track for the next cell above.
  wt = int(input("Enter width tracks to draw: "))

  with open(f'template_{tech}_{ht}_{wt}.tcl', 'w') as f:
    f.write("#!/usr/bin/tclsh\n")
    f.write("scalegrid 1 2\n")
    f.write("grid 0.005um 0.005um\n")
    f.write("snap grid\n")
    for i in range(ht):
      f.write(f"element add line track_height_{i} black 0 {i*hp:.2f}um {(wt-1)*wp:.2f}um {i*hp:.2f}um\n")
    f.write("\n")
    for i in range(wt):
      f.write(f"element add line track_width_{i} black {i*wp:.2f}um 0 {i*wp:.2f}um {(ht-1)*hp:.2f}um\n")
else: 
  print('No tech available')
