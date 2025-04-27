import os
from flask import Flask, request, jsonify
import fitz  # PyMuPDF
# Assuming 'webai' library is installed and available
# from webai import update_index # Uncomment this line when the actual webai library is available

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp/pdf_uploads' # Use a temporary directory inside the container
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Get the WebAI index path from environment variables
WEB_AI_INDEX_PATH = os.environ.get('WEB_AI_INDEX_PATH')

if not WEB_AI_INDEX_PATH:
    print("Error: WEB_AI_INDEX_PATH environment variable not set.")
    # In a real application, you might want to exit or handle this more gracefully
    # For this example, we'll just print an error and continue, but update_index calls will fail.

@app.route('/upload_and_index_pdf', methods=['POST'])
def upload_and_index_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and file.filename.lower().endswith('.pdf'):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        try:
            file.save(filepath)

            # Extract text using PyMuPDF
            doc = fitz.open(filepath)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            doc.close()

            # --- WebAI Indexing Step ---
            if WEB_AI_INDEX_PATH:
                print(f"Updating WebAI index at {WEB_AI_INDEX_PATH} with extracted text...")
                # try:
                    # Call the actual WebAI update function
                    # update_index(index_path=WEB_AI_INDEX_PATH, new_data=full_text)
                    # print("WebAI index update called successfully (assuming function exists).")
                # except Exception as webai_e:
                    # print(f"Error calling WebAI update_index: {webai_e}")
                    # return jsonify({"error": f"Failed to update WebAI index: {str(webai_e)}"}), 500
                # Placeholder for successful WebAI call (remove when uncommenting actual call)
                print("Placeholder: WebAI index update would be called here.")
            else:
                print("Skipping WebAI index update because WEB_AI_INDEX_PATH is not set.")
                return jsonify({"error": "WebAI index path not configured on the server."}), 500
            # --- End WebAI Indexing Step ---


            return jsonify({"message": "PDF processed and text extracted. WebAI index update attempted."}), 200

        except Exception as e:
            print(f"Error processing PDF: {e}")
            return jsonify({"error": f"Error processing PDF: {str(e)}"}), 500
        finally:
            # Clean up the temporary file
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    print(f"Cleaned up temporary file: {filepath}")
                except OSError as e:
                    print(f"Error removing temporary file {filepath}: {e}")

    else:
        return jsonify({"error": "Invalid file type. Only PDF files are allowed."}), 400

if __name__ == '__main__':
    # Note: Use a proper WSGI server like Gunicorn in production
    # debug=True should not be used in production
    app.run(debug=True, host='0.0.0.0', port=5001)