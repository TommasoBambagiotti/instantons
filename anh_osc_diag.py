import numpy as np
from numpy import math
from numpy import linalg as LA
from numpy.polynomial import hermite
import utility_custom


def psi_simple_model(x_position,
                     x_potential_minimum):
    """Compute the eigenfunctions of the anharmonic oscillator for the ground
    state.

    The eigenfunctions of the ground state is computed as linear superposi-
    tion of the ground state wave functions of harmonic oscillators cente-
    red in the two minima of the potential.

    Parameters
    ----------
    x_position : ndarray
        Space points.

    x_potential_minimum : double
        Potential minimum.

    Returns
    -------
    psi : ndarray
        Ground state of the anharmonic oscillator.

    Warnings
    -------
    The ground state energy can be approximated as a linear superposition on-
    ly if the potential barrier is very high, f->+inf.
    """
    psi_plus_minimum = pow((2.0 * x_potential_minimum / np.pi), 1 / 4) \
                       * np.exp(
        -x_potential_minimum * pow(x_position - x_potential_minimum, 2))

    psi_minus_minimum = pow((2.0 * x_potential_minimum / np.pi), 1 / 4) \
                        * np.exp(
        -x_potential_minimum * pow(x_position + x_potential_minimum, 2))

    psi = (psi_plus_minimum + psi_minus_minimum) * pow(2, -1 / 2)

    return psi


def hermite_pol_coeff(x_position,
                      norm,
                      n_array):
    """Compute Hermite polynomials coefficients.

    Parameters
    ----------
    x_position : ndarray
        Space positions

    norm : double

    n_array : int
        Polynomial degree, it must be greater or eq. than 0.

    Returns
    -------
    hermite_coeff : double

    Notes
    ------
    Hermite polynomials coefficients are computer following the formula:
    1/(l^1/2 pi^1/4 (2^n * n!)^1/2) * exp(-x^2/l^2 /2) * H_n(x/l), where
    l is the length scale of the harmonic oscillator: l=c=(1/mw0)^1/2
    """
    hermite_coeff = np.zeros(n_array)

    for n in range(n_array):
        val = pow(np.pi * norm * norm, -1 / 4) \
              * pow(2.0, -n / 2) * pow(math.factorial(n), -1 / 2) \
              * np.exp(-x_position * x_position / (2.0 * norm * norm))

        hermite_coeff[n] = val

    return hermite_coeff


def corr_functs_analytic(energy_density,
                         tau_array,
                         energy_eigenvalues):
    """Compute (euclidean) correlation function for space coordinates.

    Parameters
    ----------
    energy_density : double
        Energy density matrix element.

    tau_array : ndarray
        Euclidean time array.

    energy_eigenvalues: ndarray
        Hamiltonian energy eigenvalues.

    Returns
    -------
    correlation_funct : ndarray
        Correlation function in euclidean time.

    Notes
    ------
    Energy density matrix element are computed using the hamiltonian comple-
    te set of eigenstates: energy_density = <0|O(tau)|n>, with O(tau) any
    time dependent operator.
    """
    i_tau = 0
    j_energy = 0
    correlation_funct = np.zeros(tau_array.size)
    for tau in tau_array:
        for rho in energy_density:
            correlation_funct[i_tau] += rho * \
                                        np.exp(-(energy_eigenvalues[j_energy] -
                                                 energy_eigenvalues[0]) * tau)
            j_energy += 1
        j_energy = 0
        i_tau += 1
    return correlation_funct


def log_corr_funct_forward_difference(corr_funct, dtau):
    """Compute the log-derivative of correlation functions us-
    ing the method of forward differences.

    Parameters
    ----------
    corr_funct : ndarray
        Correlation function.

    dtau : double
        Increment in variable.

    Returns
    -------
    fd_der_log_corr_funct : ndarray
        Derivative of the logarithm of corr_funct.

    """
    fd_der_log_corr_funct = np.zeros(corr_funct.size - 1)
    for i in range(corr_funct.size - 1):
        fd_der_log_corr_funct[i] = - (
                np.log(corr_funct[i + 1]) - np.log(corr_funct[i])) / dtau

    return fd_der_log_corr_funct


def log_corr_funct_analytic(energy_density,
                            tau_array,
                            energy_eigenvalues,
                            correlation_function):
    """Compute analytically the log-derivative in the euclidean time of cor-
    relation functions for the anharmonic oscillator.

    Parameters
    ----------
    energy_density : double
        Energy density matrix element.

    tau_array : ndarray
        Euclidean time array.

    energy_eigenvalues : ndarray
        Hamiltonian energy eigenvalues.

    correlation_function : ndarray
        Input correlation function.

    Returns
    -------
    an_log_corr_funct : ndarray
        Log-derivative of the input correlation function.

    """
    i_tau = 0
    j_energy = 0
    an_log_corr_funct = np.zeros(tau_array.size)
    for tau in tau_array:
        for rho in energy_density:
            an_log_corr_funct[i_tau] += rho \
                                        * (energy_eigenvalues[j_energy] -
                                           energy_eigenvalues[0]) \
                                        * np.exp(
                -(energy_eigenvalues[j_energy] - energy_eigenvalues[0]) * tau)
            j_energy += 1
        i_tau += 1
        j_energy = 0

    an_log_corr_funct = np.divide(
        an_log_corr_funct, correlation_function)

    return an_log_corr_funct


def free_energy(energy_eigenvalues, output_path):
    """Compute the free energy for a system described in the canonical
    ensemble.

    The free energy F is computed according to the formula for a canonical
    ensemble: F=-log(Z)/T, where Z is the canonical partition function.

    Parameters
    ----------
    energy_eigenvalues : ndarray
        Hamiltonian energy eigenvalues.

    output_path : string
        Directory path where data are saved

    Returns
    ---------
    None
    """
    temperature_array = np.linspace(0.01, 2.0, 99)

    free_energy_array = np.empty(temperature_array.size)
    z_partition_function = 0.0
    i_f_energy = 0
    for temperature in temperature_array:
        for energy in energy_eigenvalues:
            z_partition_function += np.exp(-energy / temperature)

        free_energy_array[i_f_energy] = temperature * np.log(
            z_partition_function)
        z_partition_function = 0.0
        i_f_energy += 1

    with open(output_path + '/temperature.txt', 'w') as temperature_writer:
        np.savetxt(temperature_writer, temperature_array)
    with open(output_path + '/free_energy.txt', 'w') as fenergy_writer:
        np.savetxt(fenergy_writer, free_energy_array)


def anharmonic_oscillator_diag(n_dim,
                               x_potential_minimum=1.4,
                               freq_har_osc=1.4 * 4):
    """Diagonalize the Hamiltonian of the anharmonic oscillator and compute
    euclidean correlation functions.
    
    This program diagonalize numerically the Hamiltonian of an anharmonic
    oscillator in the harmonic oscillator basis. In all modules we use a
    system of unit of measurements where h_bar=1, m=1/2 and lambda=1. After
    diagonalization, euclidean correlation functions and their log-deriva-
    tive are computer, and finally the free energy. All results are saved
    into files.
        
    Parameters
    ----------
    n_dim : int
        Dimension of the eigenvalues basis.
        
    x_potential_minimum : double, default=1.4
        Position of the minimum(a) of the anharmonic potential.
        
    freq_har_osc : double, default=1.4*4
        Harmonic oscillator frequency
    
    Returns
    ---------
    None
    """
    # Output control
    output_path = './output_data/output_diag'
    utility_custom.output_control(output_path)
    # parameters
    n_hamiltonian = n_dim + 4

    # position array
    x_position_array = np.linspace(-2 * x_potential_minimum,
                                   2 * x_potential_minimum)
    # euclidean time coordinate
    tau_max = 2.5
    n_tau = 100
    tau_array, dtau = np.linspace(0, tau_max, n_tau, retstep=True)

    # hamiltonian
    hamiltonian_matrix = np.zeros((n_hamiltonian, n_hamiltonian))

    # ground state wave function
    psi_ground_state_squared = np.zeros(x_position_array.size)

    # energy density
    energy_densities = np.zeros((3, n_dim))

    # correlation function
    corr_funct = np.empty((3, n_tau), float)

    # normalization coefficient for the creation and annihilation
    # operators for the harmonic oscillator
    # units of measurement: h_bar=1, m=1/2, lambda=1
    c_norm_coeff = pow(freq_har_osc, -1 / 2)

    # anharmonic potential coeff.
    a = 1.0
    b = -2.0 * pow(x_potential_minimum, 2) - pow(freq_har_osc, 2) / 4.0
    c = pow(x_potential_minimum, 4)

    # Hamiltonian, symmetric n_hamiltonian x n_hamiltonian matrix
    for i in range(n_dim):
        # n=k-1
        # <i|h|i>
        hamiltonian_matrix[i, i] = \
            a * 3 * pow(c_norm_coeff, 4) * (pow(i + 1, 2) + pow(i, 2)) \
            + b * pow(c_norm_coeff, 2) * (2 * i + 1) \
            + freq_har_osc * (i + 0.5) + c

        # <n|h|n+2>
        hamiltonian_matrix[i, i + 2] = \
            a * pow(c_norm_coeff, 4) * pow((i + 1) * (i + 2), 1 / 2) * (
                    4 * i + 6) \
            + b * pow(c_norm_coeff, 2) * pow((i + 1) * (i + 2), 1 / 2)

        hamiltonian_matrix[i + 2, i] = hamiltonian_matrix[i, i + 2]

        # <n|h|n+4>
        hamiltonian_matrix[i, i + 4] = \
            pow(c_norm_coeff, 4) * pow(
                (i + 1) * (i + 2) * (i + 3) * (i + 4), 1 / 2)

        hamiltonian_matrix[i + 4, i] = hamiltonian_matrix[i, i + 4]

    # Diagononilzation of the Hamiltonian
    energy_eigenvalues, energy_eigenvectors = LA.eigh(hamiltonian_matrix)

    # WE consider also the positive eigenvalues
    # So we neglect the first 4 eigenvectors and consider the groundstate
    # v[:,4]=> because the eigenvectors are the columns.
    i_removal = 0
    indices_removed = np.empty(0, int)
    while i_removal < n_hamiltonian:
        if energy_eigenvalues[i_removal] < 0.0:
            indices_removed = np.append(indices_removed, i_removal)
            i_removal += 1
            continue
        if energy_eigenvalues[i_removal] > 1e-5:
            break

    with open(output_path + '/removed_energy_values.txt', 'w') as e_writer:
        e_writer.write('Removed energy eigenvalues:\n')
        np.savetxt(e_writer, energy_eigenvalues[:i_removal])
        for i in range(i_removal):
            e_writer.write(f'\nEnergy eigenvector {i} components:\n')
            np.savetxt(e_writer, energy_eigenvectors[0:n_hamiltonian, i])

    energy_eigenvalues = np.delete(energy_eigenvalues, indices_removed)
    energy_eigenvectors = np.delete(energy_eigenvectors, indices_removed, 1)

    # save energy eigenvalues
    with open(output_path + '/eigenvalues.txt', 'w') as e_writer:
        np.savetxt(e_writer, energy_eigenvalues)

    # Evaluate the energy dist. rho, rho2, rho2 and matrix elements
    # < 0|x^i|n > , i= 1,2,3.
    # We use the convention for the ladder operators:
    # a+ = (mw/2h)^1/2 (x^ +i/mw p^) and a = (mw/2h)^1/2 (x^ - i/mw p^)
    for n in range(n_dim):
        # C_n = | <0|x|n> |^2
        # D_n = | <0|x^2|n> |^2
        # E_n = | <0|x^3|n> |^2

        c_n = 0.0
        d_n = 0.0
        e_n = 0.0

        for k in range(n_dim):
            k_minus_3 = max(k - 3, 0)
            k_minus_2 = max(k - 2, 0)
            k_minus_1 = max(k - 1, 0)
            k_plus_1 = min(k + 1, n_dim - 1)
            k_plus_2 = min(k + 2, n_dim - 1)
            k_plus_3 = min(k + 3, n_dim - 1)

            c_n += (
                           pow(k + 1, 1 / 2) * energy_eigenvectors[k_plus_1, 0]
                           + pow(k, 1 / 2) * energy_eigenvectors[k_minus_1, 0]
                   ) * energy_eigenvectors[k, n]

            d_n += (
                           pow(k * (k - 1), 1 / 2) * energy_eigenvectors[
                       k_minus_2, 0]
                           + (2 * k + 1) * energy_eigenvectors[k, 0]
                           + pow((k + 1) * (k + 2), 1 / 2) *
                           energy_eigenvectors[k_plus_2, 0]
                   ) * energy_eigenvectors[k, n]

            e_n += (
                           pow(k * (k - 1) * (k - 2), 1 / 2) *
                           energy_eigenvectors[k_minus_3, 0]
                           + 3 * k * pow(k, 1 / 2) * energy_eigenvectors[
                               k_minus_1, 0]
                           + 3 * (k + 1) * pow(k + 1, 1 / 2) *
                           energy_eigenvectors[k_plus_1, 0]
                           + pow((k + 1) * (k + 2) * (k + 3), 1 / 2) *
                           energy_eigenvectors[k_plus_3, 0]
                   ) * energy_eigenvectors[k, n]

        energy_densities[0, n] = pow(c_norm_coeff, 2) * pow(c_n, 2)
        energy_densities[1, n] = pow(c_norm_coeff, 4) * pow(d_n, 2)
        energy_densities[2, n] = pow(c_norm_coeff, 6) * pow(e_n, 2)

    # Groundstate wave function and its properties

    for i_pos in range(x_position_array.size):
        groundstate_projections = \
            np.multiply(energy_eigenvectors[:, 0],
                        hermite_pol_coeff(x_position_array[i_pos],
                                          c_norm_coeff * pow(2.0, 1 / 2),
                                          n_hamiltonian)
                        )
        psi_ground_state_squared[i_pos] = \
            pow(hermite.hermval(
                x_position_array[i_pos] / (c_norm_coeff * np.sqrt(2.0)),
                groundstate_projections), 2)

    with open(output_path + '/x_position_array.txt', 'w') as x_writer:
        np.savetxt(x_writer, x_position_array)
    with open(output_path + '/psi_simple_model.txt', 'w') as psi_simple_writer:
        for x_position in np.nditer(x_position_array):
            psi_simple_writer.write(
                str(
                    pow(psi_simple_model(x_position, x_potential_minimum), 2)
                )
            )
            psi_simple_writer.write('\n')
    with open(output_path + '/psi_ground_state.txt', 'w') as psi_ground_writer:
        np.savetxt(psi_ground_writer, psi_ground_state_squared)

    # Correlation functions
    corr_funct[0] = corr_functs_analytic(energy_densities[0],
                                         tau_array,
                                         energy_eigenvalues)
    corr_funct[1] = corr_functs_analytic(energy_densities[1],
                                         tau_array,
                                         energy_eigenvalues)
    corr_funct[2] = corr_functs_analytic(energy_densities[2],
                                         tau_array,
                                         energy_eigenvalues)

    with open(output_path + '/tau_array.txt', 'w') as tau_writer:
        np.savetxt(tau_writer, tau_array)
    with open(output_path + '/corr_function.txt', 'w') as corr_writer:
        np.savetxt(corr_writer, corr_funct[0])
    with open(output_path + '/corr_function2.txt', 'w') as corr_writer:
        np.savetxt(corr_writer, corr_funct[1])
    with open(output_path + '/corr_function3.txt', 'w') as corr_writer:
        np.savetxt(corr_writer, corr_funct[2])

    # Logarithmic derivative of the correlators

#     # Python methods
#     py_derivative_log_corr_funct = np.gradient(-corr_funct[0], dtau)
#     py_derivative_log_corr_funct2 = np.gradient(-corr_funct[1],
#                                                 dtau)
#     py_derivative_log_corr_funct3 = np.gradient(-corr_funct[2],
#                                                 dtau)

#     with open(output_path + '/py_der_log_corr_funct.txt', 'w') as log_writer:
#         np.savetxt(log_writer, py_derivative_log_corr_funct)
#         np.savetxt(log_writer, py_derivative_log_corr_funct2)
#         np.savetxt(log_writer, py_derivative_log_corr_funct3)

#     # Forward difference

#     fd_derivative_log_corr_funct = log_corr_funct_forward_difference(
#         corr_funct[0], dtau)
#     fd_derivative_log_corr_funct2 = log_corr_funct_forward_difference(
#         corr_funct[1], dtau)
#     fd_derivative_log_corr_funct3 = log_corr_funct_forward_difference(
#         corr_funct[2], dtau)

#     with open(output_path + '/fd_der_log_corr_funct.txt', 'w') as log_writer:
#         np.savetxt(log_writer, fd_derivative_log_corr_funct)
#         np.savetxt(log_writer, fd_derivative_log_corr_funct2)
#         np.savetxt(log_writer, fd_derivative_log_corr_funct3)

    # Analytic formula

    an_derivative_log_corr_funct = log_corr_funct_analytic(energy_densities[0],
                                                           tau_array,
                                                           energy_eigenvalues,
                                                           corr_funct[
                                                               0])
    an_derivative_log_corr_funct2 = log_corr_funct_analytic(
        energy_densities[1],
        tau_array,
        energy_eigenvalues,
        corr_funct[1] - energy_densities[1, 0])

    an_derivative_log_corr_funct3 = log_corr_funct_analytic(
        energy_densities[2],
        tau_array,
        energy_eigenvalues,
        corr_funct[2])

    with open(output_path + '/av_der_log_corr_funct.txt', 'w') as log_writer:
        np.savetxt(log_writer, an_derivative_log_corr_funct)
    with open(output_path + '/av_der_log_corr_funct2.txt', 'w') as log_writer:
        np.savetxt(log_writer, an_derivative_log_corr_funct2)
    with open(output_path + '/av_der_log_corr_funct3.txt', 'w') as log_writer:
        np.savetxt(log_writer, an_derivative_log_corr_funct3)

    # Helmoltz Free Energy
    free_energy(energy_eigenvalues, output_path)

    # Return first two energy eigenvalues

