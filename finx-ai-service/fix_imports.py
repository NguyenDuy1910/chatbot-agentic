#!/usr/bin/env python3
"""
Script to fix import paths from finx.* to src.web.*
"""

import os
import re
from pathlib import Path

# Define the mapping of old imports to new imports
IMPORT_MAPPINGS = {
    'from finx.constants': 'from src.web.constants.config',
    'from finx.internal.': 'from src.web.internal.',
    'from finx.models.': 'from src.web.models.',
    'from finx.routers': 'from src.web.routers',
    'from finx.utils.': 'from src.web.utils.',
    'from finx.config.': 'from src.web.config.',
}

def fix_imports_in_file(file_path):
    """Fix imports in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply each mapping
        for old_import, new_import in IMPORT_MAPPINGS.items():
            content = content.replace(old_import, new_import)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports in: {file_path}")
            return True
        
        return False
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix all imports"""
    # Get the directory containing this script (finx-ai-service root)
    script_dir = Path(__file__).parent
    
    # Find all Python files in src/web that might need fixing
    src_web_dir = script_dir / "src" / "web"
    
    if not src_web_dir.exists():
        print(f"Directory {src_web_dir} does not exist")
        return
    
    files_fixed = 0
    files_processed = 0
    
    # Walk through all Python files
    for py_file in src_web_dir.rglob("*.py"):
        files_processed += 1
        if fix_imports_in_file(py_file):
            files_fixed += 1
    
    print(f"\nProcessed {files_processed} files, fixed {files_fixed} files")

if __name__ == "__main__":
    main()
