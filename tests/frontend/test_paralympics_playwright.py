from playwright.sync_api import Page, expect


def test_page_has_body(page: Page, app_server):
    """
    GIVEN a server URL (dash_app_server fixture yields the URL)
    WHEN the 'home' page is requested
    THEN the page body should be visible
    """
    page.goto(app_server)
    expect(page.locator("body")).to_be_attached()
    expect(page).to_have_title("Paralympics Dashboard")


def test_line_chart_displays(page: Page, app_server):
    """
    GIVEN a server URL
    WHEN the 'home' page is requested
    AND the line chart is chosen (key=chart_choice)
    AND the sports data is chosen
    THEN a plotly line chart should be visible
    """
    # WHEN the home page is selected
    page.goto(app_server)

    # AND the line chart is chosen from the chart selector
    chart_select = page.get_by_test_id("stSelectbox").filter(has_text="Choose a chart:")
    selectbox_input = chart_select.locator("input")
    selectbox_input.click()
    selectbox_input.fill("Trends")
    selectbox_input.press("Enter")

    # AND the sports data is chosen
    chart_select = page.get_by_test_id("stSelectbox").filter(has_text="Choose feature:")
    selectbox_input = chart_select.locator("input")
    selectbox_input.click()
    selectbox_input.fill("Sports")
    selectbox_input.press("Enter")

    # THEN a plotly line chart should be visible
    expect(page.locator(".js-plotly-plot")).to_be_visible()


def test_answer_question_correct(page: Page, app_server):
    """
    GIVEN a server URL
    WHEN the 'home' page is requested
    AND the answer to a question is selected and submitted and is correct
    THEN a new question should be displayed
    """
    page.goto(app_server)
    initial_q = page.get_by_text("In which winter Paralympics were").text_content()
    page.get_by_text("Lillehammer").click()
    page.get_by_test_id("stBaseButton-secondaryFormSubmit").click()
    next_q = page.get_by_text("How many participants were").text_content()
    assert initial_q != next_q  # pytest assertion


def test_new_question_submitted(page: Page, app_server):
    """
    GIVEN a server URL
    WHEN the home page is requested
    AND textarea with id="question_text" has the text for a new question entered
    AND response_text_0, response_text_1, response_text_2 and response_text_3 are completed
    AND one of is_correct_0, is_correct_1, is_correct_2 and is_correct_3 is True
    AND "new-question-submit-button" is clicked
    THEN if the requests to the REST API with a new question and 4 responses are successful, a
    response should be displayed to the 'id="new-question-submit-button"
    with text "Question saved successfully.".
    """
    page.goto(f"{app_server}/teacher_admin")
    question_text = page.get_by_role("textbox", name="Enter the question")
    question_text.click()
    question_text.fill("A new question.")
    question_text.press("Tab")
    page.keyboard.type("A is correct")
    page.keyboard.press("Tab")
    # Toggle (check) the checkbox
    page.keyboard.press("Space")
    page.keyboard.press("Tab")
    page.keyboard.type("B is incorrect")
    page.keyboard.press("Tab")
    page.keyboard.press("Tab")
    page.keyboard.type("C is incorrect")
    page.keyboard.press("Tab")
    page.keyboard.press("Tab")
    page.keyboard.type("D is incorrect")
    page.keyboard.press("Tab")
    page.keyboard.press("Tab")
    page.get_by_role("button", name="Save Question").click()

    expect(page.get_by_text("Question saved")).to_contain_text("Question saved")
