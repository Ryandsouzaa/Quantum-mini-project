import streamlit as st
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import io

def create_3_qubit_parity_check_circuit(input_state: str) -> QuantumCircuit:
    """
    Creates a 3-qubit parity check circuit.

    Args:
        input_state: A 3-character string representing the input state (e.g., "101").

    Returns:
        The quantum circuit for the parity check.
    """
    # 3 input qubits (0, 1, 2) + 1 ancilla qubit (3) = 4 qubits total
    # 1 classical bit to store the measurement result
    qc = QuantumCircuit(4, 1)

    # Prepare the 3-qubit input state
    if input_state[0] == '1':
        qc.x(0)
    if input_state[1] == '1':
        qc.x(1)
    if input_state[2] == '1':
        qc.x(2)

    qc.barrier()

    # Parity check logic: CNOT from each input qubit to the ancilla (q3)
    qc.cx(0, 3)
    qc.cx(1, 3)
    qc.cx(2, 3)

    qc.barrier()

    # Measure the ancilla qubit (q3) to get the final parity result
    qc.measure(3, 0)

    return qc

# --- Streamlit UI ---

st.set_page_config(page_title="3-Qubit Quantum Parity Check", layout="wide")
st.title("3-Qubit Quantum Parity Check")

st.markdown(
    """
    Explore how a quantum circuit can determine the parity (even or odd) of a **3-qubit** input state.
    An **ancilla qubit** (q3) is a helper qubit used to store the calculation.
    The final state of the ancilla reveals the parity: **`0` for Even**, **`1` for Odd**.
    """
)

# --- Sidebar Controls ---
st.sidebar.header("Input State Controls")
q0_state = st.sidebar.selectbox("Choose state for Qubit 0", ["0", "1"], key="q0")
q1_state = st.sidebar.selectbox("Choose state for Qubit 1", ["0", "1"], key="q1")
q2_state = st.sidebar.selectbox("Choose state for Qubit 2", ["0", "1"], key="q2") # New control for the 3rd qubit

# Create the 3-character input string
input_state_str = f"{q0_state}{q1_state}{q2_state}"

# --- Main Page ---

# Build the circuit by calling the updated function
qc = create_3_qubit_parity_check_circuit(input_state_str)

st.subheader("Quantum Circuit")
with st.expander("Show/Hide Circuit Diagram"):
    # Render to an in-memory image for reliable size control
    fig, ax = plt.subplots()
    qc.draw('mpl', ax=ax)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    st.image(buf, width=450) # Adjusted width slightly for the larger circuit

# --- Simulation ---
st.subheader("Simulation Results")
backend = AerSimulator()
shots = 1024
job = backend.run(qc, shots=shots)
result = job.result()
counts = result.get_counts(qc)

# Determine parity from the single bit result
parity_result_bit = list(counts.keys())[0]
parity = "Even" if parity_result_bit == "0" else "Odd"

# --- Display Results ---
col1, col2 = st.columns(2)
with col1:
    st.markdown("### Measurement Outcome")
    fig, ax = plt.subplots(figsize=(4, 3))
    plot_histogram(counts, ax=ax)
    ax.tick_params(axis='x', rotation=0)
    ax.set_title("Ancilla Qubit Measurement")
    ax.set_ylim(top=shots * 1.15)
    st.pyplot(fig)

with col2:
    st.markdown("### Parity Determination")
    # The f-string will now automatically display the 3-qubit state (e.g., |101⟩)
    st.metric(label=f"Input State |{input_state_str}⟩ Parity", value=parity)
    st.write(
        f"The ancilla qubit was measured in the state **|{parity_result_bit}⟩**, "
        f"which indicates the input has **{parity}** parity."
    )