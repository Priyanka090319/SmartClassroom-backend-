import csv
import os
from datetime import datetime

# File path (adjust as needed)
csv_file = 'attendance_log.csv'

def initialize_csv():
    """Create the CSV file with header if it doesn't exist."""
    if not os.path.exists(csv_file):
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write header
            writer.writerow(['Name', 'Timestamp', 'Status'])
        print(f"{csv_file} created with headers.")
    else:
        print(f"{csv_file} already exists.")

def log_attendance(name, status):
    """Append a new attendance record to the CSV file."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([name, timestamp, status])
    print(f"Logged attendance for {name} with status {status} at {timestamp}")
    

# Example usage
if __name__ == "__main__":
    initialize_csv()
    log_attendance("John Doe", "Present")
