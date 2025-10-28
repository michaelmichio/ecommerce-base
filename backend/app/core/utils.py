import os

def delete_file_safe(file_path: str, base_dir: str) -> bool:
    """
    Safely delete a file only if it's inside the base_dir.
    Returns True if file deleted, False otherwise.
    """
    if not file_path:
        return False

    abs_path = os.path.abspath(file_path)
    base_dir = os.path.abspath(base_dir)

    # Ensure the file is inside the upload directory
    if abs_path.startswith(base_dir) and os.path.exists(abs_path):
        try:
            os.remove(abs_path)
            print(f"✅ Deleted file: {abs_path}")
            return True
        except Exception as e:
            print(f"⚠️ Failed to delete file {abs_path}: {e}")
    else:
        print(f"⛔ Skipped unsafe delete: {abs_path}")

    return False
