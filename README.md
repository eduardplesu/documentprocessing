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

Steps to Update Environment Variables
Create a .env file in the project root directory.

Add the environment variables in the following format:

plaintext
Copy
Edit
AZURE_FORM_RECOGNIZER_ENDPOINT=https://<your-formrecognizer>.cognitiveservices.azure.com/
AZURE_FORM_RECOGNIZER_KEY=YOUR_KEY
AZURE_OPENAI_ENDPOINT=https://<your-openai>.openai.azure.com/
AZURE_OPENAI_KEY=YOUR_KEY
AZURE_OPENAI_DEPLOYMENT=<openai-model-name>
AZURE_SQL_SERVER=<your-server-name>.database.windows.net
AZURE_SQL_DATABASE=<your-database-name>
AZURE_SQL_USER=YOUR_USERNAME
AZURE_SQL_PASSWORD=YOUR_PASSWORD
AZURE_SQL_DRIVER=ODBC Driver 18 for SQL Server
STREAMLIT_SERVER_PORT=8501
DEBUG=False
Save the .env file.

Ensure the environment variables are set during deployment:

For local development, python-dotenv will automatically load these values.
For Azure deployment, set these as application settings under the App Service.


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