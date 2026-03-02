from data_loader import load_and_split
from model import Model

def train():
    print("="*60)
    print("TRAINING MODEL")
    print("="*60)
    X_train, X_test, y_train, y_test, features = load_and_split()
    model = Model()
    model.train(X_train, y_train)
    metrics = model.evaluate(X_test, y_test)
    model.save()
    print("\nCOMPLETE!")
    return metrics

if __name__ == "__main__":
    train()
