#!/bin/bash
# Test script for Lambda function invoking SageMaker endpoint

set -e

FUNCTION_NAME="sagemaker-endpoint-invoker"
REGION="ap-southeast-1"

echo "=================================="
echo "Lambda Function Test Suite"
echo "=================================="
echo ""

# Test 1: Passenger who survived (prediction should be 1)
echo "Test 1: High survival probability passenger"
echo "Features: Pclass=1, Sex=female, Age=30, SibSp=0, Parch=0, Fare=100, Embarked_C=0, Embarked_Q=0, Embarked_S=1, Sex_male=0, Title_Miss=1"
cat > test1.json << 'EOF'
{
  "data": [1, 1, 30.0, 0, 0, 100.0, 0, 0, 1, 0, 1]
}
EOF

aws lambda invoke \
  --function-name $FUNCTION_NAME \
  --payload file://test1.json \
  --region $REGION \
  --cli-binary-format raw-in-base64-out \
  response1.json > /dev/null

echo "Response:"
cat response1.json | python3 -c "import json,sys; r=json.load(sys.stdin); print(json.dumps(json.loads(r['body']), indent=2))"
echo ""

# Test 2: Passenger who likely died (prediction should be 0)
echo "Test 2: Low survival probability passenger"
echo "Features: Pclass=3, Sex=male, Age=22, SibSp=1, Parch=0, Fare=7.25, Embarked_C=0, Embarked_Q=0, Embarked_S=1, Sex_male=1, Title_Mr=1"
cat > test2.json << 'EOF'
{
  "data": [3, 0, 22.0, 1, 0, 7.25, 0, 0, 1, 1, 0]
}
EOF

aws lambda invoke \
  --function-name $FUNCTION_NAME \
  --payload file://test2.json \
  --region $REGION \
  --cli-binary-format raw-in-base64-out \
  response2.json > /dev/null

echo "Response:"
cat response2.json | python3 -c "import json,sys; r=json.load(sys.stdin); print(json.dumps(json.loads(r['body']), indent=2))"
echo ""

# Test 3: Using CSV string format
echo "Test 3: CSV string format"
cat > test3.json << 'EOF'
{
  "body": "2,1,35.0,1,0,53.1,0,0,1,0,1"
}
EOF

aws lambda invoke \
  --function-name $FUNCTION_NAME \
  --payload file://test3.json \
  --region $REGION \
  --cli-binary-format raw-in-base64-out \
  response3.json > /dev/null

echo "Response:"
cat response3.json | python3 -c "import json,sys; r=json.load(sys.stdin); print(json.dumps(json.loads(r['body']), indent=2))"
echo ""

# Test 4: Batch prediction (multiple passengers)
echo "Test 4: Testing error handling with invalid input"
cat > test4.json << 'EOF'
{
  "data": [1, 2, 3]
}
EOF

aws lambda invoke \
  --function-name $FUNCTION_NAME \
  --payload file://test4.json \
  --region $REGION \
  --cli-binary-format raw-in-base64-out \
  response4.json > /dev/null 2>&1 || true

echo "Response:"
cat response4.json | python3 -c "import json,sys; r=json.load(sys.stdin); print(json.dumps(json.loads(r['body']), indent=2))" || cat response4.json
echo ""

echo "=================================="
echo "Test Suite Complete!"
echo "=================================="

# Cleanup
rm -f test*.json response*.json

echo ""
echo "Summary:"
echo "✓ Test 1: High survival probability → Prediction should be 1 (Survived)"
echo "✓ Test 2: Low survival probability → Prediction should be 0 (Died)"
echo "✓ Test 3: CSV string format → Should work"
echo "✓ Test 4: Invalid input → Should return error message"
