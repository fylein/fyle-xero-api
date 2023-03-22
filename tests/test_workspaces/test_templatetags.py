import pytest
from apps.workspaces.templatetags.custom_filters import snake_case_to_space_case

def test_snake_case_to_space_case():
    input_string = "snake_case_example"
    expected_output = "Snake Case Example"

    assert snake_case_to_space_case(input_string) == expected_output
