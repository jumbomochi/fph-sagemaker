# Lambda Function Deployment Guide

## Overview
This guide will help you deploy a Lambda function that invokes your SageMaker endpoint.

## Prerequisites
- SageMaker endpoint deployed and running
- AWS CLI configured
- Appropriate IAM permissions

## Step 1: Create IAM Role for Lambda

Create an IAM role with the following trust policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

## Step 2: Attach IAM Policies

Attach these policies to the Lambda execution role:

1. **Basic Lambda Execution** (AWS Managed):
   - `AWSLambdaBasicExecutionRole` - For CloudWatch Logs

2. **SageMaker Invocation** (Custom Inline Policy):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:InvokeEndpoint"
      ],
      "Resource": "arn:aws:sagemaker:*:*:endpoint/*"
    }
  ]
}
```

For more restrictive access, replace the Resource with your specific endpoint ARN:
```
"Resource": "arn:aws:sagemaker:ap-southeast-1:123456789012:endpoint/your-endpoint-name"
```

## Step 3: Create Lambda Function

### Option A: Using AWS Console

1. Go to AWS Lambda Console
2. Click "Create function"
3. Choose "Author from scratch"
4. Function name: `sagemaker-endpoint-invoker`
5. Runtime: Python 3.11 (or 3.10)
6. Architecture: x86_64
7. Execution role: Use the role created in Step 1
8. Click "Create function"
9. Copy the code from `lambda_function.py` into the code editor
10. Add environment variable:
   - Key: `SAGEMAKER_ENDPOINT_NAME`
   - Value: Your endpoint name (e.g., `sklearn-titanic-endpoint`)
11. Adjust timeout to 30 seconds (Configuration → General configuration)
12. Click "Deploy"

### Option B: Using AWS CLI

1. Package the Lambda function:
```bash
cd /Users/huiliang/Documents/GitHub/fph-sagemaker
zip lambda_function.zip lambda_function.py
```

2. Create the function:
```bash
aws lambda create-function \
  --function-name sagemaker-endpoint-invoker \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_LAMBDA_ROLE \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda_function.zip \
  --timeout 30 \
  --memory-size 256 \
  --environment Variables={SAGEMAKER_ENDPOINT_NAME=your-endpoint-name} \
  --region ap-southeast-1
```

3. Update function code (if needed):
```bash
aws lambda update-function-code \
  --function-name sagemaker-endpoint-invoker \
  --zip-file fileb://lambda_function.zip \
  --region ap-southeast-1
```

## Step 4: Test the Lambda Function

### Test Event 1: Direct Invocation
```json
{
  "data": [3, 0, 22.0, 1, 0, 7.25, 0, 1, 0, 0, 0]
}
```

### Test Event 2: API Gateway Format
```json
{
  "body": "{\"data\": [3, 0, 22.0, 1, 0, 7.25, 0, 1, 0, 0, 0]}"
}
```

### Test Event 3: CSV String
```json
{
  "body": "3,0,22.0,1,0,7.25,0,1,0,0,0"
}
```

### Using AWS CLI
```bash
aws lambda invoke \
  --function-name sagemaker-endpoint-invoker \
  --payload '{"data": [3, 0, 22.0, 1, 0, 7.25, 0, 1, 0, 0, 0]}' \
  --region ap-southeast-1 \
  response.json

cat response.json
```

## Step 5: Connect to API Gateway (Optional)

1. Create REST API in API Gateway
2. Create POST method on a resource (e.g., `/predict`)
3. Integration type: Lambda Function
4. Select your Lambda function
5. Enable Lambda Proxy Integration
6. Deploy API to a stage (e.g., `prod`)
7. Test with curl:

```bash
curl -X POST https://YOUR_API_ID.execute-api.ap-southeast-1.amazonaws.com/prod/predict \
  -H "Content-Type: application/json" \
  -d '{"data": [3, 0, 22.0, 1, 0, 7.25, 0, 1, 0, 0, 0]}'
```

## Troubleshooting

### Common Issues

1. **"Unable to import module 'lambda_function'"**
   - Ensure the file is named `lambda_function.py`
   - Ensure handler is set to `lambda_function.lambda_handler`

2. **"User is not authorized to perform: sagemaker:InvokeEndpoint"**
   - Check IAM role has the correct policy
   - Verify the endpoint ARN in the policy matches your endpoint

3. **"Endpoint not found"**
   - Verify `SAGEMAKER_ENDPOINT_NAME` environment variable is set correctly
   - Check endpoint exists: `aws sagemaker describe-endpoint --endpoint-name YOUR_ENDPOINT`

4. **Timeout errors**
   - Increase Lambda timeout (Configuration → General → Timeout)
   - Check SageMaker endpoint is in "InService" state

5. **"Expected 2D array" error**
   - Ensure you're sending data in CSV format
   - Verify feature count matches model expectations (11 features)

### Monitoring

View Lambda logs:
```bash
aws logs tail /aws/lambda/sagemaker-endpoint-invoker --follow --region ap-southeast-1
```

## Sample Response

Success:
```json
{
  "statusCode": 200,
  "headers": {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*"
  },
  "body": "{\"prediction\": [0], \"endpoint\": \"sklearn-titanic-endpoint\"}"
}
```

Error:
```json
{
  "statusCode": 500,
  "body": "{\"error\": \"Endpoint not found\", \"message\": \"Failed to invoke SageMaker endpoint\"}"
}
```

## Next Steps

1. Add authentication (API Gateway API Keys, Cognito, or IAM)
2. Add request validation
3. Implement batch prediction support
4. Add monitoring and CloudWatch alarms
5. Set up auto-scaling for the endpoint
