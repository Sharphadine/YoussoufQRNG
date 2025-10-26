#!/usr/bin/env python3
"""
YOUSSOUF Quantum Random Number Generator (GUI Edition)
------------------------------------------------------
A modern, elegant quantum random number generator with GUI.

✨ Features:
- Beautiful dark interface with dynamic feedback
- Generate true random numbers via Quantum (Qiskit) or Pseudo backend
- View Shannon entropy & monobit test stats
- Export binary or hexadecimal output
"""

import customtkinter as ctk
import threading
import math
import random
from tkinter import messagebox

# -----------------------
# Try importing Qiskit
# -----------------------
def try_import_qiskit():
    try:
        from qiskit import QuantumCircuit, transpile
        from qiskit.providers.aer import AerSimulator
        return {"ok": True, "QuantumCircuit": QuantumCircuit, "transpile": transpile, "AerSimulator": AerSimulator}
    except Exception as e:
        return {"ok": False, "error": e}

# -----------------------
# Quantum random bits
# -----------------------
def quantum_generate_bits(n_bits):
    q = try_import_qiskit()
    if not q["ok"]:
        raise ImportError("Qiskit not installed. Please run: pip install qiskit")

    QuantumCircuit = q["QuantumCircuit"]
    transpile = q["transpile"]
    AerSimulator = q["AerSimulator"]

    sim = AerSimulator()
    qc = QuantumCircuit(n_bits, n_bits)
    qc.h(range(n_bits))
    qc.measure(range(n_bits), range(n_bits))

    tqc = transpile(qc, sim)
    job = sim.run(tqc, shots=1)
    result = job.result()
    counts = result.get_counts()
    bitstring = list(counts.keys())[0]
    return bitstring

# -----------------------
# Pseudo-random fallback
# -----------------------
def pseudo_generate_bits(n_bits):
    sysrand = random.SystemRandom()
    r = sysrand.getrandbits(n_bits)
    return format(r, f"0{n_bits}b")

# -----------------------
# Helper: entropy & tests
# -----------------------
def shannon_entropy(bits):
    n = len(bits)
    if n == 0:
        return 0.0
    p1 = bits.count("1") / n
    p0 = 1 - p1
    ent = 0
    for p in (p0, p1):
        if p > 0:
            ent -= p * math.log2(p)
    return ent

def monobit_test(bits):
    n = len(bits)
    c1 = bits.count("1")
    c0 = n - c1
    p1 = c1 / n if n else 0
    sd = math.sqrt(0.25 / n) if n else 0
    z = (p1 - 0.5) / sd if sd else 0
    return n, c0, c1, p1, z

# -----------------------
# GUI Setup
# -----------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("YOUSSOUF Quantum Random Number Generator")
app.geometry("760x650")

# Header / Welcome
header = ctk.CTkFrame(app, fg_color="#0D1B2A", height=100, corner_radius=15)
header.pack(fill="x", pady=15, padx=10)

welcome_label = ctk.CTkLabel(
    header,
    text="⚛ Welcome to YOUSSOUF Random Number Generation ⚛\n(Quantum Edition)",
    font=("Segoe UI", 24, "bold"),
    text_color="#00E5FF"
)
welcome_label.pack(pady=15)

# Main Frame
frame = ctk.CTkFrame(app, width=500, height=400, corner_radius=12)
frame.pack(pady=10)

# Inputs
bits_label = ctk.CTkLabel(frame, text="Number of Bits:", font=("Segoe UI", 14))
bits_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
bits_entry = ctk.CTkEntry(frame, placeholder_text="e.g. 8")
bits_entry.insert(0, "8")
bits_entry.grid(row=0, column=1, padx=10, pady=10)

format_label = ctk.CTkLabel(frame, text="Output Format:", font=("Segoe UI", 14))
format_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
format_choice = ctk.CTkComboBox(frame, values=["bin", "hex"], width=120)
format_choice.set("bin")
format_choice.grid(row=1, column=1, padx=10, pady=10)

backend_label = ctk.CTkLabel(frame, text="Backend:", font=("Segoe UI", 14))
backend_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
backend_choice = ctk.CTkComboBox(frame, values=["Quantum (Qiskit)", "Pseudo Random"], width=180)
backend_choice.set("Quantum (Qiskit)")
backend_choice.grid(row=2, column=1, padx=10, pady=10)

# Output box
output_box = ctk.CTkTextbox(app, height=160, width=640, font=("Consolas", 14))
output_box.pack(pady=15)

# Stats Label
stats_label = ctk.CTkLabel(app, text="", font=("Segoe UI", 13))
stats_label.pack(pady=5)

# -----------------------
# Random number generation
# -----------------------
def generate_random():
    try:
        bits = int(bits_entry.get())
        fmt = format_choice.get()
        backend = backend_choice.get()

        output_box.delete("1.0", "end")
        stats_label.configure(text="")

        def task():
            try:
                if backend.startswith("Quantum"):
                    bitstring = quantum_generate_bits(bits)
                    backend_used = "Qiskit Quantum Simulator"
                else:
                    bitstring = pseudo_generate_bits(bits)
                    backend_used = "Pseudo Random Generator"

                # Format output
                if fmt == "hex":
                    result_str = hex(int(bitstring, 2))[2:]
                else:
                    result_str = bitstring

                entropy = shannon_entropy(bitstring)
                n, c0, c1, p1, z = monobit_test(bitstring)

                output_box.insert("end", result_str)
                stats_label.configure(
                    text=(
                        f"Backend: {backend_used} | Entropy: {entropy:.4f} bits/symbol | "
                        f"Ones: {c1}, Zeros: {c0}, p1={p1:.3f}, z={z:.3f}"
                    )
                )

            except Exception as e:
                messagebox.showerror("Error", str(e))

        threading.Thread(target=task).start()

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number of bits.")

# Button
generate_button = ctk.CTkButton(
    app,
    text="🎲 Generate Quantum Random Number",
    font=("Segoe UI", 16, "bold"),
    width=280,
    height=45,
    command=generate_random,
    fg_color="#007BFF",
    hover_color="#0099FF"
)
generate_button.pack(pady=20)

# Footer
footer = ctk.CTkLabel(
    app,
    text="Developed by YOUSSOUF | Powered by Qiskit & CustomTkinter",
    font=("Segoe UI", 10),
    text_color="#80DFFF"
)
footer.pack(pady=10)

app.mainloop()
