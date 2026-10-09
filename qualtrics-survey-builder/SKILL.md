---
name: qualtrics-survey-builder
description: |
  Build and modify Qualtrics surveys programmatically via API v3.
  Handles question creation, block management, flow logic, Hebrew RTL,
  and look & feel. Includes safety patterns to prevent data loss.

  TRIGGERS: "create qualtrics survey", "build survey", "modify qualtrics",
  "qualtrics API", "survey builder", "add questions to qualtrics",
  "qualtrics question", "survey flow", "skip logic qualtrics",
  "סקר קוולטריקס", "בניית שאלון", "שאלון בקוולטריקס"
---

# Qualtrics Survey Builder

Build and modify Qualtrics surveys via the API. All code is Python (stdlib only, no pip installs).

## Decision Tree

```
What do you want to do?
|
+-- Modify an existing survey -----> Workflow A (export QSF -> reimport -> API changes)
|   +-- Remove question numbers ---> safe_question_update() + regex
|   +-- Rename blocks -------------> PUT block with Description field
|   +-- Add consent form ----------> DB/TB template + consent flow pattern
|   +-- Add skip logic ------------> Survey Flow patterns
|   +-- Change look & feel --------> Look & Feel Presets
|
+-- Build a new survey from scratch -> Workflow B (sequential API calls)
|
+-- Add a single question ----------> Question Type Templates
+-- Fix a broken survey ------------> Read CRITICAL WARNINGS first, then verify
+-- Verify a survey is correct -----> Pre-Publish Verification Checklist
```

---

## CRITICAL WARNINGS

### 0. NEVER Hardcode API Tokens

**NEVER extract tokens from source files and paste them into scripts.** Always load them from environment variables at runtime:

```python
import os
API_TOKEN = os.environ["QUALTRICS_API_KEY"]            # <YOUR_API_KEY>
BASE = f"https://{os.environ['QUALTRICS_BASE_URL']}/API/v3"  # e.g. yourorg.eu.qualtrics.com
```

Never put tokens in CLAUDE.md, documentation, plans, or generated scripts. If a token is needed and the environment variables are not set, **ask the user** to set them.

The warnings below are about Qualtrics API behavior. Read before ANY API call.

### 1. PUT = FULL REPLACE (a partial PUT wipes the rest of the question)

`PUT /survey-definitions/{sid}/questions/{qid}` **replaces the ENTIRE question definition**. Sending only changed fields WIPES everything else (Choices, DataExportTag, Validation, SubSelector, Configuration).

```python
# WRONG - destroys the question
api_put(f".../{qid}", {"QuestionText": new_text})

# CORRECT - preserve everything
qdata = api_get(f"/survey-definitions/{sid}/questions/{qid}")
updated = copy.deepcopy(qdata)
updated["QuestionText"] = new_text
strip_readonly(updated)
api_put(f"/survey-definitions/{sid}/questions/{qid}", updated)
```

### 2. Default Block Trap

New questions created via `POST .../questions` auto-land in the Default block, even if you specify a different block. After creating questions, always verify they are in the correct block and move them if needed.

### 3. Stale Data After Structural Changes

After creating/deleting blocks or questions, the survey definition cache is stale. Always re-fetch with `GET /survey-definitions/{sid}` before updating flow or making further structural changes.

### 4. Survey Name vs SurveyTitle

Two different fields, two different endpoints:
- **Project list name**: `PUT /surveys/{sid}` with `{"name": "..."}`
- **Internal SurveyTitle**: `PUT /survey-definitions/{sid}/options` with `{"SurveyTitle": "..."}`

### 5. Match the RESPONSE FORMAT to the validated instrument (not just the items)

When you build a validated scale into a survey, the **response format is part of the instrument** — the number
of response categories, the value range, the presence/absence of a neutral midpoint, and the anchor labels.
Reproducing the item wording correctly but silently changing the response format (e.g. entering a 5-point
scale with a neutral midpoint as a 4-point forced-choice grid) rescales the raw metric and breaks
cross-study / norm comparability. It is easy to miss because item text looks right.

Before publishing any established scale, verify against the source paper:

- **Category count + anchors**: does the source use 4, 5, 6, or 7 points? Does it have a neutral midpoint?
  Are the endpoint (and any mid) labels the same? In the `Matrix/Likert` template, `Answers` = the scale
  points — its length and labels must equal the instrument's.
- **Value range**: the exported numeric range (1..k) must equal the instrument's declared range.
- **Reverse-keyed items**: keep them (do not "fix" wording to be positive) — scoring handles the reversal.

Origin: a published 5-point attitude scale with a neutral midpoint was administered as a 4-category grid.
Every item was correct; only the response format differed, which broke norm comparability. The data was
internally consistent, so nothing had to be re-run, but it is a real cross-study-comparison limitation that
item-only checks did not catch. **Rule: verify the scale/response format against the instrument, not only
the items.**

---

## API Setup

### Credentials

Set two environment variables before running any script:

| Variable | Example value | Notes |
|---------|----------|---------|
| `QUALTRICS_API_KEY` | `<YOUR_API_KEY>` | Qualtrics -> Account Settings -> Qualtrics IDs -> API token |
| `QUALTRICS_BASE_URL` | `yourorg.eu.qualtrics.com` | Your organization's datacenter host, without `https://` |

These are the same two names the R `qualtRics` package uses, and the sibling `qualtrics-cleaning` skill reads them too, so one setup serves both skills.

If you work with several Qualtrics accounts (e.g., one per grant or project), give each its own pair of variables (`QUALTRICS_API_KEY_PROJECTA`, ...) and choose the pair at the top of the script.

### Create Survey From Scratch (Preferred over QSF import)

QSF import via `POST /surveys` is unreliable (500 errors, Hebrew encoding issues). Use this instead:

```python
# Create blank survey
resp = api_post("/survey-definitions", {
    "SurveyName": "English Name Only",  # Hebrew breaks in project list!
    "Language": "HE",
    "ProjectCategory": "CORE"
})
sid = resp.get('result', {}).get('SurveyID')

# Then add blocks, questions, flow, options via API
# Activate when ready:
api_put(f"/surveys/{sid}", {"isActive": True})
```

### ⚠️ CRITICAL: PUBLISH CHANGES AFTER EVERY MODIFICATION

**This is the #1 mistake to avoid.** When you modify a survey via API (add questions, edit text, change flow, update block elements), the changes are saved as a DRAFT VERSION. Participants see the LAST PUBLISHED VERSION — NOT the draft. You MUST explicitly publish or changes are invisible to respondents.

**Symptom of the bug:** API verification shows your changes are present, but when someone opens the survey URL `/jfe/form/SV_XXX` they still see the old version. The API shows version 7 but `published: false`, while version 6 is still `published: true` and that's what participants see.

**How to publish:**

```python
def publish_survey(sid, description="Updated via API"):
    """Publish the latest draft so participants see the changes."""
    result = api_post(f"/survey-definitions/{sid}/versions", {
        "Description": description,
        "Published": True,
    })
    if result:
        meta = result.get("result", {}).get("metadata", {})
        print(f"  ✓ Published {sid}: v{meta.get('versionNumber')} published={meta.get('published')}")
    return result
```

**How to check if unpublished changes exist:**

```python
def check_published_status(sid):
    """Returns True if latest version is published, False if there are unpublished drafts."""
    r = api_get(f"/survey-definitions/{sid}/versions")
    if r:
        versions = r.get("elements", [])
        if versions:
            latest = versions[0].get("metadata", {})
            return latest.get("published", False)
    return False
```

**ALWAYS publish after:**
- Adding/removing questions
- Editing question text
- Changing block structure (moving questions between blocks)
- Updating flow
- Modifying answer choices (Matrix rows, MC options)
- Any PUT/POST to `/survey-definitions/{sid}/*`

**Verify publishing worked by:**
1. Checking `published: True` on the latest version via `GET /survey-definitions/{sid}/versions`
2. **Opening the survey URL in a browser as a participant would** (non-negotiable — see Pre-Publish Verification Checklist)

Learned the hard way: a whole batch of survey changes (a new intro, merged blocks, reworded items) was saved via the API but invisible to participants because it was never published. The research team kept seeing the old survey after the fixes had been announced.

### ChoiceDataExportTags (Self-Documenting Exports)

Set descriptive tags on Matrix choices so exports have meaningful column names:

```python
# Instead of wellbeing_pre_1, wellbeing_pre_2...
# Get: wellbeing_pre_sleep, wellbeing_pre_energy...
updated['ChoiceDataExportTags'] = {
    '1': 'sleep',
    '2': 'energy',
    '8': 'mood',
    '9': 'focus',
}
```

### Email Validation

```python
updated['Validation'] = {
    'Settings': {
        'ForceResponse': 'ON', 'ForceResponseType': 'ON',
        'Type': 'ContentType', 'ContentType': 'ValidEmail',
    }
}
```

### Min Character Validation (Open-Ended)

```python
updated['Validation'] = {
    'Settings': {
        'ForceResponse': 'ON', 'ForceResponseType': 'ON',
        'Type': 'MinChar', 'MinChars': '20',
    }
}
```

### Python Boilerplate

Every script MUST start with this setup:

```python
"""
Qualtrics Survey Builder Script
Purpose: [describe what this script does]
Survey: [survey ID]
"""
import json, urllib.request, urllib.error, sys, io, copy, re

# Hebrew console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# --- Credentials (ALWAYS load from environment variables, never hardcode) ---
import os
API_TOKEN = os.environ["QUALTRICS_API_KEY"]
BASE = f"https://{os.environ['QUALTRICS_BASE_URL']}/API/v3"
SID = "SV_XXXXXXXXXX"  # Target survey ID

headers_json = {"X-API-TOKEN": API_TOKEN, "Content-Type": "application/json"}

def api_get(path):
    """GET request. Returns parsed result or None on error."""
    req = urllib.request.Request(f"{BASE}{path}", headers={"X-API-TOKEN": API_TOKEN})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))['result']
    except urllib.error.HTTPError as e:
        print(f"  GET ERROR {e.code}: {e.read().decode('utf-8')[:400]}")
        return None

def api_put(path, data):
    """PUT request (FULL REPLACE). Returns response or None on error."""
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers_json, method='PUT')
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"  PUT ERROR {e.code}: {e.read().decode('utf-8')[:400]}")
        return None

def api_post(path, data):
    """POST request (create). Returns response or None on error."""
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers_json, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"  POST ERROR {e.code}: {e.read().decode('utf-8')[:400]}")
        return None

def api_post_multipart(path, file_path, file_field="file"):
    """POST multipart/form-data (for QSF import). Returns response or None."""
    import mimetypes
    boundary = "----PythonBoundary"
    with open(file_path, 'rb') as f:
        file_data = f.read()
    fname = file_path.split("\\")[-1].split("/")[-1]
    mime = mimetypes.guess_type(fname)[0] or "application/octet-stream"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="{file_field}"; filename="{fname}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode('utf-8') + file_data + f"\r\n--{boundary}--\r\n".encode('utf-8')
    req = urllib.request.Request(
        f"{BASE}{path}", data=body,
        headers={"X-API-TOKEN": API_TOKEN, "Content-Type": f"multipart/form-data; boundary={boundary}"},
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"  POST MULTIPART ERROR {e.code}: {e.read().decode('utf-8')[:400]}")
        return None
```

---

## Safe Update Pattern

The single most important function. Use this for ALL question modifications.

```python
READONLY_FIELDS = ['QuestionID', 'Language', 'QuestionText_Unsafe', 'NextChoiceId', 'NextAnswerId']

def strip_readonly(qdata):
    """Remove read-only fields that Qualtrics rejects on PUT."""
    for field in READONLY_FIELDS:
        qdata.pop(field, None)
    return qdata

def safe_question_update(sid, qid, modify_fn):
    """
    SAFE question update pattern:
    1. Fetch current question data
    2. Deep copy it
    3. Apply modifications via modify_fn(updated_data)
    4. Strip read-only fields
    5. PUT the complete updated question

    Usage:
        def my_changes(q):
            q["QuestionText"] = "<div dir='rtl'>New text</div>"
            q["DataExportTag"] = "Q1_new_tag"
        safe_question_update(SID, "QID1", my_changes)
    """
    qdata = api_get(f"/survey-definitions/{sid}/questions/{qid}")
    if not qdata:
        print(f"  ERROR: Could not fetch {qid}")
        return None
    updated = copy.deepcopy(qdata)
    modify_fn(updated)
    strip_readonly(updated)
    result = api_put(f"/survey-definitions/{sid}/questions/{qid}", updated)
    if result:
        print(f"  Updated {qid}: {result['meta']['httpStatus']}")
    return result
```

**Caveat (measured on a live survey, DB/TB question):** stripping `NextChoiceId`, `NextAnswerId` and
`DataVisibility` before the PUT did NOT make Qualtrics keep them - the stored question came back
without those fields; a PUT that kept them (only `QuestionID` removed) was accepted. So the "rejects
on PUT" comment above does not hold for every question type. Whatever you strip, GET the whole
survey definition (`GET /survey-definitions/{sid}`) before and after, compare every question key by
key, and require that only the intended keys changed.

---

## Workflow A: Modify Existing Survey (Recommended)

Use this when you have an existing survey and need to change it.

### Step 1: Export QSF
```python
# Via API (preferred)
# GET /survey-definitions/{sid}?format=qsf returns the QSF file content
req = urllib.request.Request(
    f"{BASE}/survey-definitions/{SID}?format=qsf",
    headers={"X-API-TOKEN": API_TOKEN}
)
with urllib.request.urlopen(req) as resp:
    qsf_data = resp.read()
with open("survey_export.qsf", "wb") as f:
    f.write(qsf_data)
print(f"Exported to survey_export.qsf ({len(qsf_data)} bytes)")
```
**Fallback**: Export manually from Qualtrics UI (Tools -> Import/Export -> Export Survey)

### Step 2: Import as New Copy
```python
result = api_post_multipart("/surveys", "survey_export.qsf")
if result:
    new_sid = result['result']['id']
    print(f"Imported as new survey: {new_sid}")
```
**Fallback**: Import manually from Qualtrics UI (Create Project -> From QSF)

### Step 3: Fetch Full Definition
```python
survey = api_get(f"/survey-definitions/{new_sid}")
blocks = survey['Blocks']
questions = survey['Questions']
flow = survey['SurveyFlow']
print(f"Blocks: {len(blocks)}, Questions: {len(questions)}")
```

### Step 4: Apply Modifications
Use `safe_question_update()` for each change. Common operations:

**Remove question numbers from text:**
```python
for qid, qdata in questions.items():
    text = qdata.get('QuestionText', '')
    clean = re.sub(r'<[^>]+>', '', text).strip()
    if re.match(r'^\d+\.?\s', clean):
        def remove_number(q, original_text=text):
            q['QuestionText'] = re.sub(r'^(\s*(?:<[^>]+>)*\s*)\d+\.?\s*', r'\1', original_text)
        safe_question_update(new_sid, qid, remove_number)
```

**Rename blocks to English:**
```python
block_names = {
    "BL_abc123": "Part A - Demographics",
    "BL_def456": "Part B - AI Usage",
}
for bid, new_name in block_names.items():
    bdata = blocks[bid]
    bdata['Description'] = new_name
    api_put(f"/survey-definitions/{new_sid}/blocks/{bid}", bdata)
```

### Step 5: Set Look & Feel (see Presets section)
### Step 6: Verify (see Verification Checklist)

---

## Workflow B: Build From Scratch

### Step 1: Start with a Base Survey
Create a minimal survey in Qualtrics UI or import a minimal QSF, then get its ID.

### Step 2: Create Blocks
```python
blocks_to_create = [
    {"Description": "Consent", "Type": "Standard"},
    {"Description": "Introduction", "Type": "Standard"},
    {"Description": "Part A - Demographics", "Type": "Standard"},
    {"Description": "Part B - AI Usage", "Type": "Standard"},
    {"Description": "Part C - Attitudes", "Type": "Standard"},
]
block_ids = {}
for block in blocks_to_create:
    result = api_post(f"/survey-definitions/{SID}/blocks", block)
    if result:
        bid = result['result']['BlockID']
        block_ids[block['Description']] = bid
        print(f"  Created block '{block['Description']}': {bid}")
```

### Step 3: Create Questions (use Templates below)
### Step 4: Build Survey Flow (see Flow Patterns)
### Step 5: Set Options (see Look & Feel Presets)
### Step 6: Verify (see Verification Checklist)

---

## Question Type Templates

All templates include Hebrew RTL wrapping. Replace placeholder text with actual content.

### MC/SAVR (Single Choice Radio)
```python
mc_single = {
    "QuestionText": '<div dir="rtl" style="text-align: right;">שאלה כאן?</div>',
    "DataExportTag": "Q1_variable_name",
    "QuestionType": "MC",
    "Selector": "SAVR",       # Single Answer Vertical Radio
    "SubSelector": "TX",
    "Configuration": {"QuestionDescriptionOption": "UseText"},
    "Choices": {
        "1": {"Display": "אפשרות א"},
        "2": {"Display": "אפשרות ב"},
        "3": {"Display": "אפשרות ג"},
    },
    "ChoiceOrder": ["1", "2", "3"],
    "Validation": {"Settings": {"ForceResponse": "ON", "ForceResponseType": "ON", "Type": "None"}},
    "Language": [],
    "QuestionDescription": "Q1_variable_name",
}
```

### MC/MAVR (Multiple Choice Checkboxes)
```python
mc_multi = {
    "QuestionText": '<div dir="rtl" style="text-align: right;">בחר את כל המתאימים:</div>',
    "DataExportTag": "Q2_multi",
    "QuestionType": "MC",
    "Selector": "MAVR",       # Multiple Answer Vertical Radio (checkboxes)
    "SubSelector": "TX",
    "Configuration": {"QuestionDescriptionOption": "UseText"},
    "Choices": {
        "1": {"Display": "אפשרות א"},
        "2": {"Display": "אפשרות ב"},
        "3": {"Display": "אפשרות ג"},
        "4": {"Display": "אחר", "TextEntry": "true", "TextEntrySize": "Medium"},
    },
    "ChoiceOrder": ["1", "2", "3", "4"],
    "Validation": {"Settings": {"ForceResponse": "ON", "ForceResponseType": "ON", "Type": "None"}},
    "Language": [],
}
```

### TE/SL (Single-Line Text Entry)
```python
te_single = {
    "QuestionText": '<div dir="rtl" style="text-align: right;">שנת לידה:</div>',
    "DataExportTag": "Q3_birth_year",
    "QuestionType": "TE",
    "Selector": "SL",         # Single Line
    "Configuration": {"QuestionDescriptionOption": "UseText"},
    "Validation": {
        "Settings": {
            "ForceResponse": "ON",
            "ForceResponseType": "ON",
            "Type": "ContentType",
            "ContentType": "ValidNumber",       # Optional: enforce numeric
            "CustomValidation": {"Logic": {"0": {"0": {"ChoiceLocator": "q://QID/QuestionText",
                "Operator": "GreaterThan", "Value": "1920", "Type": "Expression"}}}}
        }
    },
    "Language": [],
}
```

### TE/ML (Multi-Line Text / Open-Ended)
```python
te_multi = {
    "QuestionText": '<div dir="rtl" style="text-align: right;">אנא פרט/י:</div>',
    "DataExportTag": "Q4_open_ended",
    "QuestionType": "TE",
    "Selector": "ML",         # Multi Line
    "Configuration": {"QuestionDescriptionOption": "UseText"},
    "Validation": {"Settings": {"ForceResponse": "OFF", "Type": "None"}},  # OFF for open-ended
    "Language": [],
}
```

### Matrix/Likert
```python
matrix_likert = {
    "QuestionText": '<div dir="rtl" style="text-align: right;">דרג/י כל אחד מהבאים:</div>',
    "DataExportTag": "Q5_likert",
    "QuestionType": "Matrix",
    "Selector": "Likert",
    "SubSelector": "SingleAnswer",
    "Configuration": {"QuestionDescriptionOption": "UseText"},
    "Choices": {                          # ROWS (items/statements)
        "1": {"Display": "פריט ראשון"},
        "2": {"Display": "פריט שני"},
        "3": {"Display": "פריט שלישי"},
    },
    "ChoiceOrder": ["1", "2", "3"],
    "Answers": {                          # COLUMNS (scale points)
        "1": {"Display": "כלל לא"},
        "2": {"Display": "במידה מועטה"},
        "3": {"Display": "במידה בינונית"},
        "4": {"Display": "במידה רבה"},
        "5": {"Display": "במידה רבה מאוד"},
    },
    "AnswerOrder": ["1", "2", "3", "4", "5"],
    "Validation": {"Settings": {"ForceResponse": "ON", "ForceResponseType": "ON", "Type": "None"}},
    "Language": [],
}
```

### DB/TB (Descriptive Text Block)
```python
db_text = {
    "QuestionText": '<div dir="rtl" style="text-align: right;">טקסט תיאורי כאן. יכול לכלול <b>עיצוב</b> ופסקאות.</div>',
    "DataExportTag": "intro_text",
    "QuestionType": "DB",
    "Selector": "TB",         # Text Block
    "Configuration": {"QuestionDescriptionOption": "UseText"},
    "Validation": {"Settings": {"ForceResponse": "OFF", "Type": "None"}},
    "Language": [],
}
```

### Creating a Question in a Block
```python
# Create the question
result = api_post(f"/survey-definitions/{SID}/questions", mc_single)
if result:
    new_qid = result['result']['QuestionID']
    print(f"  Created question: {new_qid}")

    # IMPORTANT: Verify it landed in the correct block
    # Re-fetch survey to check
    survey = api_get(f"/survey-definitions/{SID}")
    # If question is in Default block, move it to the target block
```

---

## Block Operations

### Create a Block
```python
result = api_post(f"/survey-definitions/{SID}/blocks", {
    "Description": "Part A - Demographics",
    "Type": "Standard"
})
block_id = result['result']['BlockID']
```

### Add Question to a Specific Block
```python
# Fetch the block
block = api_get(f"/survey-definitions/{SID}/blocks/{block_id}")
# Add question reference
block['BlockElements'].append({"Type": "Question", "QuestionID": "QID123"})
# Update the block
api_put(f"/survey-definitions/{SID}/blocks/{block_id}", block)
```

### Remove Question from Default Block
```python
# After creating questions, check the Default block
survey = api_get(f"/survey-definitions/{SID}")
for bid, bdata in survey['Blocks'].items():
    if bdata.get('Description', '') in ('Default Question Block', 'Trash'):
        elements = bdata.get('BlockElements', [])
        qids_in_default = [e['QuestionID'] for e in elements if e.get('Type') == 'Question']
        if qids_in_default:
            print(f"  WARNING: Questions in Default block: {qids_in_default}")
            # Remove them
            bdata['BlockElements'] = [e for e in elements if e.get('Type') != 'Question']
            api_put(f"/survey-definitions/{SID}/blocks/{bid}", bdata)
```

---

## Survey Flow Patterns

### Consent Termination
If participant declines consent, end the survey immediately.

```python
consent_branch = {
    "Type": "Branch",
    "FlowID": "FL_consent",
    "Description": "Consent Check",
    "BranchLogic": {
        "0": {
            "0": {
                "LogicType": "Question",
                "QuestionID": "QID_CONSENT",       # Replace with actual QID
                "QuestionIsInLoop": "no",
                "ChoiceLocator": "q://QID_CONSENT/SelectableChoice/2",  # Choice 2 = decline
                "Operator": "Selected",
                "QuestionIDFromLocator": "QID_CONSENT",
                "LeftOperand": "q://QID_CONSENT/SelectableChoice/2",
                "Type": "Expression",
                "Description": "<span>If decline consent</span>"
            }
        },
        "Type": "If"
    },
    "Flow": [
        {"Type": "EndSurvey", "FlowID": "FL_endsent", "EndingType": "Default", "Options": {"Advanced": "false"}}
    ]
}
```

### Conditional Skip (Show Block Only If Condition Met)
Show Part B only if participant did NOT select "Never" on Q7.

```python
skip_branch = {
    "Type": "Branch",
    "FlowID": "FL_skip",
    "Description": "Q7 Skip Logic",
    "BranchLogic": {
        "0": {
            "0": {
                "LogicType": "Question",
                "QuestionID": "QID7",
                "QuestionIsInLoop": "no",
                "ChoiceLocator": "q://QID7/SelectableChoice/5",  # Choice 5 = "Never"
                "Operator": "NotSelected",                       # NOT selected -> show block
                "QuestionIDFromLocator": "QID7",
                "LeftOperand": "q://QID7/SelectableChoice/5",
                "Type": "Expression",
                "Description": "<span>If Q7 not Never</span>"
            }
        },
        "Type": "If"
    },
    "Flow": [
        {"Type": "Block", "ID": "BL_partB_usage", "FlowID": "FL_partB"}  # Block shown conditionally
    ]
}
```

### Complete Survey Flow Structure
```python
full_flow = {
    "Type": "Root",
    "FlowID": "FL_1",
    "Flow": [
        {"Type": "Block", "ID": "BL_consent", "FlowID": "FL_2"},
        consent_branch,                                           # Branch: decline -> EndSurvey
        {"Type": "Block", "ID": "BL_intro", "FlowID": "FL_3"},
        {"Type": "Block", "ID": "BL_partA", "FlowID": "FL_4"},
        {"Type": "Block", "ID": "BL_partB_freq", "FlowID": "FL_5"},
        skip_branch,                                              # Branch: not-never -> show usage block
        {"Type": "Block", "ID": "BL_partC", "FlowID": "FL_7"},
        {"Type": "EndSurvey", "FlowID": "FL_end"},
    ],
    "Properties": {
        "Count": 8  # Must match number of elements in Flow array
    }
}

# Apply the flow
api_put(f"/survey-definitions/{SID}/flow", full_flow)
```

**Important**: FlowID values must be unique across the entire flow structure. Use sequential numbering (FL_1, FL_2, ...) or descriptive names (FL_consent, FL_skip).

---

## Look & Feel Presets

### Institutional Preset (Default)

Copy the options of a survey your institution already approved, then reuse them for every new survey:

```python
INSTITUTION_LOOK_FEEL = {
    'BackButton': 'false',
    'SurveyProtection': 'PublicSurvey',
    'SurveyExpiration': 'None',
    'SurveyTermination': 'DefaultMessage',
    'Header': '',
    'Footer': '',
    'SurveyLanguage': 'HE',
    'ProgressBarDisplay': 'NoText',
    'SecureResponseFiles': 'true',
    'SaveAndContinue': 'true',
    'NoIndex': 'Yes',
    'SurveyMetaDescription': 'שאלון מחקרי',
    'SkinType': 'component',
    'SkinLibrary': '<YOUR_SKIN_LIBRARY>',   # your organization's brand library name
    'Skin': {
        'brandingId': None,
        'templateId': '*simple',
        'overrides': {
            'logo': {
                'height': '60px',
                'position': 'center',
                'url': '<YOUR_LOGO_URL>'    # a graphic from your own Qualtrics library
            },
            'background': {'color': '#f5f5f5'},
            'colors': {
                'primary': '#1f6feb',
                'secondary': '#2da44e'
            }
        }
    }
}

# Apply it
api_put(f"/survey-definitions/{SID}/options", INSTITUTION_LOOK_FEEL)
```

### Customizing
Override any key in `INSTITUTION_LOOK_FEEL` before applying:

```python
custom = INSTITUTION_LOOK_FEEL.copy()
custom['SurveyMetaDescription'] = 'שאלון מחקרי - גרסה 2'
custom['Skin'] = {**INSTITUTION_LOOK_FEEL['Skin']}  # Shallow copy for nested dict
custom['Skin']['overrides'] = {**INSTITUTION_LOOK_FEEL['Skin']['overrides']}
custom['Skin']['overrides']['colors'] = {'primary': '#FF5733', 'secondary': '#33FF57'}
api_put(f"/survey-definitions/{SID}/options", custom)
```

### Rename Survey in Project List
```python
api_put(f"/surveys/{SID}", {"name": "My Study Wave 1 v4 FINAL"})
```

---

## Pre-Publish Verification Checklist

Run this function after ANY set of modifications. Catches problems before they reach participants.

```python
def verify_survey(sid, expected_blocks=None, consent_qid=None, open_ended_qids=None):
    """
    Run 15+ automated checks on a survey. Returns (passed, failed, details).

    Args:
        sid: Survey ID
        expected_blocks: Expected number of non-trash blocks (optional)
        consent_qid: QID of consent question (optional, auto-detected if tagged 'consent')
        open_ended_qids: List of QIDs that should have ForceResponse OFF (optional)
    """
    survey = api_get(f"/survey-definitions/{sid}")
    if not survey:
        print("FATAL: Could not fetch survey definition")
        return 0, 1, ["Could not fetch survey"]

    blocks = survey.get('Blocks', {})
    questions = survey.get('Questions', {})
    flow = survey.get('SurveyFlow', {})
    opts = api_get(f"/survey-definitions/{sid}/options") or {}

    passed = 0
    failed = 0
    details = []

    def check(name, condition, detail=""):
        nonlocal passed, failed
        if condition:
            print(f"  [PASS] {name}")
            passed += 1
        else:
            msg = f"  [FAIL] {name}" + (f" -- {detail}" if detail else "")
            print(msg)
            failed += 1
            details.append(msg)

    # --- Block Checks ---
    real_blocks = {k: v for k, v in blocks.items()
                   if 'Trash' not in v.get('Description', '') and 'Default' not in v.get('Description', '')}

    if expected_blocks:
        check(f"Block count = {expected_blocks}", len(real_blocks) == expected_blocks,
              f"Found {len(real_blocks)}")

    for bid, bdata in real_blocks.items():
        desc = bdata.get('Description', '')
        has_hebrew = bool(re.search(r'[\u0590-\u05FF]', desc))
        check(f"Block '{desc}' has English name", not has_hebrew, "Contains Hebrew characters")

    # --- Question Checks ---
    # Auto-detect consent QID
    if not consent_qid:
        for qid, qdata in questions.items():
            if qdata.get('DataExportTag', '').lower() == 'consent':
                consent_qid = qid
                break

    if consent_qid:
        cq = questions.get(consent_qid, {})
        check("Consent question exists", consent_qid in questions)
        check("Consent has 2 choices", len(cq.get('Choices', {})) == 2,
              f"Found {len(cq.get('Choices', {}))} choices")
        fr = cq.get('Validation', {}).get('Settings', {}).get('ForceResponse', '')
        check("Consent ForceResponse ON", fr == 'ON', f"Got: '{fr}'")

    if not open_ended_qids:
        open_ended_qids = []

    for qid, qdata in questions.items():
        qtype = qdata.get('QuestionType', '')
        tag = qdata.get('DataExportTag', '')

        if qtype == 'DB':
            continue

        # Check no leading numbers in question text
        text = re.sub(r'<[^>]+>', '', qdata.get('QuestionText', '')).strip()
        if re.match(r'^\d+\.?\s', text):
            check(f"{qid} ({tag}) no leading number", False, f"Text starts with number")

        # Check DataExportTag set
        check(f"{qid} has DataExportTag", bool(tag), "DataExportTag is empty")

        # Check ForceResponse
        fr = qdata.get('Validation', {}).get('Settings', {}).get('ForceResponse', '')
        if qid in open_ended_qids:
            check(f"{qid} ({tag}) ForceResponse OFF (open-ended)", fr == 'OFF', f"Got: '{fr}'")
        else:
            check(f"{qid} ({tag}) ForceResponse ON", fr == 'ON', f"Got: '{fr}'")

        # Check Choices integrity for MC questions
        if qtype == 'MC':
            choices = qdata.get('Choices', {})
            check(f"{qid} ({tag}) has choices", len(choices) > 0, f"0 choices found")

        # Check Matrix has both Answers and Choices
        if qtype == 'Matrix':
            answers = qdata.get('Answers', {})
            choices = qdata.get('Choices', {})
            check(f"{qid} ({tag}) has answers+choices",
                  len(answers) > 0 and len(choices) > 0,
                  f"Answers: {len(answers)}, Choices: {len(choices)}")

    # --- Flow Checks ---
    flow_items = flow.get('Flow', [])
    check("Flow has elements", len(flow_items) >= 2, f"Found {len(flow_items)}")

    # Check consent branch
    consent_branch_found = False
    for item in flow_items:
        if item.get('Type') == 'Branch':
            sub = item.get('Flow', [])
            if any(s.get('Type') == 'EndSurvey' for s in sub):
                consent_branch_found = True
                break
    if consent_qid:
        check("Consent branch with EndSurvey exists", consent_branch_found)

    # --- Options Checks ---
    check("SurveyLanguage is HE", opts.get('SurveyLanguage') == 'HE',
          f"Got: '{opts.get('SurveyLanguage', 'N/A')}'")

    skin_type = opts.get('SkinType', survey.get('SkinType', ''))
    check("SkinType is 'component'", skin_type == 'component', f"Got: '{skin_type}'")

    # --- Orphan Check ---
    for bid, bdata in blocks.items():
        desc = bdata.get('Description', '')
        if 'Default' in desc or 'Trash' in desc:
            orphans = [e['QuestionID'] for e in bdata.get('BlockElements', [])
                       if e.get('Type') == 'Question']
            check(f"No orphaned questions in '{desc}'", len(orphans) == 0,
                  f"Found: {orphans}")

    # --- Summary ---
    print(f"\n{'='*50}")
    print(f"VERIFICATION: {passed} passed, {failed} failed")
    print(f"{'='*50}")
    if failed == 0:
        print("ALL CHECKS PASSED - Survey is ready for preview/activation")
    else:
        print(f"ATTENTION: {failed} check(s) need review before publishing")

    return passed, failed, details

# Usage:
# verify_survey(SID, expected_blocks=6, open_ended_qids=["QID10", "QID17"])
```

---

## Quick Reference Card

### API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/surveys` | List all surveys |
| GET | `/survey-definitions/{sid}` | Full survey definition (blocks, questions, flow) |
| GET | `/survey-definitions/{sid}?format=qsf` | Export as QSF file |
| GET | `/survey-definitions/{sid}/options` | Survey options (language, skin, etc.) |
| GET | `/survey-definitions/{sid}/questions/{qid}` | Single question definition |
| PUT | `/surveys/{sid}` | Update survey name in project list |
| PUT | `/survey-definitions/{sid}/options` | Update survey options |
| PUT | `/survey-definitions/{sid}/questions/{qid}` | **FULL REPLACE** question |
| PUT | `/survey-definitions/{sid}/blocks/{bid}` | Update block |
| PUT | `/survey-definitions/{sid}/flow` | Update survey flow |
| POST | `/surveys` | Import QSF (multipart/form-data) |
| POST | `/survey-definitions/{sid}/questions` | Create new question |
| POST | `/survey-definitions/{sid}/blocks` | Create new block |

### Read-Only Fields (Strip Before PUT)

`QuestionID`, `Language`, `QuestionText_Unsafe`, `NextChoiceId`, `NextAnswerId`

### Question Type Codes

| Code | Selector | Description |
|------|----------|-------------|
| MC / SAVR | Single Answer Vertical Radio | Single-choice radio buttons |
| MC / MAVR | Multiple Answer Vertical Radio | Multi-select checkboxes |
| TE / SL | Single Line | Short text input |
| TE / ML | Multi Line | Long text / open-ended |
| Matrix / Likert | Likert scale | Rows x Columns rating grid |
| DB / TB | Text Block | Descriptive text (no response) |

### Common HTTP Errors

| Code | Meaning | Recovery |
|------|---------|----------|
| 400 | Bad request (malformed JSON, missing required fields) | Check JSON structure, ensure all required fields present |
| 401 | Invalid API token | Check that QUALTRICS_API_KEY (and QUALTRICS_BASE_URL) are set and valid |
| 403 | Insufficient permissions | Check API token scope |
| 404 | Survey/question/block not found | Verify ID, re-fetch survey |
| 413 | Payload too large | Split into smaller operations |
| 429 | Rate limited | Wait 60 seconds, retry |
| 500 | Server error | Retry after 30 seconds; if persistent, check Qualtrics status page |

### Hebrew RTL Wrapping

All Hebrew text in QuestionText and Choice Display values should be wrapped:
```html
<div dir="rtl" style="text-align: right;">טקסט בעברית כאן</div>
```

### Preview URL Pattern
```
https://{base_url}/jfe/preview/{SID}
```
Example: `https://yourorg.eu.qualtrics.com/jfe/preview/SV_XXXXXXXXXXXXXXX`
