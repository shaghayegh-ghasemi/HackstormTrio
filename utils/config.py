import os

# Define a shared directory for storing results
RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
os.makedirs(RESULTS_DIR, exist_ok=True)  # Ensure directory exists
