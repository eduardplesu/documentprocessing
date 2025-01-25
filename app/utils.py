import streamlit as st
import re
from PIL import Image
import io

def validate_cnp(cnp: str) -> bool:
    """
    Validates the format of a Romanian CNP (Personal Numeric Code).

    Args:
        cnp (str): The CNP string to validate.

    Returns:
        bool: True if the CNP is valid, False otherwise.
    """
    if not cnp or not re.match(r"^[1-8]\d{12}$", cnp):
        return False

    # CNP control digit validation
    control_weights = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    try:
        cnp_digits = [int(d) for d in cnp]
    except ValueError:
        # CNP contains non-digit characters
        return False

    control_sum = sum(cnp_digits[i] * control_weights[i] for i in range(12))
    control_digit = control_sum % 11
    if control_digit == 10:
        control_digit = 1

    return cnp_digits[-1] == control_digit

def show_validation_error(message: str) -> None:
    """
    Displays a validation error message in the Streamlit app.

    Args:
        message (str): The error message to display.
    """
    st.error(f"❌ {message}")

def display_data_preview(data: dict) -> None:
    """
    Displays a preview of extracted data in the Streamlit app.

    Args:
        data (dict): The data to preview, typically extracted from Azure services.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict) and "value" in value and "confidence" in value:
                st.write(f"**{key}:** {value['value']} (Confidence: {value['confidence']:.2f})")
            else:
                st.write(f"**{key}:** {value}")
    else:
        st.write("No data to display")

def validate_and_prepare_file(file) -> bytes:
    """
    Validates and prepares an uploaded file for Azure Document Intelligence.

    Args:
        file: Uploaded file object.

    Returns:
        bytes: The file content in bytes.

    Raises:
        RuntimeError: If the file is invalid or cannot be processed.
    """
    try:
        if file.name.lower().endswith(".pdf"):
            # Read PDF bytes directly
            file_bytes = file.read()
            return file_bytes
        else:
            # Load the file as an image
            image = Image.open(file)

            # Validate supported image format
            if image.format not in ["JPEG", "PNG"]:
                raise ValueError("Unsupported image format. Please upload a JPEG, PNG, or PDF file.")

            # Resize image to acceptable resolution
            max_resolution = (2000, 2000)
            image.thumbnail(max_resolution)

            # Save the processed image to a byte stream
            byte_stream = io.BytesIO()
            image.save(byte_stream, format=image.format)
            byte_stream.seek(0)
            return byte_stream.read()

    except Exception as e:
        raise RuntimeError(f"Error validating or preparing file: {str(e)}")
