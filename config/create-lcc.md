Step 1: Create the GitHub Secret in AWS Secrets Manager

    Generate a GitHub PAT: Go to your GitHub account settings, navigate to 
        Developer settings > Personal access tokens > Tokens (classic). 
        Generate a new token with at least the repo scope. Copy the token immediately!
    
    Create the Secret: Go to the AWS Console > Secrets Manager.
        Click Store a new secret.
        Choose Other type of secret.
        Use the following Key/Value pairs (this format is standard for Git credentials):
            Key: username | Value: Your GitHub username
            Key: password | Value: Your GitHub Personal Access Token (PAT)
        Name the secret clearly (e.g., sagemaker/github-pat). Note the Secret ARN.

Step 2: Update the SageMaker Execution Role
Your SageMaker Space's execution role needs permission to retrieve this secret.
    Find Your Role: Get the IAM Role ARN for your SageMaker Space's user profile.
    Attach Policy: Attach an IAM Policy to that role that grants secretsmanager:GetSecretValue permission to the ARN of the secret you created in Step 1.

inside your terminal, run this:

LCC_CONTENT=$(cat config/sagemaker-sync-lcc.sh | base64)

then run this:
aws sagemaker create-studio-lifecycle-config \
--region ap-southeast-1 \
--studio-lifecycle-config-name sagemaker-studio-jupyterlab-lcc \
--studio-lifecycle-config-content $LCC_CONTENT \
--studio-lifecycle-config-app-type JupyterLab