# Cross-member table

### charge_and_potential_to_localization

member                           configuration                group                        metric               units  median    verdicts
multiple_input_operator_network  rank32_latent128_trunk3x256  nearest_run_copy_floor       mean_absolute_error  29     0.006164  -       
multiple_input_operator_network  rank32_latent128_trunk3x256  per_shell_filter_floor       mean_absolute_error  29     0.083022  -       
multiple_input_operator_network  rank32_latent128_trunk3x256  semilocal_ridge_floor        mean_absolute_error  29     0.097618  -       
multiple_input_operator_network  rank32_latent128_trunk3x256  training_mean_trivial_floor  mean_absolute_error  29     0.015957  -       

### charge_to_localization

member                configuration                    group                  metric               units  median    verdicts
codomain_attention    hidden32_modes19_heads2_layers4  semilocal_ridge_floor  mean_absolute_error  29     0.097618  -       
galerkin_transformer  gate                             semilocal_ridge_floor  mean_absolute_error  29     0.097618  -       

### charge_to_potential

member              configuration                    group                                  metric                    units  median    verdicts
codomain_attention  hidden32_modes19_heads2_layers4  hartree_plus_semilocal_xc_ridge_floor  mean_removed_relative_l2  29     0.479646  -       

### cheap_to_accurate_charge

member               configuration        group                       metric                units  median    verdicts     
residual_correction  projection_backbone  conformal_calibration_0.90  orbit_field_coverage  22     1.000000  -            
residual_correction  projection_backbone  global_affine               relative_l2           22     0.010466  identity:pass
residual_correction  projection_backbone  identity                    relative_l2           22     0.011131  -            
residual_correction  projection_backbone  member                      delta_r_squared       22     0.964537  identity:pass
residual_correction  projection_backbone  member                      relative_l2           22     0.002079  identity:pass
residual_correction  projection_backbone  rank_32_ceiling             relative_l2           22     0.000002  identity:pass
residual_correction  projection_backbone  ridge_cheap_coefficients    relative_l2           22     0.000005  identity:pass
residual_correction  projection_backbone  ridge_strain_components     relative_l2           22     0.000049  identity:pass

### lattice_to_charge

member                configuration  group                     metric       units  median    verdicts
galerkin_transformer  gate           nearest_angle_copy_floor  relative_l2  25     0.085278  -       

### strain_to_charge

member                      configuration  group                            metric       units  median    verdicts
nonlinear_manifold_decoder  canonical      member_every_shape               relative_l2  30     0.002795  -       
nonlinear_manifold_decoder  canonical      member_headline_committed_split  relative_l2  22     0.002424  -       

### structure_to_charge_defects

member    configuration  group                                        metric                          units  median    verdicts
deep_dft  minimal        nearest_structure_copy_context_all_42        normalized_mean_absolute_error  21     0.067496  -       
deep_dft  minimal        reduced_salted_floor_all_42                  normalized_mean_absolute_error  21     0.111713  -       
deep_dft  minimal        superposed_atomic_density_floor_all_42       normalized_mean_absolute_error  21     0.154149  -       
deep_dft  minimal        superposed_atomic_density_floor_held_out_18  normalized_mean_absolute_error  9      0.161438  -       

### Rows outside the card's split

#### perovskite_arms

task               member                configuration  group                                metric       units  median    verdicts
lattice_to_charge  galerkin_transformer  gate           linear_in_angle_interpolation_floor  relative_l2  27     0.026421  -       

#### strain_atlas_arms

task              member                      configuration  group                                              metric       units  median    verdicts
strain_to_charge  nonlinear_manifold_decoder  canonical      bracketing_interpolation_floor                     relative_l2  423    0.000911  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      bracketing_interpolation_floor__biaxial            relative_l2  38     0.000066  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      bracketing_interpolation_floor__isotropic          relative_l2  45     0.000020  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      bracketing_interpolation_floor__one_angle_shear    relative_l2  38     0.000005  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      bracketing_interpolation_floor__three_angle_shear  relative_l2  20     0.000649  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      bracketing_interpolation_floor__triaxial           relative_l2  216    0.001374  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      bracketing_interpolation_floor__two_angle_shear    relative_l2  28     0.000194  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      bracketing_interpolation_floor__uniaxial           relative_l2  38     0.000025  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      gaussian_radial_basis_floor                        relative_l2  423    0.000991  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      gaussian_radial_basis_floor__biaxial               relative_l2  38     0.000903  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      gaussian_radial_basis_floor__isotropic             relative_l2  45     0.004046  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      gaussian_radial_basis_floor__one_angle_shear       relative_l2  38     0.016164  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      gaussian_radial_basis_floor__three_angle_shear     relative_l2  20     0.010882  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      gaussian_radial_basis_floor__triaxial              relative_l2  216    0.000712  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      gaussian_radial_basis_floor__two_angle_shear       relative_l2  28     0.011515  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      gaussian_radial_basis_floor__uniaxial              relative_l2  38     0.000532  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      member_arm_population                              relative_l2  423    0.002452  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      nearest_run_copy_floor                             relative_l2  423    0.019876  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      nearest_run_copy_floor__biaxial                    relative_l2  38     0.024364  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      nearest_run_copy_floor__isotropic                  relative_l2  45     0.025752  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      nearest_run_copy_floor__one_angle_shear            relative_l2  38     0.014143  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      nearest_run_copy_floor__three_angle_shear          relative_l2  20     0.016914  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      nearest_run_copy_floor__triaxial                   relative_l2  216    0.019984  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      nearest_run_copy_floor__two_angle_shear            relative_l2  28     0.010395  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      nearest_run_copy_floor__uniaxial                   relative_l2  38     0.024575  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      ridge_to_tensor_floor                              relative_l2  423    0.004225  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      ridge_to_tensor_floor__biaxial                     relative_l2  38     0.005077  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      ridge_to_tensor_floor__isotropic                   relative_l2  45     0.009097  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      ridge_to_tensor_floor__one_angle_shear             relative_l2  38     0.020430  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      ridge_to_tensor_floor__three_angle_shear           relative_l2  20     0.011866  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      ridge_to_tensor_floor__triaxial                    relative_l2  216    0.003353  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      ridge_to_tensor_floor__two_angle_shear             relative_l2  28     0.018543  -       
strain_to_charge  nonlinear_manifold_decoder  canonical      ridge_to_tensor_floor__uniaxial                    relative_l2  38     0.003994  -       
