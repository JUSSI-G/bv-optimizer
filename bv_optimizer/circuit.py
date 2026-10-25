"""Bernstein-Vazirani circuit construction."""

import cirq


def bernstein_vazirani(n, a):
    inputs = []

    for i in range (n):
        source = cirq.NamedQubit(f'qubit[{i}]')
        inputs.append(source)
    target = cirq.NamedQubit('target')

    circuit = cirq.Circuit()

    x = cirq.X
    hadamard = cirq.H
    cnot = cirq.CNOT


    circuit.append(hadamard.on_each(inputs))
    circuit.append([x(target), hadamard(target)])

    bits = []
    for i in a:
        bit = int(i)
        bits.append(bit)

    for i, j in enumerate(bits):
        if j == 1:
            circuit.append(cnot(inputs[i], target))

    circuit.append(hadamard.on_each(inputs))

    circuit.append(cirq.measure(inputs, key='result'))

    return circuit
