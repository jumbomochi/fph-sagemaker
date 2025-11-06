# container/serve/predictor.py
import os
import joblib
import pandas as pd
from io import StringIO
import json

# The path where the model artifact (model.joblib) will be saved by SageMaker
MODEL_PATH = os.path.join(os.environ.get('SM_MODEL_DIR'), 'model.joblib')

class SklearnPredictor(object):
    """A simple class to load the model and make predictions."""

    def __init__(self):
        # Load the model artifact
        self.model = joblib.load(MODEL_PATH)
        print("Model loaded successfully.")

    def predict(self, input_data):
        # Convert JSON string input back to a DataFrame or numpy array
        # Assuming input_data is a CSV string for simplicity
        try:
            df = pd.read_csv(StringIO(input_data), header=None)
            # Remove the 'Survived' column if it was inadvertently passed (we only want features)
            # For simplicity, we assume the input has the same number of features as the training data
            return self.model.predict(df.values)
        except Exception as e:
            print(f"Prediction error: {e}")
            return [0] # Return a default if parsing fails
        
# --- SageMaker Specific Hooks ---

def model_fn(model_dir):
    """Loads the model from disk."""
    return SklearnPredictor()

def transform_fn(model, data, input_content_type, output_content_type):
    """
    Called by the endpoint to perform prediction.
    :param model: The object returned by model_fn
    :param data: The request payload
    :param input_content_type: The content type of the request
    :param output_content_type: The content type for the response
    """
    if input_content_type == 'text/csv':
        prediction = model.predict(data.decode('utf-8'))
        
        # Convert prediction result to JSON string
        response_body = json.dumps(prediction.tolist())
        return response_body, output_content_type
    
    raise ValueError(f"Content type {input_content_type} not supported.")