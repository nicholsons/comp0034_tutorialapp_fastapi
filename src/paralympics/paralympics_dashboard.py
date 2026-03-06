from pathlib import Path
from typing import Any, Dict, List

import requests
import streamlit as st

from paralympics.charts import bar_chart, line_chart, scatter_map

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
API_BASE = "http://127.0.0.1:8000"  # REST API default URL
TIMEOUT = 5  # seconds

st.set_page_config(page_title="Paralympics Dashboard", layout="wide")


# Helper functions for interacting with the REST API

def _get(url: str, **kwargs) -> requests.Response:
    """HTTP GET with a uniform timeout and error handling.

    Args:
        url (str): URL to request
        timeout (int): Timeout in seconds

    Returns:
        requests.Response: Response object

    Raises:
        RuntimeError: If request fails
    """
    try:
        resp = requests.get(url, timeout=TIMEOUT, **kwargs)
        resp.raise_for_status()
        return resp
    except requests.exceptions.RequestException as e:
        # Propagate a clean error message upward
        raise RuntimeError(f"Request failed for {url}: {e}") from e


@st.cache_data(show_spinner=False)
def count_questions() -> int:
    """Return the number of questions available.

    Returns:
        int: Number of questions
        """
    resp = _get(f"{API_BASE}/questions")
    data = resp.json()
    return len(data)


@st.cache_data(show_spinner=False)
def get_question(qid: int) -> Dict[str, Any]:
    """Return the question JSON by ID.

    Args:
        qid (int): Question ID

    Returns:
        Dict[str, Any]: JSON for a given question ID with id and question_text
    """
    resp = _get(f"{API_BASE}/questions/{qid}")
    return resp.json()


@st.cache_data(show_spinner=False)
def get_responses(qid: int) -> List[Dict[str, Any]]:
    """Return the responses for a given question ID.

    Args:
        qid (int): Question ID

    Returns:
        List[Dict[str, Any]]: Response JSON containing the responses for a given question ID
        """
    resp = _get(f"{API_BASE}/response/search", params={"question_id": qid})
    return resp.json()


# Chart helper
def clear_other_state():
    """Clear irrelevant widget state whenever the chart choice changes."""
    for key in ["trend_feature", "bar_pills"]:
        st.session_state.pop(key, None)


# Quiz helper
def render_question_block():
    """ Render the question block.

    - Get the index from the session state (starts at 1)
    - Render the question block (question text and the response options as radio plus submit button)
    - When the submit button is clicked
        - check a response is selected
        - if a response is selected, check if is it correct (uses the response.id)
        - if the response is correct, render the next question unless all questions have been
        completed (compares the question number to the number of questions in the database)
        - if the response is incorrect, stay on the same question and allow another attempt

    """
    st.header("Questions")

    if "q_index" not in st.session_state:
        st.session_state.q_index = 1

    q_index = st.session_state.q_index

    # Fetch total count
    try:
        num_q = count_questions()
    except Exception as e:
        st.error(f"Unable to load questions. {e}")
        return

    # If past the last question, show completion and exit
    if q_index > num_q:
        st.success("Questions complete, well done!")
        return

    # Fetch the current question + its responses
    try:
        q = get_question(q_index)
    except Exception as e:
        st.error(f"Unable to load question. {e}")
        return

    try:
        responses = get_responses(q_index)
    except Exception as e:
        st.info(f"Unable to load responses. {e}")
        responses = []

    # Build radio options as label -> id map
    label_to_id = {r.get("response_text", ""): r.get("id") for r in responses if
                   r.get("response_text", "")}

    # If no responses returned from the REST API
    if not label_to_id:
        st.info("No responses available for this question.")
        return

    with st.form(key="quiz_form", clear_on_submit=False):
        st.write(q.get("question_text", ""))
        selected_label = st.radio(
            "Select one answer:",
            options=list(label_to_id.keys()),
            index=None,
        )
        submitted = st.form_submit_button("Submit answer")

    # Handle submission
    if submitted:
        if not selected_label:
            st.info("Please select an answer.")
            return

        selected_id = str(label_to_id[selected_label])

        # Find the selected response to inspect correctness
        selected_obj = next(
            (r for r in responses if str(r.get("id")) == selected_id),
            None,
        )

        if selected_obj and selected_obj.get("is_correct"):
            # Advance or finish
            if q_index >= num_q:
                st.session_state.q_index = num_q + 1
                st.success("Questions complete, well done!")
            else:
                st.session_state.q_index = q_index + 1
                # Using rerun ensures the next question renders cleanly
                st.rerun()
        else:
            st.info("Please try again!")


# Layout

nav_container = st.container(horizontal=True, horizontal_alignment="center")
with nav_container:
    logo = STATIC_DIR / "colour-logo.png"
    st.image(logo, width=40)
    st.markdown("**Paralympics research app**")

st.markdown("Use the charts to explore the data and then answer the questions below.")

left_col, right_col = st.columns([1, 3])

with left_col:
    # 1. Choose chart
    st.selectbox(
        "Choose a chart:",
        ["Trends", "Participants by gender", "Paralympics locations"],
        key="chart_choice",
        index=None,
        placeholder="Select chart to view...",
        on_change=clear_other_state
    )

    # 2. Line chart → show second selectbox
    if st.session_state.get("chart_choice") == "Trends":
        st.selectbox(
            "Choose feature:",
            ["Sports", "Events", "Countries", "Participants"],
            key="trend_feature"
        )

    # 4. Bar chart → show pills
    elif st.session_state.get("chart_choice") == "Participants by gender":
        st.pills(
            "Choose the type of Paralympics:",
            ["Winter", "Summer"],
            key="bar_pills",
            selection_mode="multi"
        )

with right_col:
    # 3. Draw a line chart after the feature is selected
    if st.session_state.get("chart_choice") == "Trends" and st.session_state.get("trend_feature"):
        feature = str.lower(st.session_state.trend_feature)
        fig = line_chart(feature)
        st.plotly_chart(fig, width="content")

    # 5. Draw one or more bar charts depending on pill selection
    if st.session_state.get("chart_choice") == "Participants by gender" and st.session_state.get(
            "bar_pills"):
        for pill in st.session_state.bar_pills:
            event_type = str.lower(pill)
            fig = bar_chart(event_type)
            st.plotly_chart(fig, width="content")

    # 6. Map chart displays once chosen
    if st.session_state.get("chart_choice") == "Paralympics locations":
        fig = scatter_map()
        st.plotly_chart(fig, width="content")

# Full-width section
st.divider()

# Questions
question_container = st.container()
with question_container:
    render_question_block()
