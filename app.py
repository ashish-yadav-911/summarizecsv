import os
import pandas as pd
from fpdf import FPDF
from openai import OpenAI
import unicodedata
from prompt import prompt_csv
from dotenv import load_dotenv

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Folder containing the CSV files
folder_path = "csvfilehere" 
# Output PDF file
output_pdf = os.getenv('OUTPUT_FILE_NAME')

def summarize_csv(file_path):

    try:

        df = pd.read_csv(file_path)
        csv_content = df.to_string(index=False) # if csv file is too big use this, df(10) to test, then add a chunker
        
        # prompt from prompt.py
        prompt = prompt_csv
        
        # Generate the summary
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error summarizing {file_path}: {e}"
    
def sanitize_text(text):
    """
    Removes or replaces characters not supported by fpdf.
    """
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

def add_summary_to_pdf(pdf, file_name, summary):
    """
    Adds the file name and its summary to the PDF.
    """
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=file_name, ln=True, align='C')
    pdf.ln(3)  # Add some spacing
    sanitized_summary = sanitize_text(summary)  # Sanitize the summary
    pdf.multi_cell(0, 10, txt=sanitized_summary)

def main():
    pdf = FPDF()
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".csv"):
            file_path = os.path.join(folder_path, file_name)
            print(f"Summarizing {file_name}...")
            summary = summarize_csv(file_path)
            add_summary_to_pdf(pdf, file_name, summary)
            print(f"Summary for {file_name} added.")
    
    # Save the PDF
    pdf.output(output_pdf)
    print(f"Summaries compiled into {output_pdf}")

if __name__ == "__main__":
    main()
