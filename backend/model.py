import numpy as np
import xgboost as xgb
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score
import pickle, os, config

class Model:
    def __init__(self):
        self.xgb = None
        self.rf = None
        self.gb = None
        
    def train(self, X_train, y_train):
        print("\nTraining models...")
        self.xgb = xgb.XGBClassifier(n_estimators=200, max_depth=7, learning_rate=0.08,
                                      random_state=42, n_jobs=4, eval_metric='mlogloss')
        self.xgb.fit(X_train, y_train)
        print("  XGBoost done")
        
        self.rf = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, n_jobs=4)
        self.rf.fit(X_train, y_train)
        print("  Random Forest done")
        
        self.gb = GradientBoostingClassifier(n_estimators=150, max_depth=6, learning_rate=0.1, random_state=42)
        self.gb.fit(X_train, y_train)
        print("  Gradient Boosting done")
    
    def predict(self, X):
        xgb_probs = self.xgb.predict_proba(X)
        rf_probs = self.rf.predict_proba(X)
        gb_probs = self.gb.predict_proba(X)
        probs = xgb_probs * 0.4 + rf_probs * 0.35 + gb_probs * 0.25
        top_5 = np.argsort(probs, axis=1)[:, ::-1][:, :5]
        return top_5, probs
    
    def evaluate(self, X_test, y_test):
        print("\nEvaluating...")
        top_5, probs = self.predict(X_test)
        y_pred = top_5[:, 0]
        acc = accuracy_score(y_test, y_pred)
        top3 = np.mean([y_test[i] in top_5[i][:3] for i in range(len(y_test))])
        print(f"Top-1: {acc:.2%}")
        print(f"Top-3: {top3:.2%}")
        return {'accuracy': acc, 'top_3_accuracy': top3}
    
    def save(self):
        self.xgb.save_model(os.path.join(config.MODELS_DIR, "xgb.json"))
        with open(os.path.join(config.MODELS_DIR, "rf.pkl"), 'wb') as f: pickle.dump(self.rf, f)
        with open(os.path.join(config.MODELS_DIR, "gb.pkl"), 'wb') as f: pickle.dump(self.gb, f)
        print("Models saved")
    
    def load(self):
        try:
            self.xgb = xgb.XGBClassifier()
            self.xgb.load_model(os.path.join(config.MODELS_DIR, "xgb.json"))
            with open(os.path.join(config.MODELS_DIR, "rf.pkl"), 'rb') as f: self.rf = pickle.load(f)
            with open(os.path.join(config.MODELS_DIR, "gb.pkl"), 'rb') as f: self.gb = pickle.load(f)
            return True
        except: return False
