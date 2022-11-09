'''

'''
import numpy as np
# import scipy.special as sp
# from scipy.stats import rv_discrete as dis

import utility_custom
import utility_monte_carlo as mc
import utility_rilm as rilm
import input_parameters as ip


def random_instanton_liquid_model(n_lattice,  # size of the grid
                                  n_mc_sweeps,  # monte carlo sweeps
                                  n_points,  #
                                  n_meas):

    # Control output filepath
    output_path = './output_data/output_rilm'
    utility_custom.output_control(output_path)

    # Eucliadian time
    tau_array = np.linspace(0.0, n_lattice * ip.dtau, n_lattice, False)

    # Correlation functions
    x_cor_sums = np.zeros((3, n_points))
    x2_cor_sums = np.zeros((3, n_points))


    loop_2 = 8 * pow(ip.x_potential_minimum, 5 / 2) \
        * pow(2 / np.pi, 1/2) * np.exp(-ip.action_0 - 71 / (72 * ip.action_0))
        
    n_ia = int(np.rint(loop_2 * n_lattice * ip.dtau))

    hist_writer = open(output_path +'/zcr_hist.txt','w')

    print(n_ia)

    for i_mc in range(n_mc_sweeps):
        print(f'#{i_mc} sweep in {n_mc_sweeps - 1}')
        tau_centers_ia = np.copy(rilm.rilm_monte_carlo_step(n_ia,
                                                      n_points,
                                                      n_meas,
                                                      tau_array,
                                                      x_cor_sums,
                                                      x2_cor_sums))

        for i in range(0, tau_centers_ia.size, 2):
            if i == 0:
                zero_m = tau_centers_ia[-1] - n_lattice * ip.dtau
            else:
                zero_m = tau_centers_ia[i-1]
                
            z_ia = min((tau_centers_ia[i+1]-tau_centers_ia[i]),
                       (tau_centers_ia[i] - zero_m))
            
            hist_writer.write(str(z_ia) + '\n')

    hist_writer.close()

    utility_custom.\
        output_correlation_functions_and_log(n_points,
                                             x_cor_sums,
                                             x2_cor_sums,
                                             n_mc_sweeps * n_meas,
                                             output_path)