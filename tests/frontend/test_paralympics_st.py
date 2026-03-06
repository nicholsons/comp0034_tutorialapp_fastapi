from pathlib import Path


from streamlit.testing.v1 import AppTest

APP_FILE = Path(__file__).parent.parent.joinpath("src", "paralympics", "paralympics_dashboard.py")

def test_questions_header():
    """
    GIVEN a test app
    WHEN the page is requested
    THEN there should be a header with the test Questions
    """
    # Load the Streamlit app from file and run it
    at = AppTest.from_file(APP_FILE).run()
    # Assert the app did not crash
    assert not at.exception
    # Access the header value and assert it is "Questions"
    assert at.header[0].value == "Questions"
    # Alternatively, assert that at least one header has the work question, case in-sensitive
    assert any("question" in h.value.lower() for h in at.header), "No header contains 'question'"


def test_line_chart_selectors():
    """
    GIVEN a test app
    WHEN the line chart is chosen
    AND the sports data is chosen
    THEN the chosen options should be displayed
    """
    # running test app
    at = AppTest.from_file(APP_FILE).run()

    # the line chart is chosen from the selector
    at.selectbox[0].set_value("Trends").run()
    assert at.selectbox[0].value == "Trends"

    # the sports data is chosen from the selector
    at.selectbox[1].set_value("Sports").run()
    assert at.selectbox[1].value == "Sports"

