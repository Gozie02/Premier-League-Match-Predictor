import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import BaggingClassifier
from sklearn.metrics import accuracy_score
import joblib
from sklearn.impute import SimpleImputer 

# Load the updated Premier League data without Outcome_encoded
data = pd.read_csv('model_training.csv')
X = data.drop('Outcome_encoded_home', axis=1)
y = data['Outcome_encoded_home']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
imputer = SimpleImputer(strategy='mean') # Create an imputer instance
x_train = imputer.fit_transform(X_train) # Fit and transform on training data
x_test = imputer.transform(X_test)
bagging_classifier = BaggingClassifier(n_estimators=1000)
bagging_classifier.fit(x_train, y_train)

# Evaluate the model on the testing set
y_pred = bagging_classifier.predict(x_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model accuracy: {accuracy:.2f}")

# Save the retrained model
joblib.dump(bagging_classifier, 'finalized_model2.pkl')

print("Model retraining completed.")
