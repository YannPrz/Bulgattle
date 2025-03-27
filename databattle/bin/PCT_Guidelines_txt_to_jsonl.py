"""
--------------------------------------------------------------------------------
Author: Camille Solacroup
Date: 2025-03-25
Description:
    This script converts extracted PCT Guidelines text files into structured 
    JSON format, organizing content into chapters, sections, and subsections.
--------------------------------------------------------------------------------
"""

import os
import json
import re



# Define input and output folders
input_folder = "/home/cytech/Bulgattle/Bulgattle/databattle/ressources/extracted/PCT_guidelines"
output_folder = "/home/cytech/Bulgattle/Bulgattle/databattle/ressources/extracted/PCT_guidelines_jsonl"


# Create output directory if it does not exist
os.makedirs(output_folder, exist_ok=True)

# Regular expressions to detect structure in the text
chapter_pattern = re.compile(r"^(Chapter\s+[IVXLCDM]+)\s+–\s+(.+)$", re.IGNORECASE)
section_pattern = re.compile(r"^(\d+\. )+(.+)$")  
subsection_pattern = re.compile(r"^(\d+\.\d+)\s+(.+)")  
subsubsection_pattern = re.compile(r"^(\d+\.\d+\.\d+)\s+(.+)") 

def convert_txt_to_json(txt_path: str, json_path: str):
    """
    Reads a structured text file and converts it into a hierarchical JSON format.

    Args:
        txt_path (str): Path to the input text file.
        json_path (str): Path where the JSON file will be saved.

    Returns:
        None
    """
    with open(txt_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    data = {}
    current_chapter = None
    current_section = None
    current_subsection = None
    current_subsubsection = None

    for line in lines:
        line = line.strip()

        if not line:
            continue
        
        # Detect chapter
        chapter_match = chapter_pattern.match(line)
        if chapter_match:
            current_chapter = chapter_match.group(1) + " – " + chapter_match.group(2)
            data[current_chapter] = {}
            current_section = None
            current_subsection = None
            current_subsubsection = None
            continue
        
        # Detect main section (X.)
        section_match = section_pattern.match(line)
        if section_match:
            current_section = section_match.group(1)
            section_title = section_match.group(2)

            # Initialize the section if it does not exist
            if current_chapter not in data:
                data[current_chapter] = {}

            data[current_chapter].setdefault(current_section, {
                "title": section_title,  # Section title without its number
                "subsections": {}
            })
            current_subsection = None
            current_subsubsection = None
            continue
        
        # Detect subsection (X.X)
        subsection_match = subsection_pattern.match(line)
        if subsection_match:
            if not current_section:
                print(f"Warning: Subsection {subsection_match.group(1)} found before any section.")
                continue

            current_subsection = subsection_match.group(1)
            subsection_title = subsection_match.group(2)

            # Initialize subsection if it does not exist
            data[current_chapter][current_section].setdefault("subsections", {})

            # Store content directly under the subsection without adding an extra title
            data[current_chapter][current_section]["subsections"].setdefault(current_subsection, {
                "content": subsection_title # Title becomes the beginning of the content
            })
            current_subsubsection = None
            continue

        # Detect sub-subsection (X.X.X)
        subsubsection_match = subsubsection_pattern.match(line)
        if subsubsection_match:
            if not current_section or not current_subsection:
                print(f"Warning: Sub-subsection {subsubsection_match.group(1)} found without a parent subsection.")
                continue

            current_subsubsection = subsubsection_match.group(1)
            subsubsection_title = subsubsection_match.group(2)

            # Initialize sub-subsection if it does not exist
            data[current_chapter][current_section]["subsections"][current_subsection].setdefault("subsections", {})

            # Add a sub-subsection with its title and content
            data[current_chapter][current_section]["subsections"][current_subsection]["subsections"].setdefault(
                current_subsubsection, {
                    
                    "content": subsubsection_title
                }
            )
            continue

        # Add content to the appropriate section
        if current_subsubsection:
            data[current_chapter][current_section]["subsections"][current_subsection]["subsections"][current_subsubsection]["content"] += " " + line
        elif current_subsection:
            # For subsections, add content, not a title
            data[current_chapter][current_section]["subsections"][current_subsection].setdefault("content", "")
            data[current_chapter][current_section]["subsections"][current_subsection]["content"] += " " + line
        elif current_section:
            # For subsections, add content, not a title
            data[current_chapter][current_section].setdefault("content", "")
            data[current_chapter][current_section]["content"] += " " + line

    # Save the result as a JSON file
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)

# Process all .txt files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".txt"):
        txt_path = os.path.join(input_folder, filename)
        json_filename = filename.replace(".txt", ".jsonl")
        json_path = os.path.join(output_folder, json_filename)

        convert_txt_to_json(txt_path, json_path)
        print(f"Converted {filename} → {json_filename}")

print("Conversion completed for all files.")