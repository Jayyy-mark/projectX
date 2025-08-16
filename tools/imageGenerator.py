# app.py
import matplotlib.pyplot as plt
import os
import re
from flask import send_file

STATIC_DIR = "bot/static/img"
os.makedirs(STATIC_DIR, exist_ok=True)

def parse_command(text):
    """
    Parses text like 'sale 5000 purchase 10000 expense 20000 income 40000'
    into labels & values.
    """
    matches = re.findall(r"(\w+)\s+(\d+)", text, re.IGNORECASE)
    labels = [m[0].capitalize() for m in matches]
    values = [int(m[1]) for m in matches]
    return labels, values

def generate_chart(text,filename="chart.png"):
    matches = re.findall(r"(\w+)\s+(\d+)", text, re.IGNORECASE)
    labels = [m[0].capitalize() for m in matches]
    values = [int(m[1]) for m in matches]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, values, color=['green', 'red', 'blue', 'orange'])
    plt.xlabel("Categories")
    plt.ylabel("Values")
    plt.title("Generated Bar Chart")
    plt.tight_layout()

    filepath = os.path.join(STATIC_DIR, filename)
    plt.savefig(filepath)
    plt.close()
    return "Successfully created!"

# command = " create an image showing barchart like sale 5000 purchase 10000 expense 40000 income 30000"

# filename = generate_chart(command)