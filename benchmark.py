"""Benchmark the original vs. optimized Bernstein-Vazirani circuit on the state-vector simulator.

Runs n = 3..11 with secret '1' * n and saves the plot to benchmark.png.
"""

import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from bv_optimizer import bernstein_vazirani, export_circuit, optimize_bv, run_program


def evaluate_circuit(circuit):
    program = export_circuit(circuit)
    timer = time.perf_counter()
    run_program(program)
    return time.perf_counter() - timer


def centered_average(nums):
    if len(nums) < 3:
        return nums[0]

    return (sum(nums) - max(nums) - min(nums)) / (len(nums) - 2)


def main():
    x = range(3, 12)
    y1 = [0] * len(x)
    y2 = [0] * len(x)

    for i, nr_q in enumerate(x):
        secret = '1' * nr_q
        circuit_orig = bernstein_vazirani(nr_q, secret)
        circuit_opt = optimize_bv(nr_q, circuit_orig)

        tmp1 = [evaluate_circuit(circuit_orig) for i in range(10)]
        tmp2 = [evaluate_circuit(circuit_opt) for i in range(10)]

        y1[i] = centered_average(tmp1)
        y2[i] = centered_average(tmp2)
        print(f"n={nr_q:2d}  original={y1[i]:.4f}s  optimized={y2[i]:.4f}s  speedup={y1[i] / y2[i]:.1f}x")

    plt.figure(num = 3, figsize=(8, 5))
    plt.plot(x, y2,
             color='green',
             linewidth=2.0,
             linestyle='--',
             label='optimized')
    plt.plot(x, y1,
             color='red',
             linewidth=1.0,
             linestyle='--',
             label='original')
    plt.xlabel("n (secret = '1' * n)")
    plt.ylabel("simulation time (s, centered average of 10 runs)")
    plt.title("Bernstein-Vazirani: original vs. optimized circuit")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig("benchmark.png", dpi=150, bbox_inches="tight")
    print("Saved benchmark.png")


if __name__ == "__main__":
    main()
