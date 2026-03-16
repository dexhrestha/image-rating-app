import csv
import io
from datetime import datetime

import streamlit as st

st.set_page_config(page_title="Imagery Questionnaire", page_icon="📝")

QUESTIONS = [
    "When I go to a new place, I prefer directions that contain detailed descriptions of landmarks (such as the size, shape, and color of a gas station) alongside the names of those landmarks.",
    "When I catch a glimpse of a car that is partially hidden behind bushes, I automatically “complete” the car by visualizing the car in its entirety in my head.",
    "When I am looking for new furniture in a store, I always imagine how the furniture would look in certain places in my house.",
    "I prefer to read novels that easily lead me to imagine where the characters are and what they are doing, rather than novels that are difficult to visualize.",
    "When I think of visiting a family member, I almost always have a clear mental image of him or her.",
    "When relatively simple technical material is clearly described in a text, I find illustrations distracting because they interfere with my ability to visualize the material.",
    "If someone were to ask me to add up two-digit numbers (e.g., 24 and 31), I would visualize them, which helps me add the numbers afterward.",
    "Before I get dressed to go out, I first imagine what I will look like when I wear the different outfits.",
    "When I think about a series of errands I need to run, I imagine the shops I am going to visit.",
    "When I first hear a friend's voice, a visual image of him or her almost always comes into my head.",
    "When I hear a radio announcer or a DJ whom I have never seen in real life, I usually imagine what they would look like.",
    "If I were to see a car accident, I would imagine what happened when I try to remember the details later.",
]

OPTIONS = {
    1: "1 - Never applies",
    2: "2",
    3: "3 - Applies about half the time",
    4: "4",
    5: "5 - Always fully applicable",
}

QUESTIONNAIRE_RESPONSES_KEY = "imagery_questionnaire_responses"
QUESTIONNAIRE_CURRENT_Q_KEY = "imagery_questionnaire_current_q"
QUESTIONNAIRE_PARTICIPANT_NAME_KEY = "imagery_questionnaire_participant_name"


def init_state():
    if QUESTIONNAIRE_CURRENT_Q_KEY not in st.session_state:
        st.session_state[QUESTIONNAIRE_CURRENT_Q_KEY] = 0
    if (
        QUESTIONNAIRE_RESPONSES_KEY not in st.session_state
        or not isinstance(st.session_state[QUESTIONNAIRE_RESPONSES_KEY], dict)
    ):
        st.session_state[QUESTIONNAIRE_RESPONSES_KEY] = {}
    if QUESTIONNAIRE_PARTICIPANT_NAME_KEY not in st.session_state:
        st.session_state[QUESTIONNAIRE_PARTICIPANT_NAME_KEY] = ""


def make_csv_bytes(participant_name: str, responses: dict[int, int]) -> bytes:
    output = io.StringIO()
    writer = csv.writer(output)

    header = ["participant_name", "timestamp"] + [f"q{i}" for i in range(1, len(QUESTIONS) + 1)]
    row = [
        participant_name,
        datetime.utcnow().isoformat(timespec="seconds") + "Z",
    ] + [responses.get(i, "") for i in range(1, len(QUESTIONS) + 1)]

    writer.writerow(header)
    writer.writerow(row)

    return output.getvalue().encode("utf-8")


init_state()

st.title("Imagery Questionnaire")
st.markdown(
    """
Rate each statement from **1** to **5**:

- **1** = never applies
- **3** = applies about half the time
- **5** = always fully applicable
"""
)

total_questions = len(QUESTIONS)
current_q = st.session_state[QUESTIONNAIRE_CURRENT_Q_KEY]
responses = st.session_state[QUESTIONNAIRE_RESPONSES_KEY]

if current_q < total_questions:
    q_num = current_q + 1
    question_text = QUESTIONS[current_q]

    st.progress(q_num / total_questions)
    st.subheader(f"Question {q_num} of {total_questions}")
    st.write(question_text)

    current_answer = responses.get(q_num, 3)

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
            next_label = "Finish" if q_num == total_questions else "Next"
            next_clicked = st.form_submit_button(next_label)

    if prev_clicked:
        responses[q_num] = answer
        st.session_state[QUESTIONNAIRE_CURRENT_Q_KEY] = max(0, current_q - 1)
        st.rerun()

    if next_clicked:
        responses[q_num] = answer
        st.session_state[QUESTIONNAIRE_CURRENT_Q_KEY] = current_q + 1
        st.rerun()

else:
    st.success("All questions completed.")
    participant_name = st.session_state[QUESTIONNAIRE_PARTICIPANT_NAME_KEY].strip()

    if not participant_name:
        st.subheader("Enter participant name")
        participant_name = st.text_input(
            "Participant name",
            key="imagery_questionnaire_participant_name_input",
        ).strip()
        st.session_state[QUESTIONNAIRE_PARTICIPANT_NAME_KEY] = participant_name
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

        st.subheader("Response Summary")
        st.dataframe(summary_rows, use_container_width=True)

        csv_bytes = make_csv_bytes(
            participant_name=participant_name,
            responses=responses,
        )

        safe_name = "_".join(participant_name.split())
        filename = f"{safe_name}_imagery_questionnaire_responses.csv"

        st.download_button(
            label="Download responses as CSV",
            data=csv_bytes,
            file_name=filename,
            mime="text/csv",
        )
    else:
        st.info("Enter the participant name to enable CSV download.")

    if st.button("Start over"):
        st.session_state[QUESTIONNAIRE_CURRENT_Q_KEY] = 0
        st.session_state[QUESTIONNAIRE_RESPONSES_KEY] = {}
        st.session_state[QUESTIONNAIRE_PARTICIPANT_NAME_KEY] = ""
        st.rerun()
