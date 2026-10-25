import cirq
import pytest

from bv_optimizer import bernstein_vazirani, export_circuit, get_counts, optimize_bv, run_program

SECRETS = ["101", "111", "00111", "1", "0110", "1111111"]


def measure_with_cirq(circuit, repetitions=200):
    result = cirq.Simulator().run(circuit, repetitions=repetitions)
    return result.histogram(key="result")


def measure_with_own_simulator(circuit, n, shots=200):
    # The last qubit is the target (left in |->), so only the first n bits carry the secret.
    counts = get_counts(run_program(export_circuit(circuit)), shots)
    return {bits[:n] for bits in counts}


@pytest.mark.parametrize("secret", SECRETS)
def test_original_circuit_measures_secret(secret):
    n = len(secret)
    circuit = bernstein_vazirani(n, secret)

    assert measure_with_cirq(circuit) == {int(secret, 2): 200}
    assert measure_with_own_simulator(circuit, n) == {secret}


@pytest.mark.parametrize("secret", SECRETS)
def test_optimized_circuit_still_measures_secret(secret):
    n = len(secret)
    circuit = optimize_bv(n, bernstein_vazirani(n, secret))

    assert measure_with_cirq(circuit) == {int(secret, 2): 200}
    assert measure_with_own_simulator(circuit, n) == {secret}


@pytest.mark.parametrize("secret", SECRETS)
def test_optimization_reduces_circuit(secret):
    n = len(secret)
    original = bernstein_vazirani(n, secret)
    optimized = optimize_bv(n, original)

    assert len(list(optimized.all_operations())) < len(list(original.all_operations()))
    assert len(optimized) <= len(original)


def test_export_111_has_four_t_gates():
    program = export_circuit(optimize_bv(3, bernstein_vazirani(3, "111")))

    assert len([g for g in program if g["gate"] == "t"]) == 4


def test_export_00111_has_single_four_qubit_cx():
    program = export_circuit(optimize_bv(5, bernstein_vazirani(5, "00111")))
    cx_gates = [g for g in program if g["gate"] == "cx"]

    assert len(cx_gates) == 1
    assert len(cx_gates[0]["qubits"]) == 4
