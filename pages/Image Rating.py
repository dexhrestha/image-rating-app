import os
import random
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Image Rating Task", layout="centered")

ANIMALS_DIR = "animals"
IMAGE_RATING_RESPONSES_KEY = "image_rating_responses"
PARTICIPANT_NAME_KEY = "image_rating_participant_name"
IMAGE_INDEX_KEY = "image_rating_image_index"
STEP_KEY = "image_rating_step"
IMAGE_PATHS_KEY = "image_rating_image_paths"
CURRENT_VIVIDNESS_KEY = "image_rating_current_vividness"


def build_image_paths(base_dir: str) -> list[str]:
    """Collect all file paths under base_dir/<animal>/*, skipping non-files."""
    paths: list[str] = []
    if not os.path.isdir(base_dir):
        return paths

    for animal in os.listdir(base_dir):
        animal_path = os.path.join(base_dir, animal)
        if not os.path.isdir(animal_path):
            continue

        for filename in os.listdir(animal_path):
            file_path = os.path.join(animal_path, filename)
            if os.path.isfile(file_path):
                paths.append(file_path)

    return list(dict.fromkeys(paths))


def init_state() -> None:
    defaults = {
        IMAGE_INDEX_KEY: 0,
        STEP_KEY: 0,  # 0=image, 1=vividness, 2=ease
        IMAGE_RATING_RESPONSES_KEY: [],
        IMAGE_PATHS_KEY: [],
        CURRENT_VIVIDNESS_KEY: None,
        PARTICIPANT_NAME_KEY: "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if not isinstance(st.session_state[IMAGE_RATING_RESPONSES_KEY], list):
        st.session_state[IMAGE_RATING_RESPONSES_KEY] = []


def init_or_refresh_image_paths(shuffle: bool = True) -> None:
    st.session_state[IMAGE_PATHS_KEY] = build_image_paths(ANIMALS_DIR)
    if shuffle:
        random.shuffle(st.session_state[IMAGE_PATHS_KEY])


def next_step() -> None:
    st.session_state[STEP_KEY] += 1
    st.rerun()


def next_image() -> None:
    st.session_state[IMAGE_INDEX_KEY] += 1
    st.session_state[STEP_KEY] = 0
    st.session_state[CURRENT_VIVIDNESS_KEY] = None
    st.rerun()


def reset_all() -> None:
    st.session_state[IMAGE_INDEX_KEY] = 0
    st.session_state[STEP_KEY] = 0
    st.session_state[IMAGE_RATING_RESPONSES_KEY] = []
    st.session_state[CURRENT_VIVIDNESS_KEY] = None
    st.session_state[PARTICIPANT_NAME_KEY] = ""
    init_or_refresh_image_paths(shuffle=True)
    st.rerun()


def build_download_df(participant_name: str) -> pd.DataFrame:
    df = pd.DataFrame(st.session_state[IMAGE_RATING_RESPONSES_KEY])

    if df.empty:
        return df

    df.insert(0, "participant_name", participant_name)
    df.insert(1, "timestamp", datetime.utcnow().isoformat(timespec="seconds") + "Z")
    df["image"] = df["image"].astype(str)
    df["filename"] = df["image"]
    df["image"] = df["image"].str.rsplit(".", n=1).str[0]
    return df


init_state()
if not st.session_state[IMAGE_PATHS_KEY]:
    init_or_refresh_image_paths(shuffle=True)

st.title("Image Imagery Rating")
st.markdown(
    """
You will see a picture of an animal on the screen.

- Look at the image carefully.
- Press **Next** and try to imagine the image.
- Rate how vivid it feels and how easy it is to imagine.
"""
)

image_paths = st.session_state[IMAGE_PATHS_KEY]
total_images = len(image_paths)

if total_images == 0:
    st.error(f"No images found under '{ANIMALS_DIR}/<animal>/*'.")
    if st.button("Restart"):
        reset_all()
    st.stop()

if st.session_state[IMAGE_INDEX_KEY] < total_images:
    q_num = st.session_state[IMAGE_INDEX_KEY] + 1
    current_image_path = image_paths[st.session_state[IMAGE_INDEX_KEY]]
    current_image_name = os.path.basename(current_image_path)

    st.progress(q_num / total_images)
    st.subheader(f"Image {q_num} of {total_images}")

    if st.session_state[STEP_KEY] == 0:
        next_col, _ = st.columns([1, 3])
        with next_col:
            next_clicked = st.button("Next", key=f"show_image_next_{st.session_state[IMAGE_INDEX_KEY]}")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(current_image_path, width=300)

        st.caption("Press Next to answer questions about this image.")
        if next_clicked:
            next_step()

    elif st.session_state[STEP_KEY] == 1:
        next_col, _ = st.columns([1, 3])
        with next_col:
            next_clicked = st.button("Next", key=f"vividness_next_{st.session_state[IMAGE_INDEX_KEY]}")

        st.markdown(
            "Close your eyes and try to recall the image. "
            "How vivid does it feel in your mind right now?"
        )

        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            st.write("Not vivid at all")

        with col2:
            vividness = st.radio(
                "Vividness",
                options=list(range(1, 8)),
                horizontal=True,
                label_visibility="collapsed",
                key=f"vividness_{st.session_state[IMAGE_INDEX_KEY]}",
            )

        with col3:
            st.write("Extremely vivid")

        if next_clicked:
            st.session_state[CURRENT_VIVIDNESS_KEY] = vividness
            next_step()

    elif st.session_state[STEP_KEY] == 2:
        submit_col, _ = st.columns([1, 3])
        submit_label = "Finish" if q_num == total_images else "Submit"
        with submit_col:
            submit_clicked = st.button(
                submit_label,
                key=f"ease_submit_{st.session_state[IMAGE_INDEX_KEY]}",
            )

        st.markdown("How easy is it to imagine this image?")

        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            st.write("Extremely easy")

        with col2:
            easy_to_imagine = st.radio(
                "Ease",
                options=list(range(1, 8)),
                horizontal=True,
                label_visibility="collapsed",
                key=f"ease_{st.session_state[IMAGE_INDEX_KEY]}",
            )

        with col3:
            st.write("Extremely difficult")

        if submit_clicked:
            st.session_state[IMAGE_RATING_RESPONSES_KEY].append(
                {
                    "image": current_image_name,
                    "vividness": st.session_state[CURRENT_VIVIDNESS_KEY],
                    "easy_to_imagine": easy_to_imagine,
                }
            )
            next_image()

else:
    st.success("All images completed.")
    participant_name = st.session_state[PARTICIPANT_NAME_KEY].strip()

    if not participant_name:
        st.subheader("Enter participant name")
        participant_name = st.text_input(
            "Participant name",
            key="image_rating_participant_name_input",
        ).strip()
        st.session_state[PARTICIPANT_NAME_KEY] = participant_name
    else:
        st.subheader("Participant")
        st.write(participant_name)

    if participant_name:
        df = build_download_df(participant_name)

        st.subheader("Response Summary")
        st.dataframe(df, use_container_width=True)

        safe_name = "_".join(participant_name.split())
        st.download_button(
            label="Download responses as CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"{safe_name}_image_rating_responses.csv",
            mime="text/csv",
        )
    else:
        st.info("Enter the participant name to enable CSV download.")

    if st.button("Start over"):
        reset_all()
