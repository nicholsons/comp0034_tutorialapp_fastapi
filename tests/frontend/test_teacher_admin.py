from unittest.mock import Mock, patch

from streamlit.testing.v1 import AppTest


def test_elements_present():
    at = AppTest.from_file("src/paralympics/pages/teacher_admin.py")
    at.run()

    assert at.header[1].value.lower() == "create question"
    assert len(at.text_input) >= 5  # question text + 4 option inputs
    assert len(at.checkbox) == 4
    assert at.button[1].label.lower() == "save question"


def test_error_when_question_text_missing():
    at = AppTest.from_file("src/paralympics/pages/teacher_admin.py")
    at.run()

    # Leave question blank
    at.text_input("Enter the question").input("A new question.")

    # Fill the four option texts but mark none correct
    for i in range(1, 5):
        at.text_input("Text for option", key=f"response_text_{i}").input("Option text")
        at.checkbox("Correct?", key=f"is_correct_{i}").uncheck()

    # Click submit
    at.button("Save Question").click()
    at.run()

    # Assert error about missing question text
    assert "Question text is required." in [e.value for e in at.error]


def test_error_when_no_correct_answer_selected():
    at = AppTest.from_file("src/paralympics/pages/teacher_admin.py")
    at.run()

    at.text_input("Enter the question").input("Test question")
    for i in range(1, 5):
        at.text_input("Text for option", key=f"response_text_{i}").input("Some option")
        at.checkbox("Correct?", key=f"is_correct_{i}").uncheck()

    at.form_submit_button("Save Question").click()
    at.run()

    assert "Please select exactly one correct response (none selected)." in [
        e.value for e in at.error
    ]


def test_error_when_multiple_correct_selected():
    at = AppTest.from_file("src/paralympics/pages/teacher_admin.py")
    at.run()

    at.text_input("Enter the question").input("Test question")

    # Two correct answers
    for i in range(1, 5):
        at.text_input("Text for option", key=f"response_text_{i}").input("Option text")

    at.checkbox("Correct?", key="is_correct_1").check()
    at.checkbox("Correct?", key="is_correct_2").check()

    at.form_submit_button("Save Question").click()
    at.run()

    assert "Please select exactly one correct response (multiple selected)." in [
        e.value for e in at.error
    ]


def test_successful_submit():
    at = AppTest.from_file("src/paralympics/pages/teacher_admin.py")
    at.run()

    # Fill form correctly
    at.text_input("Enter the question").input("Who won?")
    for i in range(1, 5):
        at.text_input("Text for option", key=f"response_text_{i}").input(f"Option {i}")
        at.checkbox("Correct?", key=f"is_correct_{i}").uncheck()

    # One correct answer
    at.checkbox("Correct?", key="is_correct_2").check()

    # Mock API responses
    mock_post = Mock()

    # First POST: question creation
    mock_post.return_value.json.return_value = {"id": 42}
    mock_post.return_value.raise_for_status.return_value = None

    with patch("teacher_admin_page.requests.post", mock_post):
        at.form_submit_button("Save Question").click()
        at.run()

    # Assert success message shown
    assert "Question saved successfully." in [s.value for s in at.success]

    # Assert 5 POST calls (1 question + 4 responses)
    assert mock_post.call_count == 5
