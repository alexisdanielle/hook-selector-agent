import os
import json
import pandas as pd
import google.generativeai as genai

# =========================
# CONFIG
# =========================

MODEL_NAME = "gemini-1.5-pro"

# =========================
# INIT GEMINI
# =========================

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel(MODEL_NAME)

# =========================
# LOAD FILES (NO HARD CODING)
# =========================

def load_static_hooks(path):
    df = pd.read_excel(path).fillna("")
    return df

def load_requests(path):
    df = pd.read_csv(path).fillna("")
    return df

# =========================
# BUILD HOOK LIBRARY STRING (DYNAMIC)
# =========================

def build_hook_library_string(df):
    rows = []
    for _, row in df.iterrows():
        row_dict = row.to_dict()
        row_text = "\n".join([f"{k}: {v}" for k, v in row_dict.items()])
        rows.append(row_text)
    return "\n\n---\n\n".join(rows)

# =========================
# CALL GEMINI
# =========================

def process_request(request_row, hook_library_text):

    request_text = "\n".join([f"{k}: {v}" for k, v in request_row.items()])

    prompt = f"""
You are a Hook Selection Agent.

You are given:

1) A request context
2) A reference hook library

Your tasks:

1. Select ONE hook from the reference library that best matches the request.
2. Return the selected hook's identifier exactly as written in the library.
3. Generate ONE new hook sentence that is suitable for the request.
4. Generate short reasoning.

IMPORTANT RULES:
- Do NOT invent a reference hook that does not exist.
- Only select from the provided library.
- Output STRICT JSON.

Output format:

{{
  "selected_hook_identifier": "...",
  "generated_hook": "...",
  "reasoning": "..."
}}

REQUEST CONTEXT:
{request_text}

REFERENCE HOOK LIBRARY:
{hook_library_text}
"""

    response = model.generate_content(prompt)
    text = response.text.strip()

    # Remove markdown fences if present
    if text.startswith("```"):
        text = text.split("```")[1]

    try:
        return json.loads(text)
    except:
        print("Invalid JSON returned:")
        print(text)
        return None

# =========================
# MAIN PIPELINE
# =========================

def main():

    static_df = load_static_hooks("TEMPLATE_HOOK.xlsx")
    request_df = load_requests("REQUEST_CONTEXT.csv")

    hook_library_text = build_hook_library_string(static_df)

    output_rows = []

    for _, req in request_df.iterrows():
        result = process_request(req.to_dict(), hook_library_text)

        if not result:
            continue

        selected_identifier = result["selected_hook_identifier"]

        # Find matching row dynamically
        matching_row = static_df[
            static_df.apply(lambda row: selected_identifier in row.astype(str).values, axis=1)
        ]

        if matching_row.empty:
            print(f"Selected identifier not found: {selected_identifier}")
            continue

        hook_data = matching_row.iloc[0].to_dict()

        output_row = {
            "request_id": req.get("request_id", ""),
            "selected_hook_identifier": selected_identifier,
            "generated_hook": result["generated_hook"],
            "reasoning": result["reasoning"]
        }

        # Attach ALL original hook metadata dynamically
        for k, v in hook_data.items():
            output_row[f"ref_{k}"] = v

        output_rows.append(output_row)

    output_df = pd.DataFrame(output_rows)
    output_df.to_csv("HOOK_MAPPING_OUTPUT.csv", index=False)

    print("Hook mapping completed.")
    print("Output: HOOK_MAPPING_OUTPUT.csv")

# =========================

if __name__ == "__main__":
    main()
