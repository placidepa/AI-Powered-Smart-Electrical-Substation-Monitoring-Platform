from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

class FaultClassifier:
    '''
    Supervised model to classify specific substation fault types.
    Labels: 0 (Normal), 1 (Overload), 2 (Short Circuit), 3 (Cooling Failure)
    '''
    def __init__(self, use_xgb=True):
        if use_xgb:
            self.model = XGBClassifier(
                n_estimators=150, max_depth=5, learning_rate=0.1, eval_metric='mlogloss'
            )
        else:
            self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)

    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self, X):
        return self.model.predict(X)
        
    def evaluate(self, X_test, y_test):
        preds = self.predict(X_test)
        return classification_report(y_test, preds)