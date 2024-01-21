"""
HTML Preview Module for GTA Text Formatting

This module provides functions to convert GTA-formatted text into HTML for preview purposes.
It utilizes GTA text formatting constants and rules defined in 'lib.gta_text_formatting'.

Functions:
    regex_replace_multiple(text: str, replacement_table: list[list[str]]) -> str:
        Replaces multiple patterns in a text using a given replacement table.
    formatted_string_to_html(text: str) -> dominate.tags.span:
        Converts a GTA-formatted string into an HTML span element with appropriate styles.
    create_html_doc() -> dominate.document:
        Creates an HTML document with predefined styles for text formatting preview.
"""
import re
import dominate
import dominate.tags
from .gta_text_formatting import HUD_COLORS, FORMAT_REPLACEMENT_TABLE, LONG_TEXT_FORMATTING_REGEX


def regex_replace_multiple(text: str, replacement_table: list[list[str]]) -> str:
    """
    Replace multiple patterns in a text using a specified replacement table.

    Args:
        text (str): The input text where replacements will be applied.
        replacement_table (list[list[str]]): A list of replacement pairs, where each pair
      is represented as a list containing two strings: the pattern to search for and
      the replacement string.

    Returns:
        str: The modified text after applying all replacements.
    """
    for replacement in replacement_table:
        text = re.sub(replacement[0], replacement[1], text)
    return text


def formatted_string_to_html(text: str) -> dominate.tags.span:
    """
    Convert a formatted text string to an HTML representation using dominate.

    Args:
        text (str): The input text with special formatting markers.

    Returns:
        dominate.tags.span: A Dominate span element representing the formatted HTML.
    """
    main_container: dominate.tags.span = dominate.tags.span()
    text = regex_replace_multiple(text, FORMAT_REPLACEMENT_TABLE)
    bolded = False
    italic = False
    color = "rgb(205,205,205)"
    condensed = 0
    new_line = False
    text_fragments = re.split(LONG_TEXT_FORMATTING_REGEX, text)
    matched_actions = re.findall(LONG_TEXT_FORMATTING_REGEX, text)
    with main_container:
        if text_fragments[0] != "":
            dominate.tags.span(text_fragments[0], style=f"color: {color};")
    for i, fragment in enumerate(text_fragments[1:]):
        formatting = matched_actions[i]
        match formatting:
            case "~h~" | "~bold~":
                bolded = not bolded
            case "~italic~":
                italic = not italic
            case "(C)":
                condensed += 1
            case "(/C)":
                condensed -= 1
            case "~n~":
                new_line = not new_line
            case _:
                hud_color_matches = re.findall(r"(?<=~)(HUD_COLOUR_.+?)(?=~)|(?<=~)(HC_.+?)(?=~)", formatting)
                if hud_color_matches:
                    color = HUD_COLORS[hud_color_matches[0][0]]
                custom_color_matches = re.findall(r"(?<=~CC_)([0-9]{1,3}_[0-9]{1,3}_[0-9]{1,3})(?=~)", formatting)
                if custom_color_matches:
                    color = f'rgba(${custom_color_matches[0].split("_").join(",")})'
        classes = []
        if condensed > 0:
            classes.append("condensed")
        if bolded:
            classes.append("bolded")
        style = ""
        if italic:
            style += "font-style: italic;"
        style += f"color: {color};"
        with main_container:
            if fragment != "":
                with dominate.tags.span(fragment):
                    if classes:
                        dominate.tags.attr(cls=' '.join(classes), style=style)
                    else:
                        dominate.tags.attr(style=style)
            if new_line:
                dominate.tags.br()
    return main_container


def create_html_doc() -> dominate.document:
    """
    Create a dominate document for text formatting preview.

    Returns:
        dominate.document: A Dominate document object.
    """
    doc: dominate.document = dominate.document(title="Text formatting preview")
    with doc.head:
        dominate.tags.style(
            """
            html {
                background-color: #202327;
            }
            span, h1, h2, h3 {
                color: #ffffff;
            }
            @font-face {
                font-family: 'Chalet';
                src: url('fonts/ChaletLondonNineteenSixty.ttf');
                font-stretch: normal;
            }
            @font-face {
                font-family: 'ChaletComprime';
                src: url('fonts/ChaletComprime_CologneSixty.ttf');
                font-stretch: 1%, 100%;
            }
            .condensed {
                font-family:'ChaletComprime';
                font-size: 2.07vh;
            }
            .bold {
                font-weight: bold;
            }
            span {
                font-family:'Chalet';
                font-weight: lighter;
                font-size: 1.725vh;
            }
            """
        )
    return doc
