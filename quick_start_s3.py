#!/usr/bin/env python3
"""
Quick start script for AWS S3 setup
Interactive script to help configure AWS S3 for the first time
"""

import os
import sys
from pathlib import Path


def print_banner():
    """Print welcome banner"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        AWS S3 Setup - Classroom Assistant                   ║
║        Quick Start Configuration                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")


def get_input(prompt, default=None):
    """Get user input with optional default"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        user_input = input(f"{prompt}: ").strip()
        while not user_input:
            print("This field is required!")
            user_input = input(f"{prompt}: ").strip()
        return user_input


def update_env_file(config):
    """Update .env file with AWS configuration"""
    env_path = Path(__file__).parent / '.env'
    
    # Read existing .env
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Remove old AWS/Supabase config
    new_lines = []
    skip_section = False
    
    for line in lines:
        if line.strip().startswith('# AWS S3 Configuration') or \
           line.strip().startswith('# Supabase Configuration'):
            skip_section = True
            continue
        
        if skip_section and line.strip() and not line.strip().startswith('#') and '=' in line:
            key = line.split('=')[0].strip()
            if key.startswith('AWS_') or key.startswith('SUPABASE_'):
                continue
            else:
                skip_section = False
        
        if not skip_section:
            new_lines.append(line)
    
    # Add AWS configuration
    aws_config = f"""
# AWS S3 Configuration
AWS_ACCESS_KEY_ID={config['access_key']}
AWS_SECRET_ACCESS_KEY={config['secret_key']}
AWS_REGION={config['region']}
AWS_S3_BUCKET={config['bucket']}
"""
    
    # Write updated .env
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
        f.write(aws_config)
    
    print(f"\n✓ Configuration saved to {env_path}")


def main():
    """Main function"""
    print_banner()
    
    print("This script will help you configure AWS S3 for audio file storage.\n")
    print("You'll need:")
    print("  1. AWS Account")
    print("  2. IAM User with S3 permissions")
    print("  3. Access Key ID and Secret Access Key\n")
    
    proceed = input("Do you have these ready? (yes/no): ").strip().lower()
    if proceed not in ['yes', 'y']:
        print("\nPlease set up your AWS account first:")
        print("  1. Go to https://aws.amazon.com/")
        print("  2. Create an account or sign in")
        print("  3. Go to IAM → Users → Create User")
        print("  4. Attach 'AmazonS3FullAccess' policy")
        print("  5. Create access key and save credentials")
        print("\nRun this script again when ready!")
        return 1
    
    print("\n" + "="*60)
    print("AWS Credentials Configuration")
    print("="*60)
    
    config = {}
    
    # Get AWS credentials
    print("\nEnter your AWS credentials:")
    config['access_key'] = get_input("AWS Access Key ID")
    config['secret_key'] = get_input("AWS Secret Access Key")
    
    # Get region
    print("\nSelect AWS Region:")
    print("  1. us-east-1 (US East - N. Virginia) [Recommended]")
    print("  2. us-west-2 (US West - Oregon)")
    print("  3. eu-west-1 (Europe - Ireland)")
    print("  4. ap-southeast-1 (Asia Pacific - Singapore)")
    print("  5. Custom region")
    
    region_choice = get_input("Choose region (1-5)", "1")
    
    regions = {
        '1': 'us-east-1',
        '2': 'us-west-2',
        '3': 'eu-west-1',
        '4': 'ap-southeast-1'
    }
    
    if region_choice in regions:
        config['region'] = regions[region_choice]
    else:
        config['region'] = get_input("Enter custom region", "us-east-1")
    
    # Get bucket name
    print("\nS3 Bucket Name:")
    print("  - Must be globally unique")
    print("  - Use lowercase letters, numbers, and hyphens only")
    config['bucket'] = get_input("Bucket name", "classroom-assistant-audio")
    
    # Confirm configuration
    print("\n" + "="*60)
    print("Configuration Summary")
    print("="*60)
    print(f"Access Key ID: {config['access_key'][:4]}...{config['access_key'][-4:]}")
    print(f"Secret Key: {config['secret_key'][:4]}...{config['secret_key'][-4:]}")
    print(f"Region: {config['region']}")
    print(f"Bucket: {config['bucket']}")
    print("="*60)
    
    confirm = input("\nSave this configuration? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Configuration cancelled.")
        return 1
    
    # Update .env file
    update_env_file(config)
    
    # Run setup script
    print("\n" + "="*60)
    print("Setting up S3 Bucket")
    print("="*60)
    
    run_setup = input("\nRun bucket setup now? (yes/no): ").strip().lower()
    if run_setup in ['yes', 'y']:
        print("\nRunning setup script...\n")
        os.system(f"{sys.executable} setup_s3_bucket.py")
    else:
        print("\nYou can run the setup later with:")
        print("  python setup_s3_bucket.py")
    
    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Start your backend: python app.py")
    print("  2. Test endpoints: python test_all_endpoints.py")
    print("  3. Upload audio files through the API")
    print("\nFor more information, see S3_MIGRATION_GUIDE.md")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {str(e)}")
        sys.exit(1)
