import difflib
import os
from pathlib import Path

def calculate_similarity(answer1, answer2):
    """Calculate similarity between two strings using difflib.SequenceMatcher"""
    return difflib.SequenceMatcher(None, answer1.lower().strip(), answer2.lower().strip()).ratio()


def get_documents_folder():
    """Get the OS-independent Documents folder path"""
    if os.name == 'nt':  # Windows
        return Path.home() / 'Documents'
    else:  # Unix-like (Linux, macOS)
        return Path.home() / 'Documents'

