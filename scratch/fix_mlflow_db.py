import sqlite3
import os

db_path = "mlflow.db"
artifact_path = os.path.abspath("mlartifacts")

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Update the default experiment (ID 0)
    cursor.execute("UPDATE experiments SET artifact_location = ? WHERE experiment_id = '0'", (f"file:///{artifact_path.replace('\\', '/')}",))
    
    if cursor.rowcount > 0:
        print(f"Successfully updated experiment 0 artifact location to: {artifact_path}")
    else:
        print("Experiment 0 not found in database.")
        
    conn.commit()
    conn.close()
except Exception as e:
    print(f"An error occurred: {e}")
