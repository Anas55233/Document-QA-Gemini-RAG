

def markdown_table_to_excel(gemini_response):
    lines = gemini_response.splitlines()
    
    table_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith("|") and line.endswith("|"):
            table_lines.append(line)
            
        # Step 3: Separate each table row into columns
    rows = []
    for line in table_lines:
        # Remove leading and trailing '|', then split by '|'
        cells = []
        
        for cell in line.strip('|').split('|'):
            # Remove leading and trailing whitespace from each cell
            cell = cell.strip()
            cells.append(cell)
            
            # Check if the cell is not just dashes (which indicates a separator row)
            is_separator = True

            for cell in cells:

                cell = cell.strip()

                cell = cell.replace("-", "")
                cell = cell.replace(":", "")
                cell = cell.replace(" ", "")

                if cell != "":
                    is_separator = False
                    break

            if is_separator:
                continue
        
        rows.append(cells)
    
    if len(rows) < 2:
        return None  # Not enough data to create a table
        
    header = rows[0]  # First row is the header
    data_rows = []  # Subsequent rows are the data
    
    for row in rows[1:]:
        # If the row has fewer cells than the header, pad it with empty strings
        if len(row) < len(header):
            row += [""] * (len(header) - len(row))
            
        # If the row has more cells than the header, truncate it to match the header length   
        if len(row) > len(header):
            row = row[:len(header)]
        # Add the row to the data_rows list
        data_rows.append(row)
    
    df = pd.DataFrame(data_rows, columns=header) # Create a DataFrame from the data rows and header
    
   
   # Step 4: Convert the DataFrame to Excel format in memory 
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name='Sheet1'
            )
        
    output.seek(0)  # Move the cursor to the beginning of the BytesIO object
    
    return output.getvalue() # Return the Excel file content as bytes
    
    
    

def data_to_excel(data):
    """
    Convert structured data into an Excel file.
    data should be a list of dictionaries.
    Example:
    [
        {"Name": "Ali", "Age": 25},
        {"Name": "Ahmed", "Age": 30}
    ]
    """

    if not data:
        return None

    df = pd.DataFrame(data)
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="Sheet1"
        )

    output.seek(0)

    return output.getvalue()
    
    
    
    
    
def extract_data_for_excel(question, context, chat_history=""):
    
    """
    Extract data from the document context for Excel generation.

    Gemini returns JSON internally.
    The JSON is never shown to the user.
    """

    model = create_gemini_model()

    prompt = f"""
You are an Excel data extraction system.

The user wants an Excel spreadsheet based ONLY on the provided
document context.

Your job is to extract the relevant information from the document
and return it as JSON.

IMPORTANT RULES:

1. Use ONLY the provided document context.
2. Do not invent or guess information.
3. Extract all relevant rows that answer the user's request.
4. Use clear column names.
5. Every row must represent one record.
6. Return ONLY valid JSON.
7. Do not use Markdown.
8. Do not add explanations.
9. Do not add ```json or ``` around the response.
10. If the requested information cannot be found, return [].

Example format:

[
    {{
        "Name": "Ali",
        "Amount": "5000",
        "Date": "22 Dec 2025"
    }},
    {{
        "Name": "Ahmed",
        "Amount": "3000",
        "Date": "25 Dec 2025"
    }}
]

Chat History:
{chat_history}

Document Context:
{context}

User Request:
{question}

Return ONLY the JSON array.
"""

    try:
        response = model.invoke(prompt)

        content = response.content

        if isinstance(content, list):
            text = ""

            for item in content:
                if isinstance(item, dict):
                    text += item.get("text", "")
                else:
                    text += str(item)

            content = text

        content = str(content).strip()

        # Remove accidental markdown code fences
        content = re.sub(r"^```json\s*", "", content, flags=re.IGNORECASE)
        content = re.sub(r"^```\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

        import json

        data = json.loads(content)

        if not isinstance(data, list):
            return None

        return data

    except Exception as e:

        error_message = str(e)

        if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            st.error(
                "⚠️ Gemini API quota exceeded. "
                "Please try again later."
            )

        elif "401" in error_message or "403" in error_message:
            st.error(
                "❌ Gemini API authentication/permission error. "
                "Please check your API key."
            )

        else:
            st.error(
                f"❌ Excel data extraction error: {error_message}"
            )

        return None
    
    
    
def check_excel_possible(question, context):
    """
    Quickly checks whether the document context contains
    useful data for creating an Excel sheet.
    """

    model = create_gemini_model()

    prompt = f"""
You are checking whether an Excel spreadsheet can reasonably
be created from the provided document context.

User request:
{question}

Document context:
{context}

Answer ONLY with one word:

YES
or
NO

Return YES if the document contains actual structured,
transactional, numerical, tabular, list-based, or record-based
information that can meaningfully be placed into Excel.

Return NO if the document is mainly explanatory text,
paragraphs, instructions, letters, descriptions, or other
content where creating an Excel sheet would not be meaningful.

Do not explain your answer.
"""

    try:
        response = model.invoke(prompt)

        content = response.content

        if isinstance(content, list):
            text = ""
            for item in content:
                if isinstance(item, dict):
                    text += item.get("text", "")
                else:
                    text += str(item)

            content = text

        result = str(content).strip().upper()

        return result.startswith("YES")

    except Exception:
        return False 
    
    
    
    def create_excel(question, context, chat_history):
        data = extract_data_for_excel(
        question,
        context,
        chat_history
    )

    return data_to_excel(data)