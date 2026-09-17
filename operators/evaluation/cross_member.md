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
