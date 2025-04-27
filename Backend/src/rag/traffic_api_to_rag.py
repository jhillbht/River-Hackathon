#!/usr/bin/env python3
"""
Traffic API to RAG PDF Converter

This script fetches data from traffic APIs, processes it, and converts it to PDFs
for ingestion into a RAG (Retrieval Augmented Generation) system.

Usage:
    python traffic_api_to_rag.py
"""

import requests
import json
import os
import pandas as pd
from datetime import datetime, timezone
from fpdf import FPDF
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
API_URL = "https://data.austintexas.gov/resource/dx9v-zd7x.json"
API_LIMIT = 50
PDF_OUTPUT_DIR = "traffic_pdfs"
RAG_INDEX_NAME = "traffic_incidents_index"

def fetch_traffic_data(limit=API_LIMIT):
    """
    Fetch traffic incident data from the Austin API
    
    Args:
        limit (int): Maximum number of records to fetch
        
    Returns:
        list: JSON response containing traffic incidents
    """
    logger.info(f"Fetching traffic data with limit {limit}")
    url = f"{API_URL}?$limit={limit}&$order=published_date DESC"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for bad status codes
        data = response.json()
        logger.info(f"Successfully fetched {len(data)} traffic incidents")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching traffic data: {e}")
        raise

def preprocess_traffic_data(data):
    """
    Clean and structure the raw traffic data
    
    Args:
        data (list): Raw traffic incident data
        
    Returns:
        pandas.DataFrame: Processed and structured data
    """
    logger.info("Preprocessing traffic data")
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Clean and normalize data
    df = df.fillna('N/A')
    
    # Convert date fields to datetime
    date_columns = ['published_date', 'status_date']
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    
    # Add derived fields - using timezone-aware datetime to avoid timezone errors
    if 'published_date' in df.columns:
        # Use a tz-aware datetime now to match the timezone from the API
        now = datetime.now(timezone.utc)
        try:
            # Calculate age in hours, handling timezone differences
            time_diff = now - df['published_date']
            df['incident_age_hours'] = time_diff.dt.total_seconds() / 3600
        except TypeError as e:
            # If timezone error occurs, skip the calculation
            logger.warning(f"Skipping incident age calculation due to: {e}")
            df['incident_age_hours'] = 'N/A'
    
    # Ensure critical fields exist
    essential_cols = ['traffic_report_id', 'issue_reported', 'address', 'status']
    for col in essential_cols:
        if col not in df.columns:
            df[col] = 'N/A'
    
    logger.info(f"Preprocessed {len(df)} traffic incidents")
    return df

def create_incident_pdfs(df, output_dir=PDF_OUTPUT_DIR):
    """
    Convert traffic incidents to PDF files
    
    Args:
        df (pandas.DataFrame): Processed traffic incident data
        output_dir (str): Directory to save PDF files
        
    Returns:
        list: Paths to created PDF files
    """
    logger.info(f"Creating incident PDFs in directory {output_dir}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Track created PDFs
    pdf_files = []
    
    # Create summary PDF with all incidents
    summary_pdf = FPDF()
    summary_pdf.add_page()
    summary_pdf.set_font("Arial", size=12)
    summary_pdf.cell(200, 10, txt="Traffic Incident Summary", ln=True, align='C')
    
    # Add current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    summary_pdf.cell(200, 10, txt=f"Generated: {timestamp}", ln=True, align='C')
    summary_pdf.cell(200, 10, txt="", ln=True)  # Empty line
    
    # Add each incident to summary and create individual PDFs
    for idx, incident in df.iterrows():
        incident_id = incident.get('traffic_report_id', f"unknown_{idx}")
        
        # Add to summary PDF
        summary_pdf.cell(200, 10, txt=f"Incident: {incident.get('issue_reported', 'N/A')}", ln=True)
        summary_pdf.cell(200, 10, txt=f"Location: {incident.get('address', 'N/A')}", ln=True)
        summary_pdf.cell(200, 10, txt=f"Status: {incident.get('status', 'N/A')}", ln=True)
        if 'published_date' in incident:
            summary_pdf.cell(200, 10, txt=f"Time: {incident['published_date']}", ln=True)
        summary_pdf.cell(200, 10, txt="-------------------------", ln=True)
        
        # Create individual PDF for each incident
        incident_pdf = FPDF()
        incident_pdf.add_page()
        incident_pdf.set_font("Arial", size=12)
        incident_pdf.cell(200, 10, txt=f"Traffic Incident: {incident_id}", ln=True, align='C')
        incident_pdf.cell(200, 10, txt=f"Generated: {timestamp}", ln=True, align='C')
        incident_pdf.cell(200, 10, txt="", ln=True)  # Empty line
        
        # Add all available incident data
        for key, value in incident.items():
            if key not in ['shape', 'location']:  # Skip geometry fields
                # Convert value to string to avoid FPDF errors with non-string types
                value_str = str(value)
                # Truncate long values to avoid PDF errors
                if len(value_str) > 200:
                    value_str = value_str[:197] + "..."
                incident_pdf.cell(200, 10, txt=f"{key.replace('_', ' ').title()}: {value_str}", ln=True)
        
        # Add coordinates if available
        if 'latitude' in incident and 'longitude' in incident:
            incident_pdf.cell(200, 10, txt=f"Coordinates: {incident.get('latitude', 'N/A')}, {incident.get('longitude', 'N/A')}", ln=True)
        
        # Save individual PDF
        individual_pdf_path = f"{output_dir}/incident_{incident_id}.pdf"
        incident_pdf.output(individual_pdf_path)
        pdf_files.append(individual_pdf_path)
        
    # Save summary PDF
    summary_pdf_path = f"{output_dir}/all_incidents_summary.pdf"
    summary_pdf.output(summary_pdf_path)
    pdf_files.append(summary_pdf_path)
    
    logger.info(f"Created {len(pdf_files)} PDF files")
    return pdf_files

def create_metadata_json(df, output_dir=PDF_OUTPUT_DIR):
    """
    Create a JSON file with metadata about all incidents
    
    Args:
        df (pandas.DataFrame): Processed traffic incident data
        output_dir (str): Directory to save JSON file
        
    Returns:
        str: Path to created JSON file
    """
    logger.info("Creating metadata JSON file")
    
    # Create metadata dictionary
    metadata = {
        "dataset_info": {
            "name": "Austin Traffic Incidents",
            "source": API_URL,
            "record_count": len(df),
            "generated_at": datetime.now().isoformat(),
            "incident_types": df['issue_reported'].unique().tolist() if 'issue_reported' in df.columns else []
        },
        "incidents": df.to_dict(orient='records')
    }
    
    # Save metadata to JSON file
    json_path = f"{output_dir}/traffic_incidents_metadata.json"
    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    logger.info(f"Created metadata JSON at {json_path}")
    return json_path

def main():
    """Main function to execute the full pipeline"""
    logger.info("Starting Traffic API to RAG PDF Converter")
    
    try:
        # Step 1: Fetch traffic data
        traffic_data = fetch_traffic_data()
        
        # Step 2: Preprocess the data
        processed_data = preprocess_traffic_data(traffic_data)
        
        # Step 3: Convert to PDFs
        pdf_files = create_incident_pdfs(processed_data)
        
        # Step 4: Create metadata JSON
        metadata_file = create_metadata_json(processed_data)
        
        logger.info("Pipeline completed successfully")
        logger.info(f"Generated PDFs and metadata in {PDF_OUTPUT_DIR}")
        logger.info("The PDFs are now ready for ingestion into your RAG system")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()
