import os
import json
import pandas as pd
from google import genai

# =========================
# CONFIG
# =========================

MODEL_NAME = "gemini-2.0-flash"

# =========================
# INIT GEMINI CLIENT
# =========================

def init_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    return genai.Client(api_key=api_key)


# =========================
# LOAD DATA
# =========================

def load_static_hooks(path):
    return pd.read_excel(path).fillna("")


def load_requests(path):
    return pd.read_csv(path).fillna("")


# =========================
# BUILD HOOK LIBRARY STRING
# =========================

def build_hook_library_string(df):
    rows = []
    for _, row in df.iterrows():
        row_text = "\n".join([f"{k}: {v}" for k, v in row.to_dict().items()])
        rows.append(row_text)
    return "\n\n---\n\n".join(rows)


# =========================
# GEMINI CALL
# =========================

def process_request(client, request_row, hook_library_text):

    request_text = "\n".join(
        [f"{k}: {v}" for k, v in request_row.items()]
    )

    prompt = f"""
You are a Hook Selection Agent.

You are given:

1) A request context
2) A reference hook library

Your tasks:

1. Select ONE hook from the reference library that best matches the request.
2. Return the selected hook's identifier exactly as written.
3. Generate ONE new hook sentence.
4. Provide short reasoning.

IMPORTANT:
- Only select from the provided library.
- Do NOT invent identifiers.
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

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )

    try:
        return json.loads(response.text)
    except Exception as e:
        print("Invalid JSON returned:")
        print(response.text)
        print("Error:", e)
        return None


# =========================
# MAIN PIPELINE
# =========================

def main():

    client = init_client()

    static_df = load_static_hooks("TEMPLATE_HOOK.xlsx")
    request_df = load_requests("REQUEST_CONTEXT.csv")

    hook_library_text = build_hook_library_string(static_df)

    output_rows = []

    for _, req in request_df.iterrows():

        result = process_request(
            client,
            req.to_dict(),
            hook_library_text
        )

        if not result:
            continue

        selected_identifier = result["selected_hook_identifier"]

        matching_row = static_df[
            static_df.apply(
                lambda row: selected_identifier in row.astype(str).values,
                axis=1
            )
        ]

        if matching_row.empty:
            print(f"Identifier not found: {selected_identifier}")
            continue

        hook_data = matching_row.iloc[0].to_dict()

        output_row = {
            "request_id": req.get("request_id", ""),
            "selected_hook_identifier": selected_identifier,
            "generated_hook": result["generated_hook"],
            "reasoning": result["reasoning"]
        }

        # Attach reference metadata dynamically
        for k, v in hook_data.items():
            output_row[f"ref_{k}"] = v

        output_rows.append(output_row)

    output_df = pd.DataFrame(output_rows)
    output_df.to_csv("HOOK_SELECTOR_OUTPUT.csv", index=False)

    print("Hook selection completed.")
    print("Output file: HOOK_SELECTOR_OUTPUT.csv")


# =========================

if __name__ == "__main__":
    main()
