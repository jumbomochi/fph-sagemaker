#!/bin/bash
set -eux

# --- 1. Git Credentials Setup (FROM Secrets Manager Helper) ---

# Configuration for Secrets Manager
AWS_REGION="ap-southeast-1"
GITHUB_SECRET_NAME="sagemaker/github-pat" # REPLACE with your secret name
GIT_USERNAME="jumbomochi" 
GIT_EMAIL="huiliang@gmail.com"

# Create the Python Helper Script
cat > /home/sagemaker-user/git-credential-helper.py << EOF
#!/usr/bin/env python3
import boto3
import json
import sys

# The credential helper is called by Git.
# It reads credentials request lines (e.g., 'host=github.com') from stdin.
if sys.argv[1] == 'get':
    client = boto3.client('secretsmanager')
    try:
        response = client.get_secret_value(SecretId='${GITHUB_SECRET_NAME}')
        secret = json.loads(response['SecretString'])
        
        # Git expects 'username' and 'password' keys on stdout
        print(f"username={secret['username']}")
        print(f"password={secret['password']}")
    except Exception as e:
        # Fails silently to allow manual entry if secret access fails
        sys.exit(0)
EOF

chmod +x /home/sagemaker-user/git-credential-helper.py

# Configure Git to use the credential helper and set user identity
git config --global credential.helper "/home/sagemaker-user/git-credential-helper.py"
git config --global user.name "$GIT_USERNAME"
git config --global user.email "$GIT_EMAIL"

echo "Git credentials configured."

# --- 2. Git Synchronization ---

REPO_DIR="sagemaker-ml-repo"
# Use the HTTPS URL now that the credential helper is configured
REPO_URL="https://github.com/jumbomochi/fph-sagemaker.git"
SM_HOME="/home/sagemaker-user"

cd $SM_HOME

if [ -d "$REPO_DIR" ]; then
    echo "Repository directory exists. Performing git pull..."
    cd $REPO_DIR
    git pull origin main 
else
    echo "Repository directory does not exist. Performing git clone..."
    git clone $REPO_URL
fi

echo "Unified Git setup complete."