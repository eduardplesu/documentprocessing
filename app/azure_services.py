import json
import os
import openai
import logging
import re
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Azure Form Recognizer credentials
FORM_RECOGNIZER_ENDPOINT = os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT")
FORM_RECOGNIZER_KEY = os.getenv("AZURE_FORM_RECOGNIZER_KEY")

# OpenAI credentials
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")  # Deployment name

# OpenAI Initialization
openai.api_type = "azure"
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = "2024-05-01-preview"  # Ensure this matches your Azure OpenAI service version
openai.api_key = AZURE_OPENAI_KEY

# Configure logging
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for detailed logs
logger = logging.getLogger(__name__)

def remove_code_blocks(text):
    """
    Removes code blocks from the given text using regular expressions.
    
    Args:
        text (str): The text potentially containing code blocks.
    
    Returns:
        str: The text with code blocks removed.
    """
    # Pattern to match ```json\n{...}\n```
    pattern = r"```json\s*\n([\s\S]*?)\n```"
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    
    # Pattern to match any ```\n{...}\n```
    pattern = r"```\s*\n([\s\S]*?)\n```"
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    
    return text.strip()

def get_field_value(field):
    """
    Safely retrieves the value from a FieldValue object or a dict.

    Args:
        field: The field object or dictionary to extract the value from.

    Returns:
        str: The extracted and stripped value, or an empty string if not available.
    """
    if field:
        if isinstance(field, dict):
            # If the field is a dict, attempt to get 'value'
            return field.get("value", "").strip() if field.get("value") else ""
        else:
            # Assume the field has a 'value' attribute
            return field.value.strip() if hasattr(field, 'value') and field.value else ""
    return ""

def process_id_document(document_bytes: bytes):
    """
    Processes an ID card using Azure Form Recognizer's prebuilt ID model.

    Args:
        document_bytes (bytes): The uploaded ID document in binary format.

    Returns:
        dict: Extracted data, including fields and confidence scores.
    """
    try:
        # Initialize the Document Analysis Client
        client = DocumentAnalysisClient(
            endpoint=FORM_RECOGNIZER_ENDPOINT,
            credential=AzureKeyCredential(FORM_RECOGNIZER_KEY)
        )

        poller = client.begin_analyze_document(
            model_id="prebuilt-idDocument",
            document=document_bytes
        )
        result = poller.result()

        # Extract relevant fields
        extracted_data = {}
        for document in result.documents:
            logger.debug(f"Processing document: {document}")
            logger.debug(f"Document fields: {document.fields}")

            # Safely extract and strip values
            extracted_data['first_name'] = get_field_value(document.fields.get("FirstName"))
            extracted_data['last_name'] = get_field_value(document.fields.get("LastName"))
            # Extract only digits for CNP
            cnp_raw = get_field_value(document.fields.get("PersonalNumber"))
            extracted_data['cnp'] = ''.join(filter(str.isdigit, cnp_raw))
            # Optionally, add other fields as needed

        return extracted_data

    except Exception as e:
        logger.error(f"Error in process_id_document: {e}")
        return {"error": str(e)}

def process_handwritten_document(document_bytes: bytes):
    """
    Processes a handwritten document using Azure Form Recognizer's OCR model
    and Azure OpenAI for text cleaning and summary extraction.

    Args:
        document_bytes (bytes): The uploaded handwritten document in binary format.

    Returns:
        dict: Processed data, including summary and extracted fields.
    """
    try:
        client = DocumentAnalysisClient(
            endpoint=FORM_RECOGNIZER_ENDPOINT,
            credential=AzureKeyCredential(FORM_RECOGNIZER_KEY)
        )

        poller = client.begin_analyze_document(
            model_id="prebuilt-read",
            document=document_bytes
        )
        result = poller.result()

        # Extract text
        ocr_text = "\n".join([line.content for page in result.pages for line in page.lines])
        logger.debug(f"OCR Extracted Text: {ocr_text}")

        # Clean the text with OpenAI Chat Completion
        cleaned_text = clean_text_with_openai(ocr_text)
        # Extract summary and metadata with OpenAI Chat Completion
        summary, first_name, last_name, cnp = extract_fields_with_openai(cleaned_text)

        return {
            "extracted_text": cleaned_text,
            "summary": summary,
            "first_name": first_name,
            "last_name": last_name,
            "cnp": cnp
        }

    except Exception as e:
        logger.error(f"Error in process_handwritten_document: {e}")
        return {"error": str(e)}

def clean_text_with_openai(text: str) -> str:
    """
    Cleans OCR-extracted text using Azure OpenAI's Chat Completion.

    Args:
        text (str): The raw OCR text to be cleaned.

    Returns:
        str: The cleaned text.
    """
    try:
        prompt = [
            {"role": "system", "content": "You are an AI assistant that helps people clean and format text."},
            {"role": "user", "content": (
                "Please clean the following OCR-extracted text by removing any extraneous characters, "
                "correcting grammatical errors, and ensuring proper punctuation while maintaining the original context and meaning.\n\n"
                f"Text:\n{text}"
            )}
        ]

        response = openai.ChatCompletion.create(
            deployment_id=AZURE_OPENAI_DEPLOYMENT,  # Use the deployment name from the environment variable
            messages=prompt,
            max_tokens=800,
            temperature=0.5,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False
        )

        # Log the raw response for debugging
        logger.debug(f"OpenAI ChatCompletion Response for Cleaning: {response}")

        # Extract cleaned text
        cleaned = response.choices[0].message['content'].strip()
        logger.debug(f"Cleaned Text: {cleaned}")

        # Remove any code block syntax if present
        cleaned = remove_code_blocks(cleaned)
        logger.debug(f"Cleaned Text after removing code blocks: {cleaned}")

        return cleaned
    except Exception as e:
        logger.error(f"Error cleaning text with OpenAI: {e}")
        raise RuntimeError(f"Error cleaning text with OpenAI: {str(e)}")

def extract_fields_with_openai(cleaned_text: str) -> tuple:
    """
    Extracts summary, first name, last name, and CNP from cleaned text using Azure OpenAI's Chat Completion.

    Args:
        cleaned_text (str): The cleaned text to analyze.

    Returns:
        tuple: summary (str), first_name (str), last_name (str), cnp (str)
    """
    try:
        # Define a prompt that instructs OpenAI to return JSON without code blocks
        prompt = [
            {"role": "system", "content": "You are an AI assistant that extracts specific information from text."},
            {"role": "user", "content": (
                "From the following text, extract the summary in Romanian Language only, first name, last name, and CNP. "
                "Return the results strictly in JSON format with the keys 'summary', 'first_name', 'last_name', and 'cnp'. "
                "Do not include any additional text, explanations, or formatting. Do not use code blocks.\n\n"
                f"Text:\n{cleaned_text}"
            )}
        ]

        response = openai.ChatCompletion.create(
            deployment_id=AZURE_OPENAI_DEPLOYMENT,  # Use the deployment name from the environment variable
            messages=prompt,
            max_tokens=800,
            temperature=0.5,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False
        )

        # Log the raw response for debugging
        logger.debug(f"OpenAI ChatCompletion Response for Extraction: {response}")

        # Extract the content
        content = response.choices[0].message['content'].strip()
        logger.debug(f"Extracted Content: {content}")

        # Remove code blocks
        content = remove_code_blocks(content)
        logger.debug(f"Content after removing code blocks: {content}")

        # Validate JSON format
        if not (content.startswith("{") and content.endswith("}")):
            logger.error("OpenAI response is not in JSON format.")
            logger.debug(f"Response Content: {content}")
            raise RuntimeError("OpenAI response is not valid JSON.")

        # Parse JSON
        metadata = json.loads(content)

        # Extract fields with defaults
        summary = metadata.get("summary", "").strip()
        first_name = metadata.get("first_name", "").strip()
        last_name = metadata.get("last_name", "").strip()
        cnp = metadata.get("cnp", "").strip()

        return summary, first_name, last_name, cnp

    except json.JSONDecodeError as jde:
        logger.error(f"Error parsing JSON from OpenAI response: {jde}")
        logger.debug(f"Response Content: {content}")  # Log the problematic content
        raise RuntimeError(f"Error parsing JSON from OpenAI response: {str(jde)}")
    except Exception as e:
        logger.error(f"Error extracting fields with OpenAI: {e}")
        raise RuntimeError(f"Error extracting fields with OpenAI: {str(e)}")
