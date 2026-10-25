"""A minimal state-vector simulator for programs produced by export_circuit."""

import numpy as np

# These are used to gate operations for the qubits by matrix multiplication:
# quantum gates are the building blocks for the circuit

# The necessary building blocks for the CNOT gate
# CNOT = P0 ⊗ I + P1 ⊗ X
X = np.array([[0, 1], [1, 0]], dtype=complex)
P0 =  np.array([[1, 0], [0, 0]], dtype=complex)
P1 =  np.array([[0, 0], [0, 1]], dtype=complex)
I = np.array([[1, 0], [0, 1]], dtype=complex)

# Single qubit
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)

T = np.array([[1, 0],[0, np.exp(1j * np.pi / 4)]], dtype=complex)

# This is the actual simulation framework
def get_ground_state(num_qubits):
    # return vector of size 2**num_qubits with all zeroes except first element which is 1
    length = 2 ** num_qubits
    vector = np.zeros(length, dtype=complex)
    vector[0] = 1
    return vector

def get_operator(total_qubits, gate_unitary, target_qubits):
    # return unitary operator of size 2**n x 2**n for given gate and target qubits

    # Example: gate on qubit 0: 𝑂 = 𝑈 ⊗ 𝐼 ⊗ 𝐼, gate on qubit 1: 𝑂 = 𝐼 ⊗ 𝑈 ⊗ 𝐼, gate on qubit 2:  𝑂 = 𝐼 ⊗ 𝐼 ⊗ 𝑈

    # For single qubits
    if len(target_qubits) == 1:
        operator = 1
        for i in range(total_qubits):
            if i == target_qubits[0]:
                operator = np.kron(operator, gate_unitary)
            else:
                operator = np.kron(operator, I)
        return operator

    # For controlled gates (CNOT): control c, target t
    if len(target_qubits) >= 2:
        c = target_qubits[0]
        targets = target_qubits[1:]
        term0 = 1
        term1 = 1
        for i in range(total_qubits):
            if i == c:
                term0 = np.kron(term0, P0)
                term1= np.kron(term1, P1)
            elif i in targets:
                term0 = np.kron(term0, I)
                term1 = np.kron(term1, gate_unitary)
            else:
                term0 = np.kron(term0, I)
                term1 = np.kron(term1, I)
        return term0 + term1

def run_program(program):
    # read program, and for each gate:
    #   - calculate matrix operator
    #   - multiply state with operator
    # return final state

    # cx: P0 ⊗ I + P1 ⊗ (gate) is already filled by get_operator, we just need X for the gate
    gates = {"h": H, "cx": X , "t": T}

    num_qubits = 0
    for i in program:
        num_qubits = max(num_qubits, max(i["qubits"]))

    num_qubits = num_qubits + 1
    state = get_ground_state(num_qubits)

    for i in program:
        gate = i["gate"]
        qubits = i["qubits"]
        matrix   = gates[gate]
        operator = get_operator(num_qubits, matrix, qubits)
        state = operator @ state
    return state

def get_counts(state_vector, num_shots):
    # probability = |amplitude|^2
    # simulate num_shots with weighted random picks

    probs = []
    for i in state_vector:
        probs.append(np.abs(i) ** 2)

    pick = np.random.choice(len(state_vector), size=num_shots, p=probs)

    # n qubits give a vector of length 2^n so we have to count the length in qubits
    num_qubits = int(np.log2(len(state_vector)))

    num_picks = {}
    for i in pick:
        bits = np.binary_repr(i, width=num_qubits)
        num_picks[bits] = num_picks.get(bits, 0) + 1
    return num_picks
