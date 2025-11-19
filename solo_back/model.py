import mysql.connector
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multioutput import MultiOutputClassifier
from sklearn.metrics import classification_report
import joblib

# Step 1: Connect to MySQL and fetch data
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin@123",   # Replace with your password
            database="solo",
            ssl_disabled=True
        )
        return conn
    except mysql.connector.Error as e:
        print("Error connecting to MySQL:", e)
        return None

conn = get_db_connection()

if conn:
    query = "SELECT name, description, tags FROM places WHERE tags IS NOT NULL"
    df = pd.read_sql(query, conn)
    conn.close()
else:
    print("Failed to connect to database.")
    exit()

print(f"Total records fetched: {len(df)}")
print(df.head())

# Step 2: Prepare the data
df['text'] = df['name'].fillna('') + " " + df['description'].fillna('')
df['tags_list'] = df['tags'].apply(lambda x: [tag.strip() for tag in x.split(',')])

mlb = MultiLabelBinarizer()
y = mlb.fit_transform(df['tags_list'])

X_train, X_test, y_train, y_test = train_test_split(df['text'], y, test_size=0.2, random_state=42)

print(f"Training samples: {len(X_train)}, Testing samples: {len(X_test)}")
print(f"Tags (classes): {mlb.classes_}")

# Step 3: Vectorize text and train model
tfidf = TfidfVectorizer(max_features=5000)
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

model = MultiOutputClassifier(LogisticRegression(max_iter=200))
model.fit(X_train_tfidf, y_train)

# Step 4: Evaluate
y_pred = model.predict(X_test_tfidf)
print("\nClassification Report (Test Set):")
print(classification_report(y_test, y_pred, target_names=mlb.classes_))

# Step 5: Save model and vectorizer
joblib.dump(model, 'tag_prediction_model.joblib')
joblib.dump(tfidf, 'tfidf_vectorizer.joblib')
joblib.dump(mlb, 'label_binarizer.joblib')

print("\nModel, vectorizer, and label binarizer saved successfully.")

# Optional: Function to predict tags for new place
def predict_tags(name, description):
    text = (name + " " + description).strip()
    text_tfidf = tfidf.transform([text])
    pred = model.predict(text_tfidf)
    tags = mlb.inverse_transform(pred)
    return list(tags[0]) if tags else []

# Example usage:
# new_place_tags = predict_tags("Sunset Beach", "Beautiful beach ideal for evening strolls.")
# print("Predicted tags:", new_place_tags)
