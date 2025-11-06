#!/bin/bash
# Quick commands for managing the Lambda function and endpoint

FUNCTION_NAME="sagemaker-endpoint-invoker"
ENDPOINT_NAME="sagemaker-titanic-sklearn-endpoint-v2"
REGION="ap-southeast-1"

case "$1" in
  test)
    echo "Testing Lambda function..."
    aws lambda invoke \
      --function-name $FUNCTION_NAME \
      --payload '{"data": [3, 0, 22.0, 1, 0, 7.25, 0, 1, 0, 0, 0]}' \
      --region $REGION \
      --cli-binary-format raw-in-base64-out \
      response.json
    echo ""
    cat response.json | python3 -m json.tool
    rm response.json
    ;;
    
  logs)
    echo "Showing Lambda logs (last 5 minutes)..."
    aws logs tail /aws/lambda/$FUNCTION_NAME \
      --region $REGION \
      --since 5m \
      --follow
    ;;
    
  status)
    echo "Lambda Function Status:"
    aws lambda get-function \
      --function-name $FUNCTION_NAME \
      --region $REGION \
      --query 'Configuration.[State,LastModified,Runtime,MemorySize,Timeout]' \
      --output table
    echo ""
    echo "SageMaker Endpoint Status:"
    aws sagemaker describe-endpoint \
      --endpoint-name $ENDPOINT_NAME \
      --region $REGION \
      --query '[EndpointName,EndpointStatus,CreationTime]' \
      --output table
    ;;
    
  update)
    echo "Updating Lambda function code..."
    zip -q lambda_function.zip lambda_function.py
    aws lambda update-function-code \
      --function-name $FUNCTION_NAME \
      --zip-file fileb://lambda_function.zip \
      --region $REGION
    echo "✓ Lambda function updated"
    rm lambda_function.zip
    ;;
    
  invoke-direct)
    if [ -z "$2" ]; then
      echo "Usage: $0 invoke-direct '<json-payload>'"
      echo "Example: $0 invoke-direct '{\"data\": [3, 0, 22.0, 1, 0, 7.25, 0, 1, 0, 0, 0]}'"
      exit 1
    fi
    echo "Invoking with payload: $2"
    aws lambda invoke \
      --function-name $FUNCTION_NAME \
      --payload "$2" \
      --region $REGION \
      --cli-binary-format raw-in-base64-out \
      response.json
    cat response.json | python3 -m json.tool
    rm response.json
    ;;
    
  *)
    echo "Lambda Function & SageMaker Endpoint Manager"
    echo ""
    echo "Usage: $0 {test|logs|status|update|invoke-direct}"
    echo ""
    echo "Commands:"
    echo "  test          - Run a quick test with sample data"
    echo "  logs          - Tail CloudWatch logs (last 5 minutes)"
    echo "  status        - Show Lambda and endpoint status"
    echo "  update        - Update Lambda function code"
    echo "  invoke-direct - Invoke with custom JSON payload"
    echo ""
    echo "Examples:"
    echo "  $0 test"
    echo "  $0 logs"
    echo "  $0 status"
    echo "  $0 invoke-direct '{\"data\": [1, 1, 30.0, 0, 0, 100.0, 0, 0, 1, 0, 1]}'"
    exit 1
    ;;
esac
