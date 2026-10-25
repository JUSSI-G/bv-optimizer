"""Export a Cirq circuit to the JSON-style gate list used by the simulator.

Only h, t and cx are emitted: X is decomposed as H T T T T H and Z as T T T T.
"""

import cirq


def export_circuit(circuit):
    place = {}
    for i, qubit in enumerate(sorted(circuit.all_qubits())):
        place[qubit] = i

    result = []

    for operation in circuit.all_operations():
        if operation.gate == cirq.H:
            result.append({"gate": "h", "qubits": [place[operation.qubits[0]]]})
        elif operation.gate == cirq.CNOT:
            result.append({"gate": "cx", "qubits": [place[operation.qubits[0]], place[operation.qubits[1]]]})
        elif operation.gate == cirq.X:
            q = place[operation.qubits[0]]
            result.append({"gate": "h", "qubits": [q]})
            for _ in range(4):
                result.append({"gate": "t", "qubits": [q]})
            result.append({"gate": "h", "qubits": [q]})
        elif operation.gate == cirq.Z:
            q = place[operation.qubits[0]]
            for _ in range(4):
                result.append({"gate": "t", "qubits": [q]})
        elif isinstance(operation, cirq.ControlledOperation):
            qubits = []
            for q in operation.qubits:
                qubits.append(place[q])
            result.append({"gate": "cx", "qubits": qubits})

    return result
