import pyodbc
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
DATABASE_SERVER = os.getenv("AZURE_SQL_SERVER")
DATABASE_NAME = os.getenv("AZURE_SQL_DATABASE")
DATABASE_USER = os.getenv("AZURE_SQL_USER")
DATABASE_PASSWORD = os.getenv("AZURE_SQL_PASSWORD")
DRIVER = os.getenv("AZURE_SQL_DRIVER", "ODBC Driver 18 for SQL Server")

def get_db_connection() -> pyodbc.Connection:
    """
    Establishes a connection to the Azure SQL database using pyodbc.
    
    Returns:
        pyodbc.Connection: Database connection object.
    """
    try:
        connection_string = (
            f"DRIVER={{{DRIVER}}};"
            f"SERVER={DATABASE_SERVER};"
            f"DATABASE={DATABASE_NAME};"
            f"UID={DATABASE_USER};"
            f"PWD={DATABASE_PASSWORD};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
            f"Connection Timeout=30;"
        )
        connection = pyodbc.connect(connection_string)
        logger.info("Successfully connected to the database.")
        return connection
    except pyodbc.Error as e:
        logger.error(f"pyodbc error: {e}")
        raise RuntimeError(f"Error connecting to the database: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise RuntimeError(f"Error connecting to the database: {e}")

def save_id_data(first_name: str, last_name: str, cnp: str) -> None:
    """
    Saves the ID data into the database.

    Args:
        first_name (str): Extracted first name.
        last_name (str): Extracted last name.
        cnp (str): Extracted CNP.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL query to insert data using parameterized query
        query = """
        INSERT INTO id_data (first_name, last_name, cnp, created_at)
        VALUES (?, ?, ?, GETDATE());
        """
        cursor.execute(query, (first_name, last_name, cnp))
        conn.commit()
        logger.info(f"ID Data saved: {first_name} {last_name}, CNP: {cnp}")
    except pyodbc.Error as e:
        logger.error(f"pyodbc error while saving ID data: {e}")
        raise RuntimeError(f"Error saving ID data to the database: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while saving ID data: {e}")
        raise RuntimeError(f"Error saving ID data to the database: {e}")
    finally:
        conn.close()
        logger.info("Database connection closed.")

def save_processed_text(extracted_text: str, summary: str, first_name: str, last_name: str, cnp: str) -> None:
    """
    Saves the processed text data into the database.

    Args:
        extracted_text (str): Extracted handwritten text.
        summary (str): Generated summary.
        first_name (str): Extracted first name.
        last_name (str): Extracted last name.
        cnp (str): Extracted CNP.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL query to insert data using parameterized query
        query = """
        INSERT INTO processed_text (extracted_text, summary, first_name, last_name, cnp, created_at)
        VALUES (?, ?, ?, ?, ?, GETDATE());
        """
        cursor.execute(query, (extracted_text, summary, first_name, last_name, cnp))
        conn.commit()
        logger.info("Processed text data saved successfully.")
    except pyodbc.Error as e:
        logger.error(f"pyodbc error while saving processed text data: {e}")
        raise RuntimeError(f"Error saving processed text data to the database: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while saving processed text data: {e}")
        raise RuntimeError(f"Error saving processed text data to the database: {e}")
    finally:
        conn.close()
        logger.info("Database connection closed.")
