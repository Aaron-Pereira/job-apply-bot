import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import MinMaxScaler
from scipy.sparse import hstack
import joblib


# Compute similarity between jobs and resume 
def compute_similarity():
    df = pd.read_csv("jobs.csv")
    print(df.head())

    # Temporarily store resume as text 
    resume_text = """
    Software Developer with experience in .NET, Blazor, SQL, and financial systems.
    Strong background in AI projects such as spam detection and job scraping bots.
    Skilled in Python, machine learning, and data analysis.
    """

    # Vectorise resume and jobs
    df["job_text"] = df["Title"] + " " +df["Description"]
    vectoriser = TfidfVectorizer(stop_words="english")
    job_vectors = vectoriser.fit_transform(df["job_text"])
    resume_vector = vectoriser.transform([resume_text])

    # Compare resume to job vector
    similarities = cosine_similarity(resume_vector, job_vectors).flatten()

    # Add similarity score into the dataframe
    df["Relevance Score"] = similarities

    # Normalise scores 1-10
    df["Rank"] = pd.qcut(df["Relevance Score"], 10, labels=False) + 1
    df = df.sort_values("Rank", ascending=False)

    print(df[["Company", "Title", "Relevance Score", "Rank"]].head(10))

def manual_rankings():
    df = pd.read_csv("jobs.csv")

    if "Manual Rank" not in df.columns:
        df["Manual Rank"] = None

    for i, row in df.iterrows():
        if pd.isna(row["Manual Rank"]):
            print("\n--- Job ---")
            print(f"Company: {row['Company']}")
            print(f"Title: {row['Title']}")
            print(f"Description: {row['Description'][:300]}...")

            while True:
                try:
                    rank = int(input("Rank this job 1-10: "))
                    if 1 <= rank <= 10:
                        df.at[i, "Manual Rank"] = rank
                        break
                    else:
                        print("Invalid rank. Please enter a number between 1 and 10.")
                except ValueError:
                    print("Invalid input. Please enter a number.")

    df.to_csv("jobs.csv", index=False)
    print("Updated jobs with manual rankings")


# ------------------- TRAIN MODEL -------------------
def train_model():
    # Load dataset
    df = pd.read_csv("jobs_train.csv")
    job_text = df["Title"] + " " +df["Description"]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=50)
    X_vec = vectorizer.fit_transform(job_text)

    # Vectorize your resume
    resume_text = """
    Software Developer with experience in .NET, Blazor, SQL, and financial systems.
    Strong background in AI projects such as spam detection and job scraping bots.
    Skilled in Python, machine learning, and data analysis.
    """
    # resume_text = """
    # Truck Driver"""

    resume_vec = vectorizer.transform([resume_text])

    # Compute similarity for each job compared to resume
    similarities = cosine_similarity(resume_vec, X_vec).flatten()

    # Normalize similarity scores and increase weighting
    scalar = MinMaxScaler()
    similarities_scaled = scalar.fit_transform(similarities.reshape(-1, 1)) * 50 # weight added

    # Final feature set
    X_final = hstack([X_vec, similarities_scaled])
    y = df["Manual Rank"]

    # Split into training and testing
    X_train, X_test, y_train, y_test = train_test_split(X_final, y, test_size=0.2, random_state=42)

    # Train model
    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_test)      
    print("MSE:", mean_squared_error(y_test, y_pred))
    print("R2:", r2_score(y_test, y_pred))

    # Save model and vectorizer
    joblib.dump(model, "job_rank_model.pkl")
    joblib.dump(vectorizer, "vectorizer.pkl")
    joblib.dump(scalar, "similarity_scaler.pkl")

# ------------------- PREDICT JOB RANKINGS -------------------
def predict_ranking():
    # Load model and vectorizer
    model = joblib.load("job_rank_model.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
    scaler = joblib.load("similarity_scaler.pkl")

    df = pd.read_csv("jobs_test.csv")
    job_text = df["Title"] + " " +df["Description"]
    X_vec = vectorizer.transform(job_text)

    resume_text = """
    Software Developer with experience in .NET, Blazor, SQL, and financial systems.
    Strong background in AI projects such as spam detection and job scraping bots.
    Skilled in Python, machine learning, and data analysis.
    """

    resume_vec = vectorizer.transform([resume_text])
    similarities = cosine_similarity(resume_vec, X_vec).flatten()
    similarities_scaled = scaler.transform(similarities.reshape(-1, 1)) * 50 # weight

    predicted_ranks = []
    # If similarity to resume is > 0.5, keeps job
    for i, sim in enumerate(similarities):
        if sim < 0.5:
            # Too dissimilar, rank = 0
            predicted_ranks.append(0)
        else:
            # Combine TF-IDF job features with similarity
            X_final = hstack([X_vec[i], similarities_scaled[i].reshape(1, -1)])
            rank = model.predict(X_final)[0]
            predicted_ranks.append(round(rank.clip(1,10)))

    # predicted_ranks = model.predict(X_final)
    # predicted_ranks = predicted_ranks.round().clip(1, 10)

    predicted_jobs = df.copy()
    predicted_jobs["Predicted Rank"] = predicted_ranks

    # Print each job with predicted rank
    for i, row in predicted_jobs.iterrows():
        print(f"{row['Predicted Rank']} - {row['Title']} at {row.get('Company','Unknown Company')}")








