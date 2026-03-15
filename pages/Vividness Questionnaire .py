import csv
import io
from datetime import datetime

import streamlit as st

st.set_page_config(page_title="VVIQ Questionnaire", page_icon="🧠", layout="centered")

# Standard VVIQ 16 items from David Marks' published description
# Source basis: official VVIQ item list
QUESTIONS = [
    "Think of some relative or friend whom you frequently see (but who is not with you at present). The exact contour of face, head, shoulders, and body.",
    "Think of some relative or friend whom you frequently see (but who is not with you at present). Characteristic poses of head, attitudes of body, etc.",
    "Think of some relative or friend whom you frequently see (but who is not with you at present). The precise carriage, length of step, etc. in walking.",
    "Think of some relative or friend whom you frequently see (but who is not with you at present). The different colors worn in some familiar clothes.",

    "Visualize a rising sun. The sun is rising above the horizon into a hazy sky.",
    "Visualize a rising sun. The sky clears and surrounds the sun with blueness.",
    "Visualize a rising sun. Clouds. A storm blows up, with flashes of lightning.",
    "Visualize a rising sun. A rainbow appears.",

    "Think of the front of a shop which you often go to. The overall appearance of the shop from the opposite side of the road.",
    "Think of the front of a shop which you often go to. A window display including colors, shape, and details of individual items for sale.",
    "Think of the front of a shop which you often go to. You are near the entrance. The color, shape, and details of the door.",
    "Think of the front of a shop which you often go to. You enter the shop and go to the counter. The counter assistant serves you. Money changes hands.",

    "Think of a country scene which involves trees, mountains, and a lake. The contours of the landscape.",
    "Think of a country scene which involves trees, mountains, and a lake. The color and shape of the trees.",
    "Think of a country scene which involves trees, mountains, and a lake. The color and shape of the lake.",
    "Think of a country scene which involves trees, mountains, and a lake. A strong wind blows on the trees and on the lake causing waves.",
]

# Original-style VVIQ scoring direction:
# 1 = vivid, 5 = no image
OPTIONS = {
    1: "1 - Perfectly clear and as vivid as normal vision",
    2: "2 - Clear and reasonably vivid",
    3: "3 - Moderately clear and vivid",
    4: "4 - Vague and dim",
    5: "5 - No image at all, you only 'know' that you are thinking of it",
}

TOTAL_QUESTIONS = len(QUESTIONS)
VVIQ_CURRENT_Q_KEY = "vviq_current_q"
VVIQ_RESPONSES_KEY = "vviq_responses"
VVIQ_PARTICIPANT_NAME_KEY = "vviq_participant_name"


def init_state():
    if VVIQ_CURRENT_Q_KEY not in st.session_state:
        st.session_state[VVIQ_CURRENT_Q_KEY] = 0

    if (
        VVIQ_RESPONSES_KEY not in st.session_state
        or not isinstance(st.session_state[VVIQ_RESPONSES_KEY], dict)
    ):
        st.session_state[VVIQ_RESPONSES_KEY] = {}

    if VVIQ_PARTICIPANT_NAME_KEY not in st.session_state:
        st.session_state[VVIQ_PARTICIPANT_NAME_KEY] = ""


def compute_total_score(responses: dict) -> int:
    return sum(int(responses.get(i, 0)) for i in range(1, TOTAL_QUESTIONS + 1))


def score_label(total_score: int) -> str:
    # Lower score = more vivid imagery, higher score = less vivid imagery
    # This is a rough descriptive band, not a diagnosis
    if total_score <= 24:
        return "Very vivid imagery"
    elif total_score <= 40:
        return "Moderately vivid imagery"
    elif total_score <= 56:
        return "Low imagery vividness"
    else:
        return "Very low imagery vividness"


def make_csv_bytes(participant_name: str, responses: dict) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)

    header = (
        ["participant_name", "timestamp_utc", "total_score", "result_label"]
        + [f"q{i}" for i in range(1, TOTAL_QUESTIONS + 1)]
    )

    total_score = compute_total_score(responses)
    label = score_label(total_score)

    row = [
        participant_name,
        datetime.utcnow().isoformat(timespec="seconds") + "Z",
        total_score,
        label,
    ] + [responses.get(i, "") for i in range(1, TOTAL_QUESTIONS + 1)]

    writer.writerow(header)
    writer.writerow(row)

    return output.getvalue().encode("utf-8")


def reset_all():
    st.session_state[VVIQ_CURRENT_Q_KEY] = 0
    st.session_state[VVIQ_RESPONSES_KEY] = {}
    st.session_state[VVIQ_PARTICIPANT_NAME_KEY] = ""


init_state()

st.title("VVIQ Questionnaire")

st.markdown(
    """
This questionnaire asks how vivid your mental imagery is.

For each item, select one response:

- **1** = perfectly clear and as vivid as normal vision
- **5** = no image at all

Please answer based on your immediate impression.
"""
)

current_q = st.session_state[VVIQ_CURRENT_Q_KEY]
responses = st.session_state[VVIQ_RESPONSES_KEY]

if current_q < TOTAL_QUESTIONS:
    q_num = current_q + 1
    question_text = QUESTIONS[current_q]
    current_answer = responses.get(q_num, 3)

    st.progress(q_num / TOTAL_QUESTIONS)
    st.subheader(f"Question {q_num} of {TOTAL_QUESTIONS}")
    st.write(question_text)

    with st.form(key=f"question_form_{q_num}"):
        answer = st.radio(
            "Select one option",
            options=list(OPTIONS.keys()),
            format_func=lambda x: OPTIONS[x],
            index=list(OPTIONS.keys()).index(current_answer),
        )

        col1, col2 = st.columns(2)

        with col1:
            prev_clicked = st.form_submit_button("Previous", disabled=(current_q == 0))

        with col2:
            next_clicked = st.form_submit_button(
                "Finish" if q_num == TOTAL_QUESTIONS else "Next"
            )

    if prev_clicked:
        responses[q_num] = answer
        st.session_state[VVIQ_CURRENT_Q_KEY] = max(0, current_q - 1)
        st.rerun()

    if next_clicked:
        responses[q_num] = answer
        st.session_state[VVIQ_CURRENT_Q_KEY] = current_q + 1
        st.rerun()

else:
    total_score = compute_total_score(responses)
    label = score_label(total_score)
    participant_name = st.session_state[VVIQ_PARTICIPANT_NAME_KEY].strip()

    st.success("Questionnaire completed.")
    # st.subheader("Result")
    # st.write(f"**Total score:** {total_score} / 80")
    # st.write(f"**Interpretation:** {label}")

    # st.caption(
    #     "Lower scores indicate more vivid imagery; higher scores indicate less vivid imagery."
    # )

    if not participant_name:
        st.subheader("Participant details")
        participant_name = st.text_input(
            "Participant name",
            key="vviq_participant_name_input",
        ).strip()
        st.session_state[VVIQ_PARTICIPANT_NAME_KEY] = participant_name
    else:
        st.subheader("Participant")
        st.write(participant_name)

    if participant_name:
        summary_rows = []
        for i, q in enumerate(QUESTIONS, start=1):
            summary_rows.append(
                {
                    "question_number": i,
                    "response": responses.get(i, ""),
                    "question": q,
                }
            )

        st.subheader("Response summary")
        st.dataframe(summary_rows, use_container_width=True)

        csv_bytes = make_csv_bytes(
            participant_name=participant_name,
            responses=responses,
        )

        safe_name = "_".join(participant_name.split())
        filename = f"{safe_name}_vviq_responses.csv"

        st.download_button(
            label="Download CSV",
            data=csv_bytes,
            file_name=filename,
            mime="text/csv",
        )
    else:
        st.info("Enter the participant name to enable the CSV download.")

    if st.button("Start over"):
        reset_all()
        st.rerun()
