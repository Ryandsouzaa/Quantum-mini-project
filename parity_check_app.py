import streamlit as st
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram
import matplotlib.pyplot as plt
import io  # Required for in-memory image handling

def create_parity_check_circuit(input_state: str) -> QuantumCircuit:
    """
    Creates a 2-qubit parity check circuit.
    """
    qc = QuantumCircuit(3, 1)
    if input_state[0] == '1':
        qc.x(0)
    if input_state[1] == '1':
        qc.x(1)
    qc.barrier()
    qc.cx(0, 2)
    qc.cx(1, 2)
    qc.barrier()
    qc.measure(2, 0)
    return qc

# --- Streamlit UI ---

st.set_page_config(page_title="Quantum Parity Check", layout="wide")
st.title("Quantum Parity Check")
st.markdown(
    """
    Explore how a quantum circuit can determine the parity (even or odd) of a 2-qubit input state.
    An **ancilla qubit** (q2) is a helper qubit used to store the calculation.
    The final state of the ancilla reveals the parity: **`0` for Even**, **`1` for Odd**.
    """
)

# --- Sidebar Controls ---
st.sidebar.header("Input State Controls")
q0_state = st.sidebar.selectbox("Choose state for Qubit 0", ["0", "1"], key="q0")
q1_state = st.sidebar.selectbox("Choose state for Qubit 1", ["0", "1"], key="q1")
input_state_str = f"{q0_state}{q1_state}"

# --- Main Page ---

# Build the circuit
qc = create_parity_check_circuit(input_state_str)

st.subheader("Quantum Circuit")
with st.expander("Show/Hide Circuit Diagram"):
    # --- NEW METHOD: Render to an in-memory image ---

    # 1. Create a Matplotlib figure to draw on
    fig, ax = plt.subplots()
    qc.draw('mpl', ax=ax)

    # 2. Save the figure to an in-memory PNG buffer
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)  # Close the figure to free up memory
    buf.seek(0)

    # 3. Display the image from the buffer using st.image, with explicit width
    st.image(buf, width=400) # <-- CONTROL THE SIZE HERE (in pixels)


# --- Simulation ---
st.subheader("Simulation Results")
backend = AerSimulator()
shots = 1024
job = backend.run(qc, shots=shots)
result = job.result()
counts = result.get_counts(qc)

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
    st.metric(label=f"Input State |{input_state_str}⟩ Parity", value=parity)
    st.write(
        f"The ancilla qubit was measured in the state **|{parity_result_bit}⟩**, "
        f"which indicates the input has **{parity}** parity."
    )