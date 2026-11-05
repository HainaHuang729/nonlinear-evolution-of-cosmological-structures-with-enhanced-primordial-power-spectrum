# Particle-binned halo density profiles (2026-11-05)

- Source runs: `PL/PL_25_1024`, `bluetilted/kp_1_ms_1.5_25_1024`, `bluetilted/kp_10_ms_1.5_25_1024`
- Snapshot 0056, SOAP `halo_properties_0056.hdf5`
- Box: 25 h^-1 Mpc = 37.1 Mpc physical; DM particle mass 1.89e6 Msun
- Two centres: `SO/200_mean/CentreOfMass` and `BoundSubhalo/CentreOfMass`
- Mass bins: 1e9, 1e10, 1e11, 1e12 Msun (5 central halos each); 1e8 omitted (N200 ~ 50)
- Shells: 20 logarithmic bins in r/R200m from 0.01 to 1; `count` gives particles per shell
- Figure: `halo-density-radial-particles-bt-pl.png` (PL black, BTKP1 blue, BTKP10 green; bottom panels BT/PL)
