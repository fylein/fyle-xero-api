import os

def load_sql_from_file_safe(file_path):
    """
    Safely loads SQL content from a given file path.
    Logs a warning if the file does not exist and returns an empty SQL string.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"SQL file not found: {file_path}. Ensure the file exists and is accessible.")
    
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
