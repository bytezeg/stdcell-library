v {xschem version=3.0.0 file_version=1.2 }
G {}
K {}
V {}
S {}
E {}
N 160 -380 160 -360 { lab=VDD}
N 230 -380 230 -360 { lab=VSS}
N 230 -300 230 -290 { lab=GND}
N 230 -290 230 -280 { lab=GND}
N 160 -300 160 -280 { lab=GND}
N 70 -110 70 -100 { lab=GND}
N 70 -100 70 -90 { lab=GND}
N 270 -210 310 -210 { lab=vin}
N 70 -210 190 -210 { lab=vin}
N 70 -210 70 -170 { lab=vin}
N 310 -210 322 -210 { lab=vin}
N 380 -310 380 -290 { lab=VDD}
N 380 -120 380 -100 { lab=VSS}
N 190 -210 270 -210 { lab=vin}
N 540 -210 552 -210 { lab=out1}
N 610 -310 610 -290 { lab=VDD}
N 610 -120 610 -100 { lab=VSS}
N 530 -210 540 -210 { lab=out1}
N 770 -210 782 -210 { lab=out2}
N 840 -310 840 -290 { lab=VDD}
N 840 -120 840 -100 { lab=VSS}
N 760 -210 770 -210 { lab=out2}
N 990 -210 1010 -210 { lab=out3}
C {devices/vsource.sym} 230 -330 0 0 {name=V1 value=0}
C {devices/vsource.sym} 160 -330 0 0 {name=V2 value=1.8}
C {devices/vdd.sym} 230 -380 0 0 {name=l1 lab=VSS}
C {devices/vdd.sym} 160 -380 0 0 {name=l2 lab=VDD}
C {devices/gnd.sym} 160 -280 0 0 {name=l6 lab=GND}
C {devices/gnd.sym} 230 -280 0 0 {name=l7 lab=GND}
C {devices/vsource.sym} 70 -140 0 0 {name=V3 value="

DC 0 PULSE(0 1.8 0 0.05ns 0.05ns 0.15ns 0.5ns)

"}
C {devices/gnd.sym} 70 -90 0 0 {name=l12 lab=GND}
C {devices/code.sym} 540 -490 0 0 {name=control 

only_toplevel=false 

value="

.param pp = 3.27
.param pn = 0.42

********************************
* Control section
********************************
.control

* Voltage values to calculate rise and fall times
let v_steady = 1.8
let per10 = v_steady * 0.1
let per90 = v_steady * 0.9
let per50 = v_steady * 0.5

* These limits are based on the design of a standard cell of 12 tracks.
let wp_max = 1.85
let wn_min = 0.41
let wp_min = 0.42
let wn_max = 1.84

* Initialization of variables and size of iteration.
let delta_w = 0.005
let wp = wp_max
let wn = wn_min
let loop = 0

* These vector will be used to save the data of each iteration.
let loops = (wp_max-wn_min)/delta_w
let wpv = unitvec($&loops)
let wnv = unitvec($&loops)
let trv = unitvec($&loops)
let tfv = unitvec($&loops)

* Start loop
while wp ge wp_min

* Modify widths
  echo
  echo ********************************** Cycle $&loop **********************************
  echo
  alterparam pp = $&wp
  reset
  alterparam pn = $&wn
  reset

* Run transient analysis
  TRAN 0.01n 1.5n $ 3 periods

* Find rise and fall times
  echo
  meas  TRAN  t_rise  TRIG  v(out2) VAL=per10 RISE=2  TARG v(out2)  VAL=per90 RISE=2
  meas  TRAN  t_fall  TRIG  v(out2) VAL=per90 FALL=2  TARG v(out2)  VAL=per10 FALL=2
  echo Wn: $&wn
  echo Wp: $&wp
  echo

* Save widths, t_rise, t_fall in vectors
  let wnv[loop] = wn
  let wpv[loop] = wp
  let trv[loop] = t_rise
  let tfv[loop] = t_fall

* Modify widths
  let wn = wn + delta_w
  let wp = wp - delta_w

* Counter increment
  let loop = loop + 1

end

echo
echo ********************************** End of Simulation **********************************
echo

* Export vector data into raw file
write data_rvs_VACIO.raw wnv wpv trv tfv

* Plot both rise and fall times vs. NMOS widths
* plot trv vs wnv, tfv vs wnv
.endc



"}
C {devices/code.sym} 680 -490 0 0 {name=models 
only_toplevel=false 
format="tcleval( @value )"
value="
.lib \\\\$::SKYWATER_MODELS\\\\/sky130.lib.spice VACIO

.param mc_mm_switch=0
.param mc_pr_switch=1

"

}
C {devices/vdd.sym} 380 -310 0 0 {name=l3 lab=VDD}
C {inverter.sym} 410 -210 0 0 {name=x1}
C {devices/vdd.sym} 380 -100 2 0 {name=l4 lab=VSS}
C {devices/vdd.sym} 610 -310 0 0 {name=l5 lab=VDD}
C {inverter.sym} 640 -210 0 0 {name=x2}
C {devices/vdd.sym} 610 -100 2 0 {name=l8 lab=VSS}
C {devices/vdd.sym} 840 -310 0 0 {name=l9 lab=VDD}
C {inverter.sym} 870 -210 0 0 {name=x3}
C {devices/vdd.sym} 840 -100 2 0 {name=l10 lab=VSS}
C {devices/opin.sym} 1010 -210 0 0 {name=p1 lab=out3}
C {devices/lab_pin.sym} 770 -210 1 0 {name=l11 sig_type=std_logic lab=out2
}
C {devices/lab_pin.sym} 540 -210 1 0 {name=l13 sig_type=std_logic lab=out1}
C {devices/lab_pin.sym} 270 -210 1 0 {name=l14 sig_type=std_logic lab=vin}
