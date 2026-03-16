import streamlit as st

st.set_page_config(
    page_title="Post-Experiment Survey",
    page_icon=":clipboard:",
    layout="wide",
)

st.title("Post-Experiment Survey")
st.caption(
    "Use this survey space to collect participants' responses immediately after the experimental task."
)

hero_left, hero_right = st.columns([2, 1], gap="large")

with hero_left:
    st.markdown(
        """
This application is designed for the **post-experiment assessment phase**.
Participants should complete the pages in the sidebar after they finish the main task.

The survey focuses on three areas:

- **Immediate image-based ratings** of what participants can mentally recall
- **General imagery habits** in everyday situations
- **Self-reported vividness of visual imagery** across standard questionnaire items

Encourage participants to answer based on their **first impression**, without overthinking.
The goal is to capture their subjective experience as accurately as possible.
"""
    )

with hero_right:
    st.info(
        """
**Recommended order**

1. Image Rating
2. Imagery Questionnaire
3. VVIQ Questionnaire
"""
    )

st.divider()

overview_col, scale_col = st.columns(2, gap="large")

with overview_col:
    st.subheader("Survey Overview")
    st.markdown(
        """
Each page in the sidebar serves a different purpose:

**Image Rating**
Participants briefly view an image, then rate how vividly they can recall it and how easy it is to imagine.
This page is useful for trial-level responses tied directly to recently presented stimuli.

**Imagery Questionnaire**
Participants respond to statements about how often imagery helps them in daily life.
This captures broader tendencies in spontaneous visual thinking.

**VVIQ Questionnaire**
Participants rate the clarity of imagined scenes and objects using a standard vividness framework.
This provides a more structured measure of visual imagery vividness.
"""
    )

with scale_col:
    st.subheader("How To Administer")
    st.markdown(
        """
- Ask participants to complete the survey **immediately after the experiment**.
- Remind them there are **no right or wrong answers**.
- Encourage quiet, focused responding without discussion.
- Have them enter a **participant name or ID** at the end of each page so responses can be downloaded.
- Download the CSV file from each page after completion.

If the participant loses their place, they can return using the sidebar and continue from the current page state.
"""
    )

st.divider()

st.subheader("Response Guidance")

guide_col1, guide_col2, guide_col3 = st.columns(3, gap="large")

with guide_col1:
    st.markdown(
        """
**For vividness ratings**

Participants should rate how clear, detailed, and image-like the mental picture feels.
Higher vividness means the image feels more present and easier to inspect mentally.
"""
    )

with guide_col2:
    st.markdown(
        """
**For ease ratings**

Participants should judge how effortless it is to generate or hold the image in mind.
This is about mental effort, not whether they liked the image.
"""
    )

with guide_col3:
    st.markdown(
        """
**For questionnaire items**

Participants should rely on their typical experience in everyday life.
They should choose the option that best fits overall, even if no answer feels perfect.
"""
    )

st.divider()

notes_col, checklist_col = st.columns([3, 2], gap="large")

with notes_col:
    st.subheader("Research Notes")
    st.markdown(
        """
This homepage can be shown to the researcher or the participant before the survey begins.
It provides a consistent explanation of the post-experiment phase and helps standardize administration.

All survey pages are structured to:

- present one response step at a time,
- keep progress visible,
- store responses during the session, and
- allow CSV export once the page is completed.

"""
    )

with checklist_col:
    st.subheader("Before Starting")
    st.markdown(
        """
- Confirm the experiment is finished
- Open the first survey page from the sidebar
- Make sure the participant understands the rating scales
- Ask them to complete every item
- Save the downloaded CSV files at the end
"""
    )

st.success(
    "When ready, select a survey page from the sidebar to begin the post-experiment questionnaire."
)
