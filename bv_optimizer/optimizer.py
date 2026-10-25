"""Template-based optimizer for Bernstein-Vazirani circuits."""

from bv_optimizer.templates import template1, template2, template3, template4


def optimize_bv(n, circuit):
    circuit = template1(circuit)
    circuit = template2(circuit)
    circuit = template3(circuit)
    circuit = template4(circuit)
    return circuit
