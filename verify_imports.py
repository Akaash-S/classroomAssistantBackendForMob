#!/usr/bin/env python3
"""
Script to verify all imports are correct before deployment
Checks for any remaining Supabase storage imports
"""

import os
import sys
import re
from pathlib import Path

def check_file_for_supabase_imports(file_path):
    """Check a single file for Supabase storage imports"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Patterns to check
        patterns = [
            r'from\s+services\.supabase_storage\s+import',
            r'import\s+.*supabase_storage',
            r'SupabaseStorageService\s*\(',
        ]
        
        issues = []
        for i, line in enumerate(content.split('\n'), 1):
            for pattern in patterns:
                if re.search(pattern, line):
                    issues.append((i, line.strip()))
        
        return issues
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def main():
    """Main function"""
    print("=" * 60)
    print("Verifying Imports - Checking for Supabase Storage References")
    print("=" * 60)
    print()
    
    # Files to check
    backend_dir = Path(__file__).parent
    
    # Python files to check (excluding test files and supabase_storage.py itself)
    files_to_check = [
        backend_dir / 'app.py',
        backend_dir / 'routes' / 'lectures.py',
        backend_dir / 'routes' / 'ai.py',
        backend_dir / 'services' / 'background_processor.py',
    ]
    
    # Add all route files
    routes_dir = backend_dir / 'routes'
    if routes_dir.exists():
        for file in routes_dir.glob('*.py'):
            if file.name != '__init__.py':
                files_to_check.append(file)
    
    all_clear = True
    
    for file_path in files_to_check:
        if not file_path.exists():
            continue
            
        issues = check_file_for_supabase_imports(file_path)
        
        if issues:
            all_clear = False
            print(f"❌ {file_path.relative_to(backend_dir)}")
            for line_num, line in issues:
                print(f"   Line {line_num}: {line}")
            print()
        else:
            print(f"✓ {file_path.relative_to(backend_dir)}")
    
    print()
    print("=" * 60)
    
    if all_clear:
        print("✅ All imports verified! No Supabase storage references found.")
        print("Ready for deployment!")
        return 0
    else:
        print("❌ Found Supabase storage references!")
        print("Please update the files above to use S3StorageService instead.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
