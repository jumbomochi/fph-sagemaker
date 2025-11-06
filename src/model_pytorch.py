# src/model_pytorch.py
import argparse
import os
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# --- 1. Define PyTorch Model ---
class TitanicModel(nn.Module):
    def __init__(self, input_size):
        super(TitanicModel, self).__init__()
        self.layer_1 = nn.Linear(input_size, 64)
        self.relu = nn.ReLU()
        self.layer_2 = nn.Linear(64, 32)
        self.output = nn.Linear(32, 1) # Binary classification output
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.layer_1(x))
        x = self.relu(self.layer_2(x))
        x = self.sigmoid(self.output(x))
        return x

# --- 2. Define Custom Dataset ---
class TitanicDataset(Dataset):
    def __init__(self, X_data, y_data):
        self.X_data = torch.from_numpy(X_data).float()
        self.y_data = torch.from_numpy(y_data).float().unsqueeze(1)
        
    def __getitem__(self, index):
        return self.X_data[index], self.y_data[index]
        
    def __len__ (self):
        return len(self.X_data)

# --- 3. Main Training Function ---
def train(args):
    # Load Data
    input_files = [os.path.join(args.train, file) for file in os.listdir(args.train)]
    data = pd.read_csv(input_files[0]) 

    X = data.drop(columns=['Survived']).values
    y = data['Survived'].values
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # DataLoader setup
    train_dataset = TitanicDataset(X_train, y_train)
    train_loader = DataLoader(dataset=train_dataset, batch_size=args.batch_size, shuffle=True)
    
    # Model, Loss, Optimizer
    input_size = X_train.shape[1]
    model = TitanicModel(input_size)
    criterion = nn.BCELoss() # Binary Cross-Entropy Loss
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)

    # Training Loop
    for epoch in range(args.epochs):
        for X_batch, y_batch in train_loader:
            optimizer.zero_grad()
            y_pred = model(X_batch)
            loss = criterion(y_pred, y_batch)
            loss.backward()
            optimizer.step()
        
    # Simple Evaluation (for logging metric)
    model.eval()
    with torch.no_grad():
        test_dataset = TitanicDataset(X_test, y_test)
        X_test_tensor, y_test_tensor = test_dataset[:]
        y_pred_tensor = model(X_test_tensor)
        y_pred_class = (y_pred_tensor >= 0.5).int()
        accuracy = accuracy_score(y_test_tensor.numpy(), y_pred_class.numpy())
        print(f"validation:accuracy: {accuracy}")

    # Save the model state dict to the designated model directory
    print("Model state dictionary saved!")
    with open(os.path.join(args.model_dir, 'model.pth'), 'wb') as f:
        torch.save(model.state_dict(), f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    # Hyperparameters from SageMaker
    parser.add_argument('--epochs', type=int, default=10)
    parser.add_argument('--batch-size', type=int, default=32)
    parser.add_argument('--learning-rate', type=float, default=1e-3)
    
    # SageMaker paths
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
    parser.add_argument('--model_dir', type=str, default=os.environ.get('SM_MODEL_DIR'))

    args = parser.parse_args()
    train(args)