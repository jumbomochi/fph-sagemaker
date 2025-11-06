# src/model_sklearn.py
import argparse
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib # Used by SageMaker to save/load Sklearn models

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