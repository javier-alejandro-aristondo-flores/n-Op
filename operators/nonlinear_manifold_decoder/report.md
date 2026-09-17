# nonlinear_manifold_decoder -- strain or lattice parameters to charge density, decoded point by point

`strain_to_charge` on the strain atlas holdout, one seeded run (seed 20260916), 272001 parameters.

## floors, pre-registered on the arm leave-one-level-out population

```
group                                              metric       units  runs  median    interquartile  mean_interval       
bracketing_interpolation_floor                     relative_l2  423    423   0.000911  0.001348       [0.000688, 0.000818]
bracketing_interpolation_floor__biaxial            relative_l2  38     38    0.000066  0.000015       [0.000064, 0.000074]
bracketing_interpolation_floor__isotropic          relative_l2  45     45    0.000020  0.000005       [0.000019, 0.000021]
bracketing_interpolation_floor__one_angle_shear    relative_l2  38     38    0.000005  0.000001       [0.000005, 0.000006]
bracketing_interpolation_floor__three_angle_shear  relative_l2  20     20    0.000649  0.000194       [0.000564, 0.000665]
bracketing_interpolation_floor__triaxial           relative_l2  216    216   0.001374  0.000523       [0.001333, 0.001409]
bracketing_interpolation_floor__two_angle_shear    relative_l2  28     28    0.000194  0.000003       [0.000194, 0.000197]
bracketing_interpolation_floor__uniaxial           relative_l2  38     38    0.000025  0.000005       [0.000024, 0.000028]
gaussian_radial_basis_floor                        relative_l2  423    423   0.000991  0.003138       [0.003048, 0.004115]
gaussian_radial_basis_floor__biaxial               relative_l2  38     38    0.000903  0.000713       [0.000728, 0.000982]
gaussian_radial_basis_floor__isotropic             relative_l2  45     45    0.004046  0.000762       [0.003829, 0.004093]
gaussian_radial_basis_floor__one_angle_shear       relative_l2  38     38    0.016164  0.014060       [0.012455, 0.017162]
gaussian_radial_basis_floor__three_angle_shear     relative_l2  20     20    0.010882  0.007047       [0.007694, 0.012233]
gaussian_radial_basis_floor__triaxial              relative_l2  216    216   0.000712  0.000613       [0.000773, 0.000906]
gaussian_radial_basis_floor__two_angle_shear       relative_l2  28     28    0.011515  0.011363       [0.009600, 0.014738]
gaussian_radial_basis_floor__uniaxial              relative_l2  38     38    0.000532  0.000451       [0.000427, 0.000583]
ridge_to_tensor_floor                              relative_l2  423    423   0.004225  0.006619       [0.006818, 0.008186]
ridge_to_tensor_floor__biaxial                     relative_l2  38     38    0.005077  0.005108       [0.005221, 0.008272]
ridge_to_tensor_floor__isotropic                   relative_l2  45     45    0.009097  0.002726       [0.007981, 0.009086]
ridge_to_tensor_floor__one_angle_shear             relative_l2  38     38    0.020430  0.017725       [0.017808, 0.024029]
ridge_to_tensor_floor__three_angle_shear           relative_l2  20     20    0.011866  0.002519       [0.011071, 0.012817]
ridge_to_tensor_floor__triaxial                    relative_l2  216    216   0.003353  0.001252       [0.003411, 0.003955]
ridge_to_tensor_floor__two_angle_shear             relative_l2  28     28    0.018543  0.014941       [0.016728, 0.023092]
ridge_to_tensor_floor__uniaxial                    relative_l2  38     38    0.003994  0.002098       [0.003662, 0.004373]
nearest_run_copy_floor                             relative_l2  423    423   0.019876  0.010944       [0.022205, 0.024712]
nearest_run_copy_floor__biaxial                    relative_l2  38     38    0.024364  0.022644       [0.023751, 0.034560]
nearest_run_copy_floor__isotropic                  relative_l2  45     45    0.025752  0.022191       [0.025184, 0.034881]
nearest_run_copy_floor__one_angle_shear            relative_l2  38     38    0.014143  0.012087       [0.011017, 0.015981]
nearest_run_copy_floor__three_angle_shear          relative_l2  20     20    0.016914  0.000080       [0.016890, 0.016955]
nearest_run_copy_floor__triaxial                   relative_l2  216    216   0.019984  0.003366       [0.022379, 0.024928]
nearest_run_copy_floor__two_angle_shear            relative_l2  28     28    0.010395  0.000602       [0.010466, 0.011595]
nearest_run_copy_floor__uniaxial                   relative_l2  38     38    0.024575  0.029520       [0.025519, 0.038317]
```

## the member against its floors and bars

```
group  floor                     floor_median  member_median  improvement  required  verdict
all    bracketing_interpolation  0.000911      0.002452       -169.2%      33.3%     kill   
all    gaussian_radial_basis     0.000991      0.002452       -147.4%      33.3%     kill   
all    own_40_cubed_error        0.002424      0.003188       -31.6%       -30.0%    kill   
```

**dead end**: the interpolation bar killed the entry (the canon's terminal clause for this member). Grid transfer is reported regardless of the interpolation verdict, per the canon's own instruction for this entry.

## the member's own headline, committed strain_atlas_holdout split

```
group                            metric       units  runs  median    interquartile  mean_interval       
member_headline_committed_split  relative_l2  22     176   0.002424  0.001684       [0.002564, 0.003277]
member_arm_population            relative_l2  423    423   0.002452  0.001879       [0.005053, 0.006796]
member_every_shape               relative_l2  30     248   0.002795  0.001553       [0.002721, 0.003335]
```

Training manifest: ['probe_learning_rate', 'probe_steps', 'stage_0', 'stage_1', 'stage_2', 'peak_accelerator_bytes'].

Figures: 19 files written under `figures/pooled/`, arrays cached at `/Pool/VASP_DATA/_derived/_figures/nonlinear_manifold_decoder`.

