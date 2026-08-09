import os

def print_tree(directory, prefix=""):
    """Recursively prints the directory structure in a clean tree format."""
    try:
        # Get all items and sort them alphabetically
        items = sorted(os.listdir(directory))
    except PermissionError:
        return

    # Filter out hidden files and Python cache folders to keep the map clean
    valid_items = [item for item in items if not item.startswith('.') and item != '__pycache__']

    for i, item in enumerate(valid_items):
        path = os.path.join(directory, item)
        is_last = (i == len(valid_items) - 1)
        
        # Visual connectors for the tree branches
        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{item}")
        
        # If the item is a folder, dive inside it
        if os.path.isdir(path):
            extension = "    " if is_last else "│   "
            print_tree(path, prefix + extension)

if __name__ == "__main__":
    target_dir = r"C:\BrainTrader"
    print("==================================================")
    print(f" BRAINTRADER ARCHITECTURE MAP")
    print("==================================================\n")
    print("BrainTrader/")
    print_tree(target_dir)
    print("\n==================================================")