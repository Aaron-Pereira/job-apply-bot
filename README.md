# 📌 Job Finder & Ranking Bot

This project automates the process of:
1. **Scraping job postings** from [Seek](https://www.seek.com.au).
2. **Reading Gmail verification codes** automatically to handle login.
3. **Extracting job descriptions, titles, and companies** into structured CSV files.
4. **Computing similarity scores** between your resume and job descriptions.
5. **Training a machine learning model** to predict job relevance rankings.
6. **Predicting and ranking jobs** (1–10 scale) based on how well they match your resume.

---

## 🚀 Features
- 🔑 **Automated Gmail login verification** using the Gmail API (reads 6-digit codes from your inbox).
- 🌐 **Web scraping** with Selenium + BeautifulSoup to collect job postings.
- 📊 **TF-IDF similarity scoring** to measure how closely a job matches your resume.
- 🤖 **Machine learning (Random Forest)** model to learn from manually ranked jobs.
- 🏆 **Prediction pipeline**: Filters out irrelevant jobs (<0.5 similarity) and ranks relevant ones from 1–10.

---
