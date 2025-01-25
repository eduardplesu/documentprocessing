import streamlit as st
from dotenv import load_dotenv
from app.azure_services import process_id_document, process_handwritten_document
from app.database import save_id_data, save_processed_text
from app.utils import validate_and_prepare_file, validate_cnp, show_validation_error, display_data_preview

# Ensure Streamlit configuration is set first
st.set_page_config(
    page_title="ROPS Document Processor",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Load environment variables
load_dotenv()

# Title and description
st.title("📝 ROPSDocProcess")
st.write("A demo application to process ID cards and handwritten documents using Azure AI services.")

# Step 1: File Upload for ID Card
st.header("Step 1: Upload an ID Card")
uploaded_id_file = st.file_uploader("Upload a scanned ID card (PDF/Image)", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_id_file:
    try:
        # Preprocess the uploaded file
        doc_bytes = validate_and_prepare_file(uploaded_id_file)

        # Extract ID document data
        extracted_id_data = process_id_document(doc_bytes)

        if "error" in extracted_id_data:
            st.error(f"Error processing ID document: {extracted_id_data['error']}")
        else:
            st.success("ID Data extracted successfully!")
            display_data_preview(extracted_id_data)

            # Extract fields
            first_name = extracted_id_data.get("first_name", "").strip()
            last_name = extracted_id_data.get("last_name", "").strip()
            cnp = extracted_id_data.get("cnp", "").strip()

            st.write(f"**Extracted CNP:** {cnp}")  # Debugging line

            # Validate CNP
            if not cnp:
                st.error("Personal number (CNP) not found in the ID document.")
            elif not validate_cnp(cnp):
                show_validation_error("Invalid CNP format. Please verify the ID card.")
            else:
                st.info(f"Validated CNP: {cnp}")

                # Add a button to save the data to the database
                if st.button("Save ID Data to Database"):
                    try:
                        save_id_data(first_name, last_name, cnp)
                        st.success(f"ID Data saved to database with CNP: {cnp}")
                    except Exception as e:
                        st.error(f"Error saving ID data: {str(e)}")

    except Exception as e:
        st.error(f"Error processing the ID card: {str(e)}")

# Step 2: File Upload for Handwritten Document
st.header("Step 2: Upload a Handwritten Document")
uploaded_text_file = st.file_uploader("Upload a handwritten document (PDF/Image)", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_text_file:
    try:
        # Preprocess the uploaded file
        doc_bytes = validate_and_prepare_file(uploaded_text_file)

        # Extract handwritten text data
        processed_text_data = process_handwritten_document(doc_bytes)

        if "error" in processed_text_data:
            st.error(f"Error processing handwritten document: {processed_text_data['error']}")
        else:
            st.success("Handwritten text processed successfully!")
            st.write(f"**Extracted Text:** {processed_text_data.get('extracted_text', '')}")  # Debugging line
            st.write(f"**Summary:** {processed_text_data.get('summary', '')}")  # Debugging line
            st.write(f"**First Name:** {processed_text_data.get('first_name', '')}")  # Debugging line
            st.write(f"**Last Name:** {processed_text_data.get('last_name', '')}")  # Debugging line
            st.write(f"**CNP:** {processed_text_data.get('cnp', '')}")  # Debugging line

            # Extract data to save
            extracted_text = processed_text_data.get("extracted_text", "").strip()
            summary = processed_text_data.get("summary", "").strip()
            first_name = processed_text_data.get("first_name", "").strip()
            last_name = processed_text_data.get("last_name", "").strip()
            cnp = processed_text_data.get("cnp", "").strip()

            # Validate CNP if present
            if cnp and not validate_cnp(cnp):
                show_validation_error("Invalid CNP format extracted from handwritten text.")
            else:
                # Add a button to save the processed text to the database
                if st.button("Save Handwritten Data to Database"):
                    try:
                        save_processed_text(extracted_text, summary, first_name, last_name, cnp)
                        st.success("Handwritten data saved to database successfully!")
                    except Exception as e:
                        st.error(f"Error saving handwritten data: {str(e)}")

    except Exception as e:
        st.error(f"Error processing the handwritten document: {str(e)}")
