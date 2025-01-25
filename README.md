# Document Processing Application

This is a document processing application using **Streamlit**, **Azure AI services**, and **Docker**. The application allows users to upload ID cards and handwritten documents for processing.

## Features
- Extracts data from ID cards using Azure Form Recognizer.
- Processes handwritten documents with Azure Form Recognizer OCR.
- Utilizes Azure OpenAI for text cleaning and metadata extraction.
- Fully containerized and deployable to Azure Web Apps.

## Technologies Used
- Python
- Streamlit
- Azure AI Form Recognizer
- Azure OpenAI
- Docker
- Azure App Service
- Azure SQL Server

## Project Structure
ropsdocprocess/ ├── app/ │ ├── init.py │ ├── azure_services.py │ ├── database.py │ ├── utils.py ├── .env ├── Dockerfile ├── requirements.txt ├── main.py ├── README.md └── .gitignore

bash
Copy
Edit

## How to Run Locally
1. Clone the repository:
   ```bash
   git clone https://github.com/eduardplesu/documentprocessing.git
   cd documentprocessing
Install dependencies:
bash
Copy
Edit
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
Run the application:
bash
Copy
Edit
streamlit run main.py
Deploying to Azure
Follow the deployment steps outlined in the Azure deployment guide.