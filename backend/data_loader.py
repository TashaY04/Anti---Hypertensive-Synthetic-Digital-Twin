import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import config

def create_dataset():
    print("\nCreating dataset...")
    np.random.seed(42)
    data = []
    n = 1000
    
    for drug_id in range(config.NUM_DRUGS):
        for _ in range(n):
            base = {
                'age': np.random.randint(25, 80),
                'systolic': np.random.randint(130, 190),
                'diastolic': np.random.randint(80, 115),
                'weight': np.random.uniform(50, 100),
                'height': np.random.uniform(150, 190),
                'exercise': np.random.choice([0, 1, 2, 3]),
                'diet': np.random.choice([0, 1, 2]),
                'stress': np.random.choice([0, 1, 2]),
                'alcohol': np.random.choice([0, 1, 2]),
                'diabetes': 0, 'kidney': 0, 'pregnancy': 0, 'depression': 0, 'smoker': 0,
                'drug': drug_id
            }
            
            if drug_id == 0: base.update({'diabetes': 1, 'age': np.random.randint(40, 70), 'alcohol': 0})
            elif drug_id == 1: base.update({'age': np.random.randint(45, 75), 'stress': 2})
            elif drug_id == 2: base.update({'kidney': 1, 'age': np.random.randint(50, 85)})
            elif drug_id == 3: base.update({'age': np.random.randint(18, 45), 'exercise': 2})
            elif drug_id == 4: base.update({'depression': 1, 'stress': 2, 'alcohol': 2})
            elif drug_id == 5: base.update({'age': np.random.randint(55, 80)})
            else: base.update({'diabetes': 1, 'depression': 1})
            
            data.append(base)
    
    df = pd.DataFrame(data)
    df['bmi'] = df['weight'] / ((df['height']/100) ** 2)
    print(f"Created {len(df)} samples")
    return df

def load_and_split():
    df = create_dataset()
    features = ['age', 'systolic', 'diastolic', 'bmi', 'exercise', 'diet', 'stress',
                'diabetes', 'kidney', 'pregnancy', 'depression', 'smoker', 'alcohol']
    X = df[features].values
    y = df['drug'].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")
    return X_train, X_test, y_train, y_test, features
