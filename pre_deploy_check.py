#!/usr/bin/env python3
"""
Pre-deployment check script
Verifies everything is ready for Render deployment
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def check_env_variables():
    """Check required environment variables"""
    print_header("1. Checking Environment Variables")
    
    required_vars = {
        'AWS_ACCESS_KEY_ID': 'AWS Access Key',
        'AWS_SECRET_ACCESS_KEY': 'AWS Secret Key',
        'AWS_REGION': 'AWS Region',
        'AWS_S3_BUCKET': 'S3 Bucket Name',
    }
    
    optional_vars = {
        'DATABASE_URL': 'Database Connection',
        'RAPIDAPI_KEY': 'RapidAPI Key',
        'GEMINI_API_KEY': 'Gemini API Key',
        'SECRET_KEY': 'Flask Secret Key',
    }
    
    all_good = True
    
    print("\nRequired Variables:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != f'your-{var.lower().replace("_", "-")}':
            print(f"  ✓ {description}: Configured")
        else:
            print(f"  ✗ {description}: NOT CONFIGURED")
            all_good = False
    
    print("\nOptional Variables (recommended for production):")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✓ {description}: Configured")
        else:
            print(f"  ⚠ {description}: Not configured")
    
    return all_good

def check_imports():
    """Check for old Supabase imports"""
    print_header("2. Checking Imports")
    
    import subprocess
    result = subprocess.run(
        [sys.executable, 'verify_imports.py'],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent
    )
    
    # Check if the output contains success message
    if "All imports verified" in result.stdout or result.returncode == 0:
        print("  ✓ All imports verified")
        return True
    else:
        print("  ✗ Import issues found")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return False

def check_files():
    """Check required files exist"""
    print_header("3. Checking Required Files")
    
    required_files = [
        'Dockerfile',
        'requirements.txt',
        'app.py',
        'services/s3_storage.py',
        'routes/lectures.py',
        'routes/ai.py',
    ]
    
    all_exist = True
    for file in required_files:
        file_path = Path(file)
        if file_path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            all_exist = False
    
    return all_exist

def check_dockerfile():
    """Check Dockerfile configuration"""
    print_header("4. Checking Dockerfile")
    
    dockerfile_path = Path('Dockerfile')
    if not dockerfile_path.exists():
        print("  ✗ Dockerfile not found")
        return False
    
    with open(dockerfile_path, 'r') as f:
        content = f.read()
    
    checks = {
        '${PORT': 'Dynamic port binding',
        'gunicorn': 'Gunicorn server',
        'app:app': 'Application entry point',
        'HEALTHCHECK': 'Health check configured',
    }
    
    all_good = True
    for check, description in checks.items():
        if check in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - MISSING")
            all_good = False
    
    return all_good

def check_requirements():
    """Check requirements.txt"""
    print_header("5. Checking Requirements")
    
    req_path = Path('requirements.txt')
    if not req_path.exists():
        print("  ✗ requirements.txt not found")
        return False
    
    with open(req_path, 'r') as f:
        content = f.read()
    
    required_packages = {
        'boto3': 'AWS SDK (for S3)',
        'Flask': 'Flask framework',
        'gunicorn': 'Production server',
        'psycopg2-binary': 'PostgreSQL driver',
    }
    
    deprecated_packages = {
        'supabase': 'Old Supabase package (should be removed)',
    }
    
    all_good = True
    
    print("\nRequired Packages:")
    for package, description in required_packages.items():
        if package.lower() in content.lower():
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description} - MISSING")
            all_good = False
    
    print("\nDeprecated Packages (should not be present):")
    for package, description in deprecated_packages.items():
        if package.lower() in content.lower():
            print(f"  ✗ {description} - FOUND (should be removed)")
            all_good = False
        else:
            print(f"  ✓ {description} - Not found (good)")
    
    return all_good

def main():
    """Main function"""
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                                                              ║")
    print("║        Pre-Deployment Check                                 ║")
    print("║        Render Platform                                      ║")
    print("║                                                              ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    
    checks = [
        ("Environment Variables", check_env_variables),
        ("Imports", check_imports),
        ("Required Files", check_files),
        ("Dockerfile", check_dockerfile),
        ("Requirements", check_requirements),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n  ✗ Error during {name} check: {str(e)}")
            results.append((name, False))
    
    # Summary
    print_header("Summary")
    
    all_passed = all(result for _, result in results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✅ All checks passed! Ready for deployment.")
        print("\nNext steps:")
        print("  1. Commit and push to GitHub")
        print("  2. Deploy on Render")
        print("  3. Configure environment variables on Render")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Update .env with AWS credentials")
        print("  - Run: pip install -r requirements.txt")
        print("  - Verify all files are present")
        return 1

if __name__ == "__main__":
    sys.exit(main())
