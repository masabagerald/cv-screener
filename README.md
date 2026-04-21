#                                                            
  
  
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
                      
   AI-Powered CV Screener

## Overview
AI-Powered CV Screener is a recruitment automation tool that evaluates candidate CVs against job descriptions using OpenAI’s Agents SDK. It enforces **strict, evidence-based screening** to ensure objective, consistent, and high-quality hiring decisions.

Built with FastAPI, the system enables recruiters to efficiently parse, score, and shortlist candidates with minimal manual effort.

---

## Key Features
- **Automated CV Evaluation**
  - Extracts and analyzes CV and cover letter content
  - Matches candidates against job requirements

- **Strict AI Scoring Engine**
  - No assumptions — only proven evidence is considered
  - Scores:
    - Skills match
    - Experience relevance
    - Education fit
    - Communication clarity
    - Cover letter quality

- **Requirement Validation**
  - Each requirement marked as:
    - Met / Partially Met / Not Met
  - Missing evidence is flagged

- **Decision Support**
  - Outputs:
    - Shortlist
    - Consider
    - Reject

- **FastAPI Backend**
  - Lightweight and scalable
  - Easy API integration

---

## Tech Stack
- **Backend:** FastAPI  
- **AI Engine:** OpenAI Agents SDK  
- **Language:** Python  
- **ORM/Database:** SQLAlchemy  
- **Frontend (Optional):** HTML, CSS, JavaScript  

---

## Installation

### Prerequisites
- Python 3.9 or higher  
- pip  
- Virtual environment tool (venv recommended)  

### Setup Steps
1. Clone the repository and navigate into the project directory  
2. Create and activate a virtual environment  
3. Install dependencies from `requirements.txt`  
4. Create a `.env` file in the project root  

### Environment Variables
Add the following to your `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here

cv-screener/
│── app.py
│── requirements.txt
│── agents/
│── services/
│── models/
│── utils/
│── templates/
│── static/

