import pandas as pd
import json

# Input and output file names
csv_file = "word-word_translation - cleaned for json.csv"
json_file = "midterm_dictionary.json"

# Read CSV file (auto-detect delimiter)
df = pd.read_csv(csv_file, sep=None, engine="python")

# Replace missing or NaN values with "-"
df = df.fillna("-")

# Convert to list of dictionaries (each row becomes a JSON object)
data = df.to_dict(orient="records")

# Write JSON file with proper formatting
with open(json_file, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Successfully converted {csv_file} to {json_file}")