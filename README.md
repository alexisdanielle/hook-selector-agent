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
hook-selector-agent/ </br>
│ </br>
├── hook_selector_agent.py </br>
├── TEMPLATE_HOOK.xlsx</br>
├── REQUEST_CONTEXT.csv</br>
└── README.md</br>


Setup and Running </br>
```pip install google-generativeai pandas openpyxl```</br>
```setx GEMINI_API_KEY "your_api_key_here"```</br>
```python hook_selector_agent.py```</br>


NOTES : 
Input Files
1. TEMPLATE_HOOK.xlsx (Static Hook Library)
Each row represents one hook template.
You can structure the columns however you like.

2. REQUEST_CONTEXT.csv (Dynamic Requests)
Each row represents one video/content request.
Variable Structure : request_id,persona,audience_stage,platform,niche,topic,goal

