import streamlit as st
import os
import hashlib
import random
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Image Rating Task", layout="centered")

ANIMALS_DIR = "animals"


# -----------------------------
# HELPERS
# -----------------------------
def build_image_paths(base_dir: str) -> list[str]:
    """Collect all file paths under base_dir/<animal>/*, skipping non-files."""
    paths: list[str] = []
    if not os.path.isdir(base_dir):
        return paths

    for animal in os.listdir(base_dir):
        animal_path = os.path.join(base_dir, animal)
        if not os.path.isdir(animal_path):
            continue

        for f in os.listdir(animal_path):
            fp = os.path.join(animal_path, f)
            if os.path.isfile(fp):
                paths.append(fp)

    # Optional: dedupe while preserving order (just in case)
    paths = list(dict.fromkeys(paths))
    return paths


# -----------------------------
# SESSION STATE INIT
# -----------------------------
defaults = {
    "page": "login",
    "username": "",
    "image_index": 0,
    "step": 0,  # 0=image, 1=Q1, 2=Q2
    "responses": [],
    "image_paths": [],
    "current_vividness": None,
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def init_or_refresh_image_paths(shuffle: bool = True) -> None:
    st.session_state.image_paths = build_image_paths(ANIMALS_DIR)
    if shuffle:
        random.shuffle(st.session_state.image_paths)


# Build + shuffle ONCE per session (prevents repeats caused by reruns)
if not st.session_state.image_paths:
    init_or_refresh_image_paths(shuffle=True)


# -----------------------------
# STATE CONTROL FUNCTIONS
# -----------------------------
def go_to_task():
    st.session_state.page = "task"
    st.session_state.image_index = 0
    st.session_state.step = 0
    st.session_state.responses = []
    st.session_state.current_vividness = None

    # New run = reshuffle once
    init_or_refresh_image_paths(shuffle=True)
    st.rerun()


def next_step():
    st.session_state.step += 1
    st.rerun()


def next_image():
    st.session_state.image_index += 1
    st.session_state.step = 0
    st.session_state.current_vividness = None
    st.rerun()


def reset_all():
    for k, v in defaults.items():
        st.session_state[k] = v
    # Re-init images after reset
    init_or_refresh_image_paths(shuffle=True)
    st.rerun()


# -----------------------------
# LOGIN PAGE
# -----------------------------
if st.session_state.page == "login":
    st.markdown(
        """
## Instructions

You will see a picture of an animal on the screen. Press the next button and close your eyes to imagine the picture.
Your task is to answer questions that follow the picture.

Once you answer all the questions you will need to download the data in csv format and send to
[dipesh.shrestha@unitn.it](mailto:dipesh.shrestha@unitn.it)

Enter your name and press start.
"""
    )

    name_input = st.text_input("Name")

    if st.button("Start", disabled=not name_input.strip()):
        random_number = random.randint(10**9, 10**10 - 1)
        raw_string = f"{name_input.strip()}_{random_number}"
        hashed_username = hashlib.sha256(raw_string.encode()).hexdigest()[:12]

        st.session_state.username = hashed_username
        go_to_task()


# -----------------------------
# TASK PAGE
# -----------------------------
elif st.session_state.page == "task":
    image_paths = st.session_state.image_paths
    total_images = len(image_paths)

    if total_images == 0:
        st.error(f"No images found under '{ANIMALS_DIR}/<animal>/*'.")
        if st.button("Restart"):
            reset_all()
        st.stop()

    if st.session_state.image_index >= total_images:
        st.success("All images completed.")
        st.write("Responses:")

        df = pd.DataFrame(st.session_state.responses)

        if not df.empty and "image" in df.columns:
            df["image"] = df["image"].astype(str)
            df["filename"] = df["image"]
            df["image"] = df["image"].str.rsplit(".", n=1).str[0]

        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download responses as CSV",
            data=csv,
            file_name=f"{st.session_state.username}_responses.csv",
            mime="text/csv",
        )

        if st.button("Restart"):
            reset_all()

    else:
        current_image_path = image_paths[st.session_state.image_index]
        current_image_name = os.path.basename(current_image_path)

        st.title("Image Imagery Rating")
        st.caption(
            f"User: {st.session_state.username} | "
            f"Image {st.session_state.image_index + 1} / {total_images}"
        )

        # -----------------------------
        # STEP 0 → Show image only
        # -----------------------------
        if st.session_state.step == 0:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(current_image_path, width=300)

            st.text("Press next to answer questions about this image.")
            if st.button("Next"):
                next_step()

        # -----------------------------
        # STEP 1 → Question 1 (Vividness)
        # -----------------------------
        elif st.session_state.step == 1:
            st.markdown(
                "## Close your eyes and try to recall the image. "
                "How vivid does it feel in your mind right now?"
            )

            col1, col2, col3 = st.columns([1, 4, 1])
            with col1:
                st.write("Not vivid at all")

            with col2:
                vividness = st.radio(
                    "",
                    options=list(range(1, 8)),
                    horizontal=True,
                    key=f"vividness_{st.session_state.image_index}",
                )

            with col3:
                st.write("Extremely vivid")

            if st.button("Next"):
                st.session_state.current_vividness = vividness
                next_step()

        # -----------------------------
        # STEP 2 → Question 2 (Ease)
        # -----------------------------
        elif st.session_state.step == 2:
            st.markdown("## How easy is it to imagine this image?")

            col1, col2, col3 = st.columns([1, 4, 1])
            with col1:
                st.write("Extremely easy")

            with col2:
                easy_to_imagine = st.radio(
                    "",
                    options=list(range(1, 8)),
                    horizontal=True,
                    key=f"ease_{st.session_state.image_index}",
                )

            with col3:
                st.write("Extremely difficult")

            if st.button("Submit"):
                # Save response (FIXED: vividness and ease are no longer swapped)
                st.session_state.responses.append(
                    {
                        "username": st.session_state.username,
                        "image": current_image_name,
                        "vividness": st.session_state.current_vividness,
                        "easy_to_imagine": easy_to_imagine,
                    }
                )
                next_image()