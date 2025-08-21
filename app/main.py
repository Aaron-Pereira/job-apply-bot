# app/main.py

from job_finder import find_jobs
from process_jobs import compute_similarity
from process_jobs import manual_rankings
from process_jobs import train_model
from process_jobs import predict_ranking

def main():
    # Find relevant jobs
    # find_jobs()
    # compute_similarity()
    # manual_rankings()
    train_model()
    predict_ranking()

if __name__ == "__main__":
    main()
