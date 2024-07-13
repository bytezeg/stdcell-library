v {xschem version=3.0.0 file_version=1.2 }
G {}
K {}
V {}
S {}
E {}
N 160 -840 160 -820 { lab=VDD}
N 230 -840 230 -820 { lab=VSS}
N 230 -760 230 -750 { lab=GND}
N 230 -750 230 -740 { lab=GND}
N 160 -760 160 -740 { lab=GND}
N 80 -350 80 -340 { lab=GND}
N 80 -340 80 -330 { lab=GND}
N 80 -450 80 -410 { lab=vin}
N 540 -210 552 -210 { lab=in}
N 610 340 610 360 { lab=VDD}
N 610 480 610 500 { lab=VSS}
N 160 -530 310 -530 { lab=vin}
N 610 30 610 50 { lab=VDD}
N 610 170 610 190 { lab=VSS}
N 720 110 740 110 { lab=out2}
N 610 -290 610 -270 { lab=VDD}
N 610 -150 610 -130 { lab=VSS}
N 370 -610 370 -590 { lab=VDD}
N 370 -470 370 -450 { lab=VSS}
N 610 -610 610 -590 { lab=VDD}
N 610 -470 610 -450 { lab=VSS}
N 780 -530 800 -530 { lab=out}
N 720 420 740 420 { lab=out1}
N 860 -610 860 -590 { lab=VDD}
N 860 -470 860 -450 { lab=VSS}
N 970 -530 990 -530 { lab=out6}
N 780 -770 800 -770 { lab=out}
N 860 -850 860 -830 { lab=VDD}
N 860 -710 860 -690 { lab=VSS}
N 970 -770 990 -770 { lab=out7}
N 780 -1020 800 -1020 { lab=out}
N 860 -1100 860 -1080 { lab=VDD}
N 860 -960 860 -940 { lab=VSS}
N 970 -1020 990 -1020 { lab=out8}
N 780 -1270 800 -1270 { lab=out}
N 860 -1350 860 -1330 { lab=VDD}
N 860 -1210 860 -1190 { lab=VSS}
N 970 -1270 990 -1270 { lab=out9}
N 720 -530 780 -530 { lab=out}
N 760 -770 780 -770 { lab=out}
N 760 -770 760 -530 { lab=out}
N 760 -1020 760 -770 { lab=out}
N 760 -1020 780 -1020 { lab=out}
N 760 -1270 760 -1020 { lab=out}
N 760 -1270 780 -1270 { lab=out}
N 480 -530 550 -530 { lab=in}
N 720 -210 750 -210 { lab=out3}
N 740 110 750 110 { lab=out2}
N 740 420 750 420 { lab=out1}
N 510 -530 510 -220 { lab=in}
N 510 -220 510 -210 { lab=in}
N 510 -210 540 -210 { lab=in}
N 510 -210 510 110 { lab=in}
N 510 110 550 110 { lab=in}
N 510 110 510 420 { lab=in}
N 510 420 550 420 { lab=in}
N 80 -530 80 -450 { lab=vin}
N 80 -530 160 -530 { lab=vin}
C {devices/vsource.sym} 230 -790 0 0 {name=V1 value=0}
C {devices/vsource.sym} 160 -790 0 0 {name=V2 value=1.8}
C {devices/vdd.sym} 230 -840 0 0 {name=l1 lab=VSS}
C {devices/vdd.sym} 160 -840 0 0 {name=l2 lab=VDD}
C {devices/gnd.sym} 160 -740 0 0 {name=l6 lab=GND}
C {devices/gnd.sym} 230 -740 0 0 {name=l7 lab=GND}
C {devices/vsource.sym} 80 -380 0 0 {name=V3 value="DC 0 PULSE(0 1.8 0 80.9315ps 80.9315ps 1ns 2ns 0)
"}
C {devices/gnd.sym} 80 -330 0 0 {name=l12 lab=GND}
C {devices/code.sym} 370 -820 0 0 {name=control 

only_toplevel=false 

value="

.param pp = 2.81
.param pn = 0.88

********************************
* Control section
********************************
.control

* Voltage values to calculate rise and fall times
let v_steady = 1.8
let per10 = v_steady * 0.1
let per90 = v_steady * 0.9
let per50 = v_steady * 0.5

* Run transient analysis
TRAN 1p 6n $ 3 periods

* Find rise and fall times
echo
meas  TRAN  t_rise  TRIG  v(out) VAL=per10 RISE=2  TARG v(out)  VAL=per90 RISE=2
meas  TRAN  t_fall  TRIG  v(out) VAL=per90 FALL=2  TARG v(out)  VAL=per10 FALL=2
echo
echo ********************************** End of Simulation **********************************
echo

* Export vector data into raw file
* write data_VACIO.raw wnv wpv trv tfv

* Plot both rise and fall times vs. NMOS widths
plot out in
.endc



"}
C {devices/code.sym} 370 -980 0 0 {name=models 
only_toplevel=false 
format="tcleval( @value )"
value="
.lib \\\\$::SKYWATER_MODELS\\\\/sky130.lib.spice lh

.param mc_mm_switch=0
.param mc_pr_switch=1

"

}
C {devices/vdd.sym} 610 340 0 0 {name=l5 lab=VDD}
C {devices/vdd.sym} 610 500 2 0 {name=l8 lab=VSS}
C {inverter.sym} 620 420 0 0 {name=x1}
C {devices/vdd.sym} 610 30 0 0 {name=l3 lab=VDD}
C {devices/vdd.sym} 610 190 2 0 {name=l4 lab=VSS}
C {inverter.sym} 620 110 0 0 {name=x2}
C {devices/vdd.sym} 610 -290 0 0 {name=l9 lab=VDD}
C {devices/vdd.sym} 610 -130 2 0 {name=l10 lab=VSS}
C {inverter.sym} 620 -210 0 0 {name=x3}
C {devices/vdd.sym} 370 -610 0 0 {name=l11 lab=VDD}
C {devices/vdd.sym} 370 -450 2 0 {name=l13 lab=VSS}
C {inverter.sym} 380 -530 0 0 {name=x4}
C {devices/vdd.sym} 610 -610 0 0 {name=l14 lab=VDD}
C {devices/vdd.sym} 610 -450 2 0 {name=l15 lab=VSS}
C {inverter.sym} 620 -530 0 0 {name=x5}
C {devices/vdd.sym} 860 -610 0 0 {name=l16 lab=VDD}
C {devices/vdd.sym} 860 -450 2 0 {name=l17 lab=VSS}
C {inverter.sym} 870 -530 0 0 {name=x6}
C {devices/vdd.sym} 860 -850 0 0 {name=l18 lab=VDD}
C {devices/vdd.sym} 860 -690 2 0 {name=l19 lab=VSS}
C {inverter.sym} 870 -770 0 0 {name=x7}
C {devices/vdd.sym} 860 -1100 0 0 {name=l20 lab=VDD}
C {devices/vdd.sym} 860 -940 2 0 {name=l21 lab=VSS}
C {inverter.sym} 870 -1020 0 0 {name=x8}
C {devices/vdd.sym} 860 -1350 0 0 {name=l22 lab=VDD}
C {devices/vdd.sym} 860 -1190 2 0 {name=l23 lab=VSS}
C {inverter.sym} 870 -1270 0 0 {name=x9}
C {devices/opin.sym} 990 -770 0 0 {name=p1 lab=out7
}
C {devices/opin.sym} 990 -530 0 0 {name=p2 lab=out6}
C {devices/opin.sym} 990 -1020 0 0 {name=p3 lab=out8}
C {devices/opin.sym} 990 -1270 0 0 {name=p4 lab=out9}
C {devices/lab_pin.sym} 190 -530 1 0 {name=l24 sig_type=std_logic lab=vin
}
C {devices/lab_pin.sym} 770 -1270 1 0 {name=l26 sig_type=std_logic lab=out}
C {devices/opin.sym} 750 -210 0 0 {name=p5 lab=out3}
C {devices/opin.sym} 750 110 0 0 {name=p6 lab=out2
}
C {devices/opin.sym} 750 420 0 0 {name=p7 lab=out1

}
C {devices/lab_pin.sym} 500 -530 1 0 {name=l25 sig_type=std_logic lab=in}
