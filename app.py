import os
import json
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

APP_TITLE = "AI-Powered Automation Assistant"
EXCEL_FILE = "data/automation_log.xlsx"
DEFAULT_MODEL = "openai/gpt-oss-20b"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# GROQ CONFIGURATION
# ============================================================

api_key = os.getenv("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")
model = os.getenv("GROQ_MODEL", DEFAULT_MODEL)

if not api_key:
    st.error("Groq API key was not found.")
    st.info("Create a .env file and add your Groq API key.")
    st.code("GROQ_API_KEY=your_api_key_here")
    st.stop()

client = Groq(api_key=api_key)


# ============================================================
# AI SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are a professional business automation assistant.

Analyze the incoming business email or message.

Return ONLY valid JSON using exactly these fields:

category
priority
department
summary
suggested_action
suggested_reply

Rules:

- priority must be Low, Medium, or High
- category should describe the type of request
- department should identify the likely responsible department
- summary should be concise
- suggested_action should be a practical next step
- suggested_reply should be professional and ready for human review
- Do not invent confidential company information
"""


# ============================================================
# GROQ AI FUNCTION
# ============================================================

def analyze_with_groq(message):

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": message
            }
        ],
        temperature=0.2,
        max_completion_tokens=1000
    )

    content = response.choices[0].message.content.strip()

    # Remove Markdown code fences if returned by the model
    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    return json.loads(content)


# ============================================================
# SAVE TO EXCEL
# ============================================================

def save_to_excel(message, result):

    os.makedirs("data", exist_ok=True)

    new_record = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Original Message": message,
        "Category": result.get("category", ""),
        "Priority": result.get("priority", ""),
        "Department": result.get("department", ""),
        "Summary": result.get("summary", ""),
        "Suggested Action": result.get("suggested_action", ""),
        "Suggested Reply": result.get("suggested_reply", "")
    }

    if os.path.exists(EXCEL_FILE):

        df = pd.read_excel(EXCEL_FILE)

        df = pd.concat(
            [
                df,
                pd.DataFrame([new_record])
            ],
            ignore_index=True
        )

    else:

        df = pd.DataFrame([new_record])

    df.to_excel(
        EXCEL_FILE,
        index=False
    )


# ============================================================
# USER INTERFACE
# ============================================================

st.title("🤖 AI-Powered Automation Assistant")

st.caption(
    "Python + Groq API + AI Classification + Automated Response + Excel"
)

st.divider()


sample_message = """Hello Team,

We need a meeting to discuss the cybersecurity assessment scheduled
for next week.

Please confirm your availability and let us know what information
should be prepared before the meeting.

Regards,
Operations Team
"""


message = st.text_area(
    "📩 Enter Email / Business Message",
    value=sample_message,
    height=220
)


# ============================================================
# AUTOMATION BUTTON
# ============================================================

if st.button(
    "🚀 Analyze & Automate",
    type="primary",
    use_container_width=True
):

    if not message.strip():

        st.warning(
            "Please enter an email or business message."
        )

    else:

        try:

            with st.spinner(
                "Groq AI is analyzing the message..."
            ):

                result = analyze_with_groq(message)

                save_to_excel(
                    message,
                    result
                )

            st.success(
                "Automation completed successfully!"
            )

            # ------------------------------------------------
            # AI CLASSIFICATION
            # ------------------------------------------------

            st.subheader("📊 AI Classification")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Category",
                    result.get("category", "")
                )

            with col2:
                st.metric(
                    "Priority",
                    result.get("priority", "")
                )

            with col3:
                st.metric(
                    "Department",
                    result.get("department", "")
                )

            # ------------------------------------------------
            # SUMMARY
            # ------------------------------------------------

            st.subheader("📝 Summary")

            st.write(
                result.get("summary", "")
            )

            # ------------------------------------------------
            # ACTION
            # ------------------------------------------------

            st.subheader("⚙️ Suggested Action")

            st.write(
                result.get("suggested_action", "")
            )

            # ------------------------------------------------
            # RESPONSE
            # ------------------------------------------------

            st.subheader("✉️ AI Generated Response")

            st.info(
                result.get("suggested_reply", "")
            )

        except json.JSONDecodeError:

            st.error(
                "Groq returned an invalid JSON response. Please try again."
            )

        except Exception as error:

            st.error(
                f"Automation error: {error}"
            )


# ============================================================
# EXCEL LOG
# ============================================================

st.divider()

st.subheader("📁 Automation Log")

if os.path.exists(EXCEL_FILE):

    df = pd.read_excel(
        EXCEL_FILE
    )

    st.dataframe(
        df,
        use_container_width=True
    )

    with open(
        EXCEL_FILE,
        "rb"
    ) as file:

        st.download_button(
            "📥 Download Excel Log",
            file,
            file_name="automation_log.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:

    st.info(
        "No automation records yet."
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ AI Configuration")

    st.write(
        f"**Groq Model:** `{model}`"
    )

    st.write(
        "**Framework:** Streamlit"
    )

    st.write(
        "**Language:** Python"
    )

    st.write(
        "**Output:** Excel"
    )

    st.divider()

    st.markdown(
        """
### 🔄 Workflow

**1.** User Input / Email

↓

**2.** Python Application

↓

**3.** Groq LLM

↓

**4.** Classify & Analyze

↓

**5.** Generate Response

↓

**6.** Save to Excel
"""
    )