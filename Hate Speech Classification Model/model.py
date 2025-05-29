import re
import nltk
import pandas as pd
import numpy as np

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression  
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.feature_selection import SelectKBest, chi2

# Load dataset (Modify 'your_dataset.csv' to your actual file)
df = pd.read_csv("Dynamically Generated Hate Dataset v0.2.3.csv")  # Ensure it has 'text' and 'label' columns


df = df.head(3000)
df = df.drop(df.columns[0], axis=1)
df = df.drop(columns=['acl.id', 'X1', 'level', 'split', 'round.base', 'annotator', 'round', 'acl.id.matched'])

print(df)

print(type(df))
print(hasattr(df, 'index'))
print(df.index)

# Function to clean text
def clean_text(text):
    if isinstance(text, str):
        removed_spec_char = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
        tokenized = word_tokenize(removed_spec_char)  # Tokenize words
        stop_words = set(stopwords.words('english'))  
        filtered = [word for word in tokenized if word.lower() not in stop_words]  # Remove stopwords
        return ' '.join(filtered)  # Join back into a string
    return ""

# Apply text cleaning
df['cleaned_text'] = df['text'].apply(clean_text)

# Extract features and labels
texts = df['cleaned_text'].tolist()
labels = df['label'].tolist()

# Convert text to numerical features using TfidfVectorizer
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)
y = np.array(labels)

# Split into training (80%) and testing (20%) sets
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#Apply Feature Selection
selector = SelectKBest(chi2, k=1500)
X = selector.fit_transform(X, y)

indices = np.arange(len(df))
# Split while keeping index tracking
X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
    X, y, indices, test_size=0.2, random_state=42
)

# Train Logistic Regression model
model = LogisticRegression(class_weight='balanced', penalty='l2', C=50, solver='liblinear',random_state=42)
model.fit(X_train, y_train)

# Predict on test data
y_pred = model.predict(X_test)

# Print predictions for all test samples
for i, (text, actual, predicted) in enumerate(zip(idx_test, y_test, y_pred)):
    original_text = df.loc[text, 'text']
    print(f"Text: {original_text}")
    #print(predicted)
    print(f"Predicted Label: {predicted} ({'Toxic' if predicted == 'hate' else 'Non-toxic'})")
    #print(actual)
    print(f"Actual Label: {actual} ({'Toxic' if actual == 'hate' else 'Non-toxic'})\n")

# Print classification report
print("Classification Report:")
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))

# Print model accuracy
accuracy = accuracy_score(y_test, y_pred)*100
print(f"Model accuracy: {accuracy:.2f}%")