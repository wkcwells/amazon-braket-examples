# general imports
import numpy as np
import math
import matplotlib.pyplot as plt

# AWS imports: Import Amazon Braket SDK modules
import braket
from braket.circuits import Circuit, circuit
from braket.devices import LocalSimulator
from braket.aws import AwsDevice

import sys
sys.path.append('../../')
import AWSBraket.utilities

#### Much of this is copied from the QPE notebook ####

## HELPER FUNCTIONS FOR NUMERICAL TESTS
# Because we will run the same code repeatedly, let's first create a helper function we can use to keep the notebook clean.



# %%

def postprocess_qpe_results(out):
    """
    Function to postprocess dictionary returned by run_qpe

    Args:
        out: dictionary containing results/information associated with QPE run as produced by run_qpe
    """

    # unpack results
    circ = out['circuit']
    measurement_counts = out['measurement_counts']
    bitstring_keys = out['bitstring_keys']
    probs_values = out['probs_values']
    precision_results_dic = out['precision_results_dic']
    phases_decimal = out['phases_decimal']
    eigenvalues = out['eigenvalues']

    # print the circuit
    print('Printing circuit:')
    print(circ)

    # TODO: Why include the last bit - isnt that not part of the algo??
    # plot probabalities
    plt.bar(bitstring_keys, probs_values)
    plt.xlabel('bitstrings')
    plt.ylabel('probability')
    plt.xticks(rotation=90)
    plt.show()

    metadata = out['task_metadata']
    shots = metadata.shots
    print('### SHOT COUNT: %d ###' % shots)
    if shots == 0:
        states = out['states']
        for label, state in enumerate(states):
            print('State #%d: %s' % (label, np.round(state, 5)))
    else:
        # print measurement results
        print('Measurement counts:', measurement_counts)
        # print results
        print('Results in precision register:', precision_results_dic)
        print('QPE phase estimates:', phases_decimal)
        print('QPE eigenvalue estimates:', None if eigenvalues is None else np.round(eigenvalues, 5))


#%%

# local imports
from utils_qpe import qpe, run_qpe

# set up device: local simulator or the managed cloud-based simulator

device = LocalSimulator()


#%%

# Define Pauli matrices
Id = np.eye(2)             # Identity matrix
X = np.array([[0., 1.],
              [1., 0.]])   # Pauli X
Y = np.array([[0., -1.j],
              [1.j, 0.]])  # Pauli Y
Z = np.array([[1., 0.],
              [0., -1.]])  # Pauli Z

# Hadamard
H = 1/np.sqrt(2.) * np.array([[1., 1.],
              [1., -1.]])

PHASE_SHIFT = np.array([[1., 0.],
              [0., np.exp(1.j*2*math.pi/8)]])


# set total number of qubits
precision_qubits = [0, 1]
query_qubits = [2]

# prepare query register
my_qpe_circ = Circuit().h(query_qubits)

# set unitary
unitary = X

# show small QPE example circuit
my_qpe_circ = my_qpe_circ.qpe(precision_qubits, query_qubits, unitary)
print('QPE CIRCUIT:')
print(my_qpe_circ)


#%%

#### As follows, we set up the same circuit, this time implementing the unitary $C-U^{2^k}$, by repeatedly applying the core building block $C-U$.
#### This operation can be done by setting the parameter ```control_unitary=False``` (default is ```True```).

#%%

# set qubits
precision_qubits = [0,1]
query_qubits = [2]

# prepare query register
my_qpe_circ = Circuit().i(query_qubits)
my_qpe_circ.h(query_qubits)

# set unitary
unitary = X

# show small QPE example circuit
my_qpe_circ = my_qpe_circ.qpe(precision_qubits, query_qubits, unitary, control_unitary=False)
print('QPE CIRCUIT:')
print(my_qpe_circ)

# TODO:
#   check out control_unitary= true/false

### NUMERICAL TEST EXAMPLE 1

#%% md

# First, apply the QPE algorithm to the simple single-qubit unitary $U=X$, with eigenstate $|\Psi\rangle = |+\rangle = H|0\rangle$.
# Here, we expect to measure the phase $\varphi=0$ (giving the corresponding eigenvalue $\lambda=1$).
# We show that this result stays the same as we increase the number of qubits $n$ for the top register.

# Set total number of precision qubits: 2
number_precision_qubits = 2

# Define the set of precision qubits
precision_qubits = range(number_precision_qubits)

# Define the query qubits. We'll have them start after the precision qubits
query_qubits = [number_precision_qubits]

# State preparation for eigenstate of U=X
query = Circuit().x(query_qubits).h(query_qubits)   # .z(query_qubits).h(query_qubits)
#query = Circuit().phaseshift(query_qubits, 2 * np.pi / 8).h(query_qubits)

# Just a test
print(braket.circuits.gate.Gate.CPhaseShift(2 * np.pi / 8).to_matrix())

AWSBraket.utilities.print_header('Running qpe circuit')

# Run the test with U=X
out = run_qpe(X, precision_qubits, query_qubits, query, device, shots=0)

AWSBraket.utilities.print_header('Post processing qpe circuit')

# Postprocess results
postprocess_qpe_results(out)
