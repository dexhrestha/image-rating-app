import json
from datetime import datetime

import streamlit as st

st.set_page_config(
    page_title="Post-Experiment Questions",
    page_icon=":memo:",
    layout="centered",
)

QUESTIONS = [
    {
        "id": "animal_order",
        "prompt": "What animals were there. Order them according to the sequence you saw in the experiment?",
        "type": "text_area",
        "help": "List the animals in order, for example: dog, cat, horse.",
    },
    {
        "id": "animal_counts",
        "prompt": "How many individual animals were there for each animal?",
        "type": "text_area",
        "help": "Describe the count for each animal, for example: dog: 3, cat: 2.",
    },
    {
        "id": "most_accurate_speed",
        "prompt": "Which speed were you most accurate in?",
        "type": "text_input",
        "help": "Enter the speed condition that felt most accurate.",
    },
    {
        "id": "strategy",
        "prompt": "Did you use any particular strategy?",
        "type": "text_area",
        "help": "Briefly describe any strategy you used. If none, write 'No'.",
    },
    {
        "id": "used_counting",
        "prompt": "Did you use counting?",
        "type": "radio",
        "options": ["Yes", "No"],
    },
    {
        "id": "used_body_movement",
        "prompt": "Did you use systematic movement of your body (toes, foot, finger) to keep track of the rhythm?",
        "type": "radio",
        "options": ["Yes", "No"],
    },
]

TOTAL_QUESTIONS = len(QUESTIONS)
CURRENT_Q_KEY = "post_experiment_current_q"
RESPONSES_KEY = "post_experiment_responses"
PARTICIPANT_NAME_KEY = "post_experiment_participant_name"


def init_state() -> None:
    if CURRENT_Q_KEY not in st.session_state:
        st.session_state[CURRENT_Q_KEY] = 0

    if RESPONSES_KEY not in st.session_state or not isinstance(
        st.session_state[RESPONSES_KEY], dict
    ):
        st.session_state[RESPONSES_KEY] = {}

    if PARTICIPANT_NAME_KEY not in st.session_state:
        st.session_state[PARTICIPANT_NAME_KEY] = ""


def reset_all() -> None:
    st.session_state[CURRENT_Q_KEY] = 0
    st.session_state[RESPONSES_KEY] = {}
    st.session_state[PARTICIPANT_NAME_KEY] = ""


def make_json_bytes(participant_name: str, responses: dict[str, str]) -> bytes:
    payload = {
        "participant_name": participant_name,
        "timestamp_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "responses": {
            question["id"]: {
                "question": question["prompt"],
                "answer": responses.get(question["id"], ""),
            }
            for question in QUESTIONS
        },
    }
    return json.dumps(payload, indent=2).encode("utf-8")


init_state()

st.title("Post-Experiment Questions")
st.markdown(
    """
Please answer the following questions about your experience in the experiment.

- You will see **one question at a time**
- Use **Next** and **Previous** to move between questions
- At the end, enter the **participant name or ID** to download the responses as a JSON file
"""
)

current_q = st.session_state[CURRENT_Q_KEY]
responses = st.session_state[RESPONSES_KEY]

if current_q < TOTAL_QUESTIONS:
    question = QUESTIONS[current_q]
    question_id = question["id"]
    question_prompt = question["prompt"]
    question_type = question["type"]
    saved_answer = responses.get(question_id, "")

    st.progress((current_q + 1) / TOTAL_QUESTIONS)
    st.subheader(f"Question {current_q + 1} of {TOTAL_QUESTIONS}")
    st.write(question_prompt)

    with st.form(key=f"post_experiment_form_{question_id}"):
        if question_type == "text_area":
            answer = st.text_area(
                "Your answer",
                value=saved_answer,
                help=question.get("help"),
                height=160,
            )
        elif question_type == "text_input":
            answer = st.text_input(
                "Your answer",
                value=saved_answer,
                help=question.get("help"),
            )
        else:
            options = question["options"]
            default_index = options.index(saved_answer) if saved_answer in options else 0
            answer = st.radio(
                "Select one option",
                options=options,
                index=default_index,
            )

        col1, col2 = st.columns(2)
        with col1:
            prev_clicked = st.form_submit_button("Previous", disabled=(current_q == 0))
        with col2:
            next_clicked = st.form_submit_button(
                "Finish" if current_q == TOTAL_QUESTIONS - 1 else "Next"
            )

    if prev_clicked:
        responses[question_id] = answer
        st.session_state[CURRENT_Q_KEY] = max(0, current_q - 1)
        st.rerun()

    if next_clicked:
        responses[question_id] = answer
        st.session_state[CURRENT_Q_KEY] = current_q + 1
        st.rerun()

else:
    participant_name = st.session_state[PARTICIPANT_NAME_KEY].strip()
    st.success("All questions completed.")

    if not participant_name:
        st.subheader("Participant details")
        participant_name = st.text_input(
            "Participant name or ID",
            key="post_experiment_participant_name_input",
        ).strip()
        st.session_state[PARTICIPANT_NAME_KEY] = participant_name
    else:
        st.subheader("Participant")
        st.write(participant_name)

    summary_rows = [
        {
            "question_number": index,
            "question": question["prompt"],
            "response": responses.get(question["id"], ""),
        }
        for index, question in enumerate(QUESTIONS, start=1)
    ]

    st.subheader("Response Summary")
    st.dataframe(summary_rows, use_container_width=True)

    if participant_name:
        json_bytes = make_json_bytes(participant_name, responses)
        safe_name = "_".join(participant_name.split())

        st.download_button(
            label="Download responses as JSON",
            data=json_bytes,
            file_name=f"{safe_name}_post_experiment_responses.json",
            mime="application/json",
        )
    else:
        st.info("Enter the participant name or ID to enable the JSON download.")

    if st.button("Start over"):
        reset_all()
        st.rerun()
