# Particle-binned halo density profiles (2026-11-05)

## What changed relative to the original figure

The manuscript figure `halo-density-radial-n100-power.png` is produced by
`bt_plot_halo_density_radial_trial_png.py`: for every halo it takes the SOAP
concentration C200, draws the **analytic NFW profile** with that concentration,
and stacks the median over the haloes in a mass bin. That curve is therefore an
NFW by construction; the central shape, substructure and any deviation from NFW
are invisible, and comparing it to a theoretical NFW is largely circular.

The new figure uses the **simulation particles directly**:

1. read SOAP `halo_properties_0056.hdf5`; convert `SO/200_mean/TotalMass` with
   `U_M = 1e10 Msun` and `SORadius` with `U_L = 1 Mpc`;
2. keep central haloes (`InputHalos/IsCentral == 1`) within 0.2 dex of the target
   mass and take the 5 closest per bin;
3. stream the snapshot `PL_25_1024_0056.hdf5` in chunks of 4e6 particles; for each
   chunk compute the periodic-wrapped distance to every selected halo centre
   (box = 37.1 Mpc physical, i.e. 25 h^-1 Mpc);
4. accumulate particle mass and particle count in 20 logarithmic shells of
   `r/R200m` between 0.01 and 1, then `rho = M_shell / V_shell` in Msun/kpc^3;
5. mask shells whose median particle count is below 10 (resolution limit) and
   shade that region in the figure;
6. NFW reference: amplitude-matched with the same M200 and c,
   `rho_s = M200 / (4 pi rs^3 [ln(1+c) - c/(1+c)])`, `rs = R200/c`.

Two centrings are computed and compared: `SO/200_mean/CentreOfMass` (the
"centre of mass within R200m" used by the original description) and
`BoundSubhalo/CentreOfMass` (more stable, closer to the potential minimum).

## Contents

- `profiles_PL.json`, `profiles_kp1.json`, `profiles_kp10.json`: per halo, per
  centre, the shell-averaged density `rho` and the particle `count` per shell.
- Source runs: `PL/PL_25_1024`, `bluetilted/kp_1_ms_1.5_25_1024`,
  `bluetilted/kp_10_ms_1.5_25_1024`; snapshot 0056.
- Mass bins: 1e9, 1e10, 1e11, 1e12 Msun; the 1e8 bin is omitted because
  `N200 ~ 50` particles only.
- DM particle mass: 1.89e6 Msun (confirms the 37.1 Mpc physical box).
- Figure: `halo-density-radial-particles-bt-pl.png` (PL black, BTKP1 blue,
  BTKP10 green; bottom panels show BT/PL).

## Caveats

- 1e12 Msun bins contain few haloes in a 37 Mpc box, so their scatter is large.
- Shells below the masking radius are still stored in the JSON; do not use them.
- The profiles use DM particles only; gas/baryonic effects are not included.
