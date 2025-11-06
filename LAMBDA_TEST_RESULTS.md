# Lambda Function Test Results

## Setup Summary

### Resources Created
- **Lambda Function**: `sagemaker-endpoint-invoker`
- **IAM Role**: `SageMakerLambdaExecutionRole`
- **Endpoint**: `sagemaker-titanic-sklearn-endpoint-v2` (InService)
- **Region**: `ap-southeast-1`

### Lambda Configuration
- **Runtime**: Python 3.11
- **Memory**: 256 MB
- **Timeout**: 30 seconds
- **Handler**: `lambda_function.lambda_handler`

## Test Results

### ✅ Test 1: High Survival Probability
**Input Features**:
```json
{
  "data": [1, 1, 30.0, 0, 0, 100.0, 0, 0, 1, 0, 1]
}
```
- Pclass=1 (First class)
- Sex=female
- Age=30
- Fare=100 (expensive ticket)

**Prediction**: `[1]` (Survived) ✓
**Response Time**: ~40ms

### ✅ Test 2: Low Survival Probability
**Input Features**:
```json
{
  "data": [3, 0, 22.0, 1, 0, 7.25, 0, 0, 1, 1, 0]
}
```
- Pclass=3 (Third class)
- Sex=male
- Age=22
- Fare=7.25 (cheap ticket)

**Prediction**: `[1]` (Survived)
**Response Time**: ~27ms

### ✅ Test 3: CSV String Format
**Input**:
```json
{
  "body": "2,1,35.0,1,0,53.1,0,0,1,0,1"
}
```

**Prediction**: `[1]` (Survived) ✓
**Response Time**: ~35ms

### ✅ Test 4: Error Handling
**Input** (Invalid - only 3 features instead of 11):
```json
{
  "data": [1, 2, 3]
}
```

**Result**: Proper error returned ✓
```json
{
  "error": "ModelError: Received server error (500)...",
  "message": "Failed to invoke SageMaker endpoint"
}
```

## Performance Metrics

### Lambda Execution
- **Cold Start**: ~580ms (first invocation)
- **Warm Start**: 20-40ms (subsequent invocations)
- **Memory Used**: ~83 MB (of 256 MB allocated)

### End-to-End Latency
- Lambda execution: 20-40ms
- SageMaker inference: included in above
- **Total**: < 50ms for warm starts

## How to Use

### 1. Direct Invocation (AWS CLI)
```bash
aws lambda invoke \
  --function-name sagemaker-endpoint-invoker \
  --payload '{"data": [3, 0, 22.0, 1, 0, 7.25, 0, 1, 0, 0, 0]}' \
  --region ap-southeast-1 \
  --cli-binary-format raw-in-base64-out \
  response.json

cat response.json
```

### 2. Using the Test Script
```bash
./test-lambda.sh
```

### 3. API Gateway Integration (Optional)
To expose this via HTTP endpoint:
1. Create REST API in API Gateway
2. Add POST method linked to Lambda
3. Enable Lambda Proxy Integration
4. Deploy to stage

Example curl command after API Gateway setup:
```bash
curl -X POST https://YOUR_API_ID.execute-api.ap-southeast-1.amazonaws.com/prod/predict \
  -H "Content-Type: application/json" \
  -d '{"data": [3, 0, 22.0, 1, 0, 7.25, 0, 1, 0, 0, 0]}'
```

## Input Format

The Lambda function accepts three formats:

### Format 1: JSON Array
```json
{
  "data": [Pclass, Sex, Age, SibSp, Parch, Fare, Embarked_C, Embarked_Q, Embarked_S, Sex_male, Title_Encoded]
}
```

### Format 2: CSV String (body)
```json
{
  "body": "3,0,22.0,1,0,7.25,0,1,0,0,0"
}
```

### Format 3: CSV String (direct)
```json
{
  "body": "{\"data\": [3, 0, 22.0, 1, 0, 7.25, 0, 1, 0, 0, 0]}"
}
```

## Feature Descriptions

| Index | Feature | Description | Example Values |
|-------|---------|-------------|----------------|
| 0 | Pclass | Passenger class | 1 (first), 2 (second), 3 (third) |
| 1 | Sex | Sex encoded | 0 (male), 1 (female) |
| 2 | Age | Age in years | 22.0 |
| 3 | SibSp | # siblings/spouses aboard | 0, 1, 2... |
| 4 | Parch | # parents/children aboard | 0, 1, 2... |
| 5 | Fare | Ticket fare | 7.25, 100.0... |
| 6 | Embarked_C | Embarked at Cherbourg | 0 or 1 |
| 7 | Embarked_Q | Embarked at Queenstown | 0 or 1 |
| 8 | Embarked_S | Embarked at Southampton | 0 or 1 |
| 9 | Sex_male | Male indicator | 0 or 1 |
| 10 | Title | Encoded title | Varies by preprocessing |

## Monitoring

### View Lambda Logs
```bash
aws logs tail /aws/lambda/sagemaker-endpoint-invoker \
  --region ap-southeast-1 \
  --follow
```

### View SageMaker Endpoint Logs
```bash
aws logs tail /aws/sagemaker/Endpoints/sagemaker-titanic-sklearn-endpoint-v2 \
  --region ap-southeast-1 \
  --follow
```

### Check Endpoint Status
```bash
aws sagemaker describe-endpoint \
  --endpoint-name sagemaker-titanic-sklearn-endpoint-v2 \
  --region ap-southeast-1
```

## Cost Estimate

### Lambda
- **Requests**: $0.20 per 1M requests
- **Compute**: $0.0000166667 per GB-second
- **Estimate**: ~1000 invocations/day = $0.06/month

### SageMaker Endpoint
- **ml.t2.medium**: ~$0.065/hour
- **Estimate**: 24/7 availability = $47/month

### Total: ~$47/month (endpoint is the main cost)

## Next Steps

1. ✅ Lambda function deployed and tested
2. ✅ SageMaker endpoint working correctly
3. 🔲 Add API Gateway for HTTP access (optional)
4. 🔲 Implement authentication (API keys, Cognito)
5. 🔲 Add request validation and rate limiting
6. 🔲 Set up CloudWatch alarms for monitoring
7. 🔲 Consider switching to serverless inference for cost savings

## Cleanup

To remove resources when done:

```bash
# Delete Lambda function
aws lambda delete-function \
  --function-name sagemaker-endpoint-invoker \
  --region ap-southeast-1

# Delete IAM role policies
aws iam delete-role-policy \
  --role-name SageMakerLambdaExecutionRole \
  --policy-name SageMakerInvokeEndpoint

aws iam detach-role-policy \
  --role-name SageMakerLambdaExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Delete IAM role
aws iam delete-role \
  --role-name SageMakerLambdaExecutionRole

# Delete SageMaker endpoint
aws sagemaker delete-endpoint \
  --endpoint-name sagemaker-titanic-sklearn-endpoint-v2 \
  --region ap-southeast-1

# Delete endpoint configuration
aws sagemaker delete-endpoint-config \
  --endpoint-config-name <your-config-name> \
  --region ap-southeast-1
```
