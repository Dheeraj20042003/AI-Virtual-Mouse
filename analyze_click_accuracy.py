# analyze_click_accuracy.py
# The number of clicks you intended to perform
intended_clicks = 5 # Update this to match the number of intended clicks

log_file = 'click_accuracy.log'

with open(log_file, 'r') as file:
    logs = file.readlines()

click_detected_count = sum(1 for log in logs if "Click detected" in log)

accuracy = (click_detected_count / intended_clicks) * 100

if accuracy > 100:
    accuracy = 100

print(f"Right-hand click detection accuracy: {accuracy:.2f}%")
