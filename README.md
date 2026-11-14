# MediNova AI 3.0

**Developed by Mokshith Reddy**  
Android-friendly web app built with Python and Streamlit.

## Included
- Overview dashboard
- Timestamped synthetic real-time demo dashboard
- Optional AI science education assistant
- Medicine information framework
- Diagnostics and lab-test learning
- Biotechnology knowledge hub
- Local study notebook

## Run locally
1. Install Python 3.10 or newer.
2. Extract this ZIP and open a terminal in this folder.
3. Run `pip install -r requirements.txt`.
4. Run `streamlit run app.py`.
5. Open the URL shown in the terminal. On Android, open the deployed HTTPS URL in Chrome.

## Optional AI setup
Set `OPENAI_API_KEY` as a private environment variable, or add it in Streamlit Community Cloud:
App → Settings → Secrets:
```toml
OPENAI_API_KEY = "your-key"
OPENAI_MODEL = "gpt-5.5"
```
Never commit secrets to GitHub. AI is optional; the rest of the app works without it.

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository named `MediNova-AI`.
2. Upload the contents of this folder to the repository root (so `app.py` is at the root).
3. In Streamlit Community Cloud, choose **New app**.
4. Select the repository, branch, and `app.py` as the main file.
5. Deploy. Add the AI key through Streamlit **Secrets**, not GitHub.
6. Open the public HTTPS URL on Android.

## Important data limitation
The demo dashboard creates synthetic sample events only. SQLite storage on Streamlit Community Cloud may be temporary and is not a production database. Do not store patient information. Before using persistent or real data, migrate to a managed database with encryption, authentication, authorization, backups, audit logging and a privacy review.

## Healthcare safety
This is an educational software prototype, not a medical device. It does not diagnose, triage, interpret personal test results, prescribe, or recommend doses. Do not enter personal health information. Any real-world clinical use requires qualified professional review, validation, security/privacy assessment and applicable regulatory advice in India.
