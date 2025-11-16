import difflib
import os
from pathlib import Path

def calculate_similarity(answer1, answer2, case_sensitive=False):
    """Calculate similarity between two strings using difflib.SequenceMatcher"""
    if case_sensitive:
        return difflib.SequenceMatcher(None, answer1.strip(), answer2.strip()).ratio()
    else:
        return difflib.SequenceMatcher(None, answer1.lower().strip(), answer2.lower().strip()).ratio()

#a function that checks if a string begins with >> and returns a clean string without the >> if it does or None if it does not
def case_sensitive_answer(answer):
    """Check if a string begins with >> and return a clean string without the >> if it does, or None if it does not"""
    if answer.startswith(">>"):
        return answer[2:].strip()
    return None

def get_documents_folder():
    """Get the OS-independent Documents folder path"""
    if os.name == 'nt':  # Windows
        return Path.home() / 'Documents'
    else:  # Unix-like (Linux, macOS)
        return Path.home() / 'Documents'

