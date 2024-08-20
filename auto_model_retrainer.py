import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import BaggingClassifier
from sklearn.metrics import accuracy_score
import joblib

# Load the updated Premier League data without Outcome_encoded
data = pd.read_csv('model_training.csv')
X = data.drop('Outcome_encoded', axis=1)
y = data['Outcome_encoded']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
bagging_classifier = BaggingClassifier(n_estimators=1000)
bagging_classifier.fit(X_train, y_train)

# Evaluate the model on the testing set
y_pred = bagging_classifier.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {accuracy:.2f}")

# Save the retrained model
joblib.dump(bagging_classifier, 'finalized_model2.pkl')

print("Model retraining completed.")
