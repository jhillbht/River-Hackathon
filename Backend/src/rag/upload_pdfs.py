import os
import requests
import glob

def upload_pdf(file_path):
    url = 'http://localhost:5001/upload_and_index_pdf'
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
        response = requests.post(url, files=files)
        print(f"Uploading {os.path.basename(file_path)}: {response.status_code}")
        if response.status_code != 200:
            print(f"Error: {response.json()}")

def main():
    pdf_dir = 'traffic_pdfs'
    pdf_files = glob.glob(os.path.join(pdf_dir, '*.pdf'))
    
    print(f"Found {len(pdf_files)} PDF files to upload")
    for pdf_file in pdf_files:
        upload_pdf(pdf_file)
    
    print("Upload complete!")

if __name__ == '__main__':
    main() 