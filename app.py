import streamlit as st
import os
import hashlib
import random
import pandas as pd
# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(page_title="Image Rating Task", layout="centered")

animal = "cat"  # <-- change dynamically if needed
image_dir = os.path.join("animals", animal)
image_paths = sorted(os.listdir(image_dir))


# Keep only image files
image_paths = [
    img for img in image_paths
    if img.lower().endswith((".png", ".jpg", ".jpeg"))
]
random.shuffle(image_paths)
# -----------------------------
# SESSION STATE INIT
# -----------------------------
defaults = {
    "page": "login",
    "username": "",
    "image_index": 0,
    "step": 0,  # 0=image, 1=Q1, 2=Q2
    "responses": []
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# -----------------------------
# STATE CONTROL FUNCTIONS
# -----------------------------
def go_to_task():
    st.session_state.page = "task"
    st.session_state.image_index = 0
    st.session_state.step = 0
    st.session_state.responses = []
    st.rerun()


def next_step():
    st.session_state.step += 1
    st.rerun()


def next_image():
    st.session_state.image_index += 1
    st.session_state.step = 0
    st.rerun()


def reset_all():
    for k, v in defaults.items():
        st.session_state[k] = v
    st.rerun()


# -----------------------------
# LOGIN PAGE
# -----------------------------
if st.session_state.page == "login":

    st.title("Enter your name")

    name_input = st.text_input("Name")

    if st.button("Start", disabled=not name_input.strip()):

        # Generate random 10-digit number
        random_number = random.randint(10**9, 10**10 - 1)

        # Combine name + random number
        raw_string = f"{name_input.strip()}_{random_number}"

        # Hash it
        hashed_username = hashlib.sha256(raw_string.encode()).hexdigest()[:12]

        # Store hashed ID
        st.session_state.username = hashed_username

        st.session_state.page = "task"
        st.rerun()


# -----------------------------
# TASK PAGE
# -----------------------------
elif st.session_state.page == "task":

    total_images = len(image_paths)



    if st.session_state.image_index >= total_images:

        st.success("All images completed.")
        st.write("Responses:")

        df = pd.DataFrame(st.session_state.responses)
 
        if not df.empty and "image" in df.columns:

            # Ensure string type
            df["image"] = df["image"].astype(str)

            # Create filename column (original full name)
            df["filename"] = df["image"]

            # Remove extension from image column
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
        current_image_name = image_paths[st.session_state.image_index]
        current_image_path = os.path.join(image_dir, current_image_name)

        st.title("Image Imagery Rating")
        st.caption(
            f"User: {st.session_state.username} | "
            f"Image {st.session_state.image_index + 1} / {total_images}"
        )

        # -----------------------------
        # STEP 0 → Show image only
        # -----------------------------
        if st.session_state.step == 0:

            col1, col2, col3 = st.columns([1,2,1])

            with col2:
                st.image(current_image_path, use_container_width=True)

            if st.button("Next"):
                next_step()

        # -----------------------------
        # STEP 1 → Image + Question 1
        # -----------------------------
        elif st.session_state.step == 1:

                        # st.image(current_image_path, use_container_width=True)
            st.markdown("## 1. How easy is it to imagine this image?")

            col1, col2, col3 = st.columns([1,4,1])

            with col1:
                st.write("Low")

            with col2:
                q1 = st.radio(
                    "",
                    options=list(range(1, 8)),
                    horizontal=True,
                    key=f"q1_{st.session_state.image_index}"
                )

            with col3:
                st.write("High")

            if st.button("Next"):
                st.session_state.current_q1 = q1
                next_step()

        # -----------------------------
        # STEP 2 → Image + Question 2
        # -----------------------------
        elif st.session_state.step == 2:

            # st.image(current_image_path, use_container_width=True)
            st.markdown("## 1. How vividly can you imagine ?")

            col1, col2, col3 = st.columns([1,4,1])

            with col1:
                st.write("Low")

            with col2:
                q2 = st.radio(
                    "",
                    options=list(range(1, 8)),
                    horizontal=True,
                    key=f"q1_{st.session_state.image_index}"
                )

            with col3:
                st.write("High")

            if st.button("Submit"):

                # Save response
                st.session_state.responses.append({
                    "username": st.session_state.username,
                    "image": current_image_name,
                    "easy_to_imagine": st.session_state.current_q1,
                    "vividness": q2
                })

                next_image()