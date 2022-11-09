'''
Heating based on the instanton
random liqud model
'''

import numpy as np

import utility_custom
import utility_rilm as rilm
import input_parameters as ip

                        
def random_instanton_liquid_model_heating(n_lattice,  # size of the grid
                                          n_mc_sweeps,  # monte carlo sweeps
                                          n_points,  #
                                          n_meas,
                                          n_heating):

    # Control output filepath
    output_path = './output_data/output_rilm_heating'
    utility_custom.output_control(output_path)

    # Eucliadian time
    tau_array = np.linspace(0.0, n_lattice * ip.dtau, n_lattice, False)

    # Correlation functions
    x_cor_sums = np.zeros((3, n_points))
    x2_cor_sums = np.zeros((3, n_points))


    # n_ia evaluated from 2-loop semi-classical expansion
    s0 = 4 / 3 * pow(ip.x_potential_minimum, 3)
    loop_2 = 8 * pow(ip.x_potential_minimum, 5 / 2) \
        * pow(2 / np.pi, 1/2) * np.exp(-s0 - 71 / (72 * s0))
    n_ia = int(np.rint(loop_2 * n_lattice * ip.dtau))
    print(n_ia)
    for i_mc in range(n_mc_sweeps):
        print(f'#{i_mc} sweep in {n_mc_sweeps-1}')
        
        rilm.rilm_heated_monte_carlo_step(n_ia,
                                          n_heating,
                                          n_points,
                                          n_meas,
                                          tau_array,
                                          x_cor_sums,
                                          x2_cor_sums)
        
    utility_custom.\
        output_correlation_functions_and_log(n_points,
                                             x_cor_sums,
                                             x2_cor_sums,
                                             n_mc_sweeps * n_meas,
                                             output_path)