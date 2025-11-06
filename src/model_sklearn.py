# src/model_sklearn.py
import argparse
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib # Used by SageMaker to save/load Sklearn models

def model_fn(model_dir):
    """
    Loads the model from the model_dir. This function is called by the 
    SageMaker Scikit-learn Model Server when the endpoint starts.
    """
    # Note: The model_dir points to the folder containing model.joblib
    model = joblib.load(os.path.join(model_dir, "model.joblib"))
    return model
# Add these functions to your src/model_sklearn.py
import numpy as np
import pandas as pd
from io import StringIO

def input_fn(request_body, request_content_type):
    """
    Custom input function to deserialize the CSV payload and enforce 2D shape.
    """
    if request_content_type == 'text/csv':
        # 1. Read the CSV data using Pandas (which handles reading the string)
        df = pd.read_csv(StringIO(request_body), header=None)
        
        # 2. Convert to NumPy array
        data = df.values
        
        # 3. CRITICAL FIX: Ensure 2D shape (1 sample, 11 features).
        # This fixes the ValueError: Expected 2D array, got 1D array instead.
        if data.ndim == 1:
            data = data.reshape(1, -1)
            
        return data
    
    raise ValueError(f"Unsupported content type: {request_content_type}")


def predict_fn(input_data, model):
    """
    Custom prediction function. The input_data is the NumPy array from input_fn.
    """
    # The data is already a 2D NumPy array, ready for prediction.
    prediction = model.predict(input_data)
    
    # Return as a list of lists for clean serialization via the default output_fn
    return prediction.tolist()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    # Hyperparameters are passed as arguments
    parser.add_argument('--n_estimators', type=int, default=100)
    parser.add_argument('--max_depth', type=int, default=10)
    
    # SageMaker passes the training data path as environment variables
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
    
    # SageMaker provides the path where the model should be saved
    parser.add_argument('--model_dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    
    args = parser.parse_args()

    # --- 1. Load Data ---
    # Data is available in the 'train' channel directory
    input_files = [os.path.join(args.train, file) for file in os.listdir(args.train)]
    if not input_files: raise FileNotFoundError("No input files found in SM_CHANNEL_TRAIN.")
    
    data = pd.read_csv(input_files[0]) # Load the 'processed_train.csv'

    # --- 2. Split Data ---
    X = data.drop(columns=['Survived'])
    y = data['Survived']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- 3. Train Model ---
    print(f"Training RandomForestClassifier with n_estimators={args.n_estimators}, max_depth={args.max_depth}")
    
    model = RandomForestClassifier(
        n_estimators=args.n_estimators, 
        max_depth=args.max_depth,
        random_state=42
    )
    model.fit(X_train, y_train)

    # --- 4. Evaluate and Log Metrics ---
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    # SageMaker automatically logs metrics printed in this format
    print(f"validation:accuracy: {accuracy}") 

    # --- 5. Save Model ---
    # Save the model artifact to the designated model directory
    joblib.dump(model, os.path.join(args.model_dir, "model.joblib"))
    print("Model successfully saved!")