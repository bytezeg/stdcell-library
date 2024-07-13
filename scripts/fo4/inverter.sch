v {xschem version=3.0.0 file_version=1.2 }
G {}
K {}
V {}
S {}
E {}
N 210 -180 210 -150 { lab=out}
N 150 -120 170 -120 { lab=in}
N 150 -210 150 -120 { lab=in}
N 150 -210 170 -210 { lab=in}
N 130 -160 150 -160 { lab=in}
N 210 -160 250 -160 { lab=out}
N 210 -250 210 -240 { lab=vdd}
N 210 -90 210 -70 { lab=vss}
N 210 -120 290 -120 { lab=vss}
N 290 -120 290 -80 { lab=vss}
N 210 -80 290 -80 { lab=vss}
N 210 -260 210 -250 { lab=vdd}
N 210 -210 290 -210 { lab=vdd}
N 290 -250 290 -210 { lab=vdd}
N 210 -250 290 -250 { lab=vdd}
C {sky130_fd_pr/pfet_01v8.sym} 190 -210 0 0 {name=M1
L=0.15
W=pp
nf=1
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=pfet_01v8
spiceprefix=X
}
C {sky130_fd_pr/nfet_01v8.sym} 190 -120 0 0 {name=M2
L=0.15
W=pn
nf=1 
mult=1
ad="'int((nf+1)/2) * W/nf * 0.29'" 
pd="'2*int((nf+1)/2) * (W/nf + 0.29)'"
as="'int((nf+2)/2) * W/nf * 0.29'" 
ps="'2*int((nf+2)/2) * (W/nf + 0.29)'"
nrd="'0.29 / W'" nrs="'0.29 / W'"
sa=0 sb=0 sd=0
model=nfet_01v8
spiceprefix=X
}
C {devices/opin.sym} 250 -160 0 0 {name=p1 lab=out}
C {/home/nelson/cad/share/xschem/xschem_library/devices/ipin.sym} 130 -160 0 0 {name=p2 lab=in}
C {/home/nelson/cad/share/xschem/xschem_library/devices/iopin.sym} 210 -260 3 0 {name=p3 lab=vdd}
C {/home/nelson/cad/share/xschem/xschem_library/devices/iopin.sym} 210 -70 1 0 {name=p4 lab=vss}
