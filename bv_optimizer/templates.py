"""Circuit rewrite templates used by the optimizer.

template1: H Z H                   -> X
template2: H H                     -> (nothing)
template3: H(c) CNOT(c, t) H(c)    -> CNOT(t, c), with the target's Hadamards moved to the end
template4: CNOTs sharing a control -> one controlled multi-target X
"""

import cirq


def gate_pos(operations, qubit):
    pos = []
    for i, operation in enumerate(operations):
        if operation is not None and qubit in operation.qubits:
            pos.append(i)
    return pos


def template1(circuit):
    operations = list(circuit.all_operations())

    for qubit in circuit.all_qubits():
        pos = gate_pos(operations, qubit)

        for k in range(len(pos) - 2):
            a = operations[pos[k]]
            b = operations[pos[k+1]]
            c = operations[pos[k+2]]
            if a is None or b is None or c is None:
                continue

            if (a.gate, b.gate, c.gate) == (cirq.H, cirq.Z, cirq.H):
                operations[pos[k]] = cirq.X(qubit)
                operations[pos[k+1]] = None
                operations[pos[k+2]] = None

    new_circuit = cirq.Circuit()

    for o in operations:
        if o is not None:
            new_circuit.append(o)

    return new_circuit

def template2(circuit):
    operations = list(circuit.all_operations())

    for qubit in circuit.all_qubits():
        pos = gate_pos(operations, qubit)

        for k in range(len(pos) - 1):
            a = operations[pos[k]]
            b = operations[pos[k+1]]
            if a is None or b is None:
                continue

            if (a.gate, b.gate) == (cirq.H, cirq.H):
                operations[pos[k]] = None
                operations[pos[k+1]] = None

    new_circuit = cirq.Circuit()

    for o in operations:
        if o is not None:
            new_circuit.append(o)

    return new_circuit

def template3(circuit):
    operations = list(circuit.all_operations())
    target = None

    for qubit in circuit.all_qubits():
        pos = gate_pos(operations, qubit)

        for k in range(len(pos) - 2):
            a = operations[pos[k]]
            b = operations[pos[k+1]]
            c = operations[pos[k+2]]
            if a is None or b is None or c is None:
                continue

            if (a.gate, b.gate, c.gate) == (cirq.H, cirq.CNOT, cirq.H) and b.qubits[0] == qubit:
                target = b.qubits[1]
                operations[pos[k]] = None
                operations[pos[k+1]] = cirq.CNOT(target, qubit)
                operations[pos[k+2]] = None

    if target is not None:
        for i,o in enumerate(operations):
            if o is not None and o.gate == cirq.H and o.qubits[0] == target:
                operations[i] = None
        operations.append(cirq.H(target))

    new_circuit = cirq.Circuit()

    for o in operations:
        if o is not None:
            new_circuit.append(o)

    return new_circuit

def template4(circuit):
    operations = list(circuit.all_operations())

    for i, o in enumerate(operations):
        if o is None or o.gate != cirq.CNOT:
            continue

        c = o.qubits[0]
        run = [i]
        for j in range (i + 1, len(operations)):
            other = operations[j]
            if other is None:
                continue
            if other.gate == cirq.CNOT and other.qubits[0] == c:
                run.append(j)
            elif c in other.qubits:
                break

        if len(run) >= 2:
            targets = []
            for k in run:
                targets.append(operations[k].qubits[1])
            gate = cirq.ParallelGate(cirq.X, len(targets))
            operation = gate.on(*targets)
            merged = operation.controlled_by(c)
            operations[run[0]] = merged
            for k in run[1:]:
                operations[k] = None

    new_circuit = cirq.Circuit()
    for o in operations:
        if o is not None:
            new_circuit.append(o)
    return new_circuit
