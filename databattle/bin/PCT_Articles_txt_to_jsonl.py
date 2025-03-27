"""
--------------------------------------------------------------------------------
Author: Camille Solacroup
Date: 2025-03-25
Description:
    This script extracts articles from a structured text file and converts them
    into a JSONL format, where each article is stored as a separate JSON object.
--------------------------------------------------------------------------------
"""

import re
import json

# Define input and output files
input_file = "/home/cytech/Bulgattle/Bulgattle/databattle/ressources/extracted/PCT/PCT_articles.txt"
output_file = "/home/cytech/Bulgattle/Bulgattle/databattle/ressources/extracted/PCT/PCT_articles.jsonl"

# Regular expression to detect article headers
article_pattern = re.compile(r"^Article \d+$")

# Read the input file
with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Initialize storage variables
data = []
current_article = None
current_title = None
current_description = []
i = 0

# Process each line in the file
while i < len(lines):
    line = lines[i].strip()
    
    # Detect an article header
    if article_pattern.match(line):

        # If an article was being processed, save it before moving to the next one
        if current_article:
            data.append({
                "Article": current_article,
                "Title": current_title,
                "Description": " ".join(current_description).strip()
            })

        # Start a new article
        current_article = line
        i += 1 
        current_title = lines[i].strip() if i < len(lines) else ""
        current_description = []
    
    else:
        # Append content to the article's description
        current_description.append(line)

    i += 1

# Save the last article if any
if current_article:
    data.append({
        "Article": current_article,
        "Title": current_title,
        "Description": " ".join(current_description).strip()
    })

# Write the extracted data to a JSONL file
with open(output_file, "w", encoding="utf-8") as f:
    for entry in data:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"Conversion completed : {output_file}")
