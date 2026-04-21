# CV Screener

This project is a CV Screener application that leverages a FastAPI backend with an HTML frontend.

## Installation Instructions

### Prerequisites
- Python 3.8+
- pip

### Setup Virtual Environment
1. Clone the repository:
   ```bash
   git clone https://github.com/masabagerald/cv-screener.git
   cd cv-screener
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - For Windows:
     ```bash
     venv\Scripts\activate
     ```
   - For macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

### Install Dependencies
Run the following command to install the required packages:
```bash
pip install -r requirements.txt
```

### Running the Application
1. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

2. Open your browser and go to `http://127.0.0.1:8000` to view the application.

## Usage Instructions
- Follow the prompts on the HTML frontend to upload and process CVs.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.