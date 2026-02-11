# hook-selector-agent
What This Does : 
For each content request:
1. Reads your static hook library (TEMPLATE_HOOK.xlsx)
2. Reads dynamic content requests (REQUEST_CONTEXT.csv)
3. Uses Gemini to:
   - Select one existing hook from your library
   - Generate one new custom hook variant
4. Outputs a structured CSV containing:
   - Selected reference hook
   - Generated hook
   - Short reasoning
   - All original hook metadata

Structure : 
hook-selector-agent/
│
├── hook_selector_agent.py
├── TEMPLATE_HOOK.xlsx
├── REQUEST_CONTEXT.csv
└── README.md


Setup 
```pip install google-generativeai pandas openpyxl```
```setx GEMINI_API_KEY "your_api_key_here"```
```python hook_selector_agent.py```


NOTES : 
Input Files
1. TEMPLATE_HOOK.xlsx (Static Hook Library)
Each row represents one hook template.
You can structure the columns however you like.

2. REQUEST_CONTEXT.csv (Dynamic Requests)
Each row represents one video/content request.
Variable Structure : request_id,persona,audience_stage,platform,niche,topic,goal

