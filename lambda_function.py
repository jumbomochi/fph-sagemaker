"""
AWS Lambda function to invoke a SageMaker endpoint.
This function accepts CSV data and returns predictions from the endpoint.
"""
import json
import boto3
import os

# Initialize the SageMaker runtime client
sagemaker_runtime = boto3.client('sagemaker-runtime')

# Get endpoint name from environment variable
ENDPOINT_NAME = os.environ.get('SAGEMAKER_ENDPOINT_NAME', 'your-endpoint-name')


def lambda_handler(event, context):
    """
    Lambda handler function to invoke SageMaker endpoint.
    
    Expected event format (API Gateway):
    {
        "body": "0,1,2,3,4,5,6,7,8,9,10"  # CSV format matching your model's features
    }
    
    Or direct invocation:
    {
        "data": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # List of feature values
    }
    """
    try:
        # Parse input data
        if 'body' in event:
            # API Gateway integration - body is a string
            body = event['body']
            if isinstance(body, str):
                # Check if it's JSON string
                try:
                    body = json.loads(body)
                    if 'data' in body:
                        # Convert list to CSV string
                        csv_data = ','.join(map(str, body['data']))
                    else:
                        csv_data = body
                except json.JSONDecodeError:
                    # Assume it's already CSV string
                    csv_data = body
        elif 'data' in event:
            # Direct invocation with data array
            csv_data = ','.join(map(str, event['data']))
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Invalid input. Provide "body" (CSV string) or "data" (array).'
                })
            }
        
        print(f"Invoking endpoint: {ENDPOINT_NAME}")
        print(f"Payload: {csv_data}")
        
        # Invoke the SageMaker endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=ENDPOINT_NAME,
            ContentType='text/csv',
            Body=csv_data
        )
        
        # Read and decode the response
        result = response['Body'].read().decode('utf-8')
        
        # Parse the prediction result
        try:
            prediction = json.loads(result)
        except json.JSONDecodeError:
            # If response is not JSON, return as-is
            prediction = result
        
        print(f"Prediction: {prediction}")
        
        # Return successful response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Enable CORS if needed
            },
            'body': json.dumps({
                'prediction': prediction,
                'endpoint': ENDPOINT_NAME
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to invoke SageMaker endpoint'
            })
        }


# For local testing
if __name__ == '__main__':
    # Test event with sample data (11 features for your model)
    test_event = {
        'data': [3, 0, 22.0, 1, 0, 7.25, 0, 1, 0, 0, 0]
    }
    
    # Mock context
    class MockContext:
        def __init__(self):
            self.function_name = 'test-function'
            self.memory_limit_in_mb = 128
            self.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:test'
            self.aws_request_id = 'test-request-id'
    
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
