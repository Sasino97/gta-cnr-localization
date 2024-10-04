"""Module providing a static class for validating XML localization files."""
import argparse
import json
import sys
import xml.dom.minidom
import xml.sax
import xml.sax.xmlreader
import re
from dataclasses import dataclass, field
from typing import TypeVar, Optional


T = TypeVar("T")
COLORAMA_INSTALLED = True
DOMINATE_INSTALLED  = True
XML_LANG_ATTRIB =  "xml:lang"
SHORT_GTA_FORMAT_REGEX = r"~(?:[s,b,r,n,y,p,g,o,h,c]|HUD_COLOUR_NET_PLAYER1)~"
TOO_MANY_SPACES_REGEX = r"\s~[s,b,r,n,y,p,g,o,h,c]~\s|\s\s+"
TEXT_VARIABLE_REGEX = r"{[0-9]+}"
PUNCTUATION_MARKS_REGEX = r"[.,?,!]"
WRONG_PUNCTUATION_REGEX = r"\s" + PUNCTUATION_MARKS_REGEX + r"|\s" + SHORT_GTA_FORMAT_REGEX + PUNCTUATION_MARKS_REGEX


try:
    import colorama
except ModuleNotFoundError:
    COLORAMA_INSTALLED = False

try:
    import dominate
    import dominate.tags
except ModuleNotFoundError:
    DOMINATE_INSTALLED = False


if DOMINATE_INSTALLED:
    import lib.html_preview


def str_from_node(node: xml.dom.minidom.Node) -> str:
    """
    Extracts and concatenates the text content from the child nodes of the given XML DOM Node.

    Args:
        node (xml.dom.minidom.Node): The XML DOM Node from which text content will be extracted.

    Returns:
        str: A string containing the concatenated text content of all child nodes with nodeType TEXT_NODE.
    """
    return "".join(t.nodeValue for t in node.childNodes if t.nodeType == t.TEXT_NODE)


def get_consecutive_duplicate(lst: list[T], exceptions: list[T] = None) -> Optional[T]:
    """
    Finds the first consecutive duplicate element in a list, excluding elements specified in the exceptions list.

    Args:
        lst (List[T]): The input list to search for consecutive duplicates.
        exceptions (List[T]): A list of elements to be excluded from consideration.

    Returns:
        Optional[T]: The first consecutive duplicate element found, or None if no such element is found.
    """
    if exceptions is None:
        exceptions = []
    for i in range(len(lst) - 1):
        if lst[i] not in exceptions:
            if lst[i] == lst[i + 1]:
                return lst[i]
    return None


@dataclass
class EntryInfo:
    """
    Data class representing information about entry.

    Attributes:
        translations (List[str]): List of translations for the entry.
        found_langs (List[str]): List of language codes found in the entry.
        should_end_with_format (Optional[str]): The expected format tag for the last found format in the entry.
        required_text_formatting (Set[str]): Set of required text formatting tags in the entry.
        required_variables (List[str]): List of required variables in the entry.
    """
    translations: list[str] = field(default_factory=list)
    found_langs: list[str] = field(default_factory=list)
    should_end_with_format: Optional[str] = field(default=None)
    required_text_formatting: set[str] = field(default_factory=set)
    required_variables: list[str] = field(default_factory=list)


class Validator:
    """XML Validation

    This class provides utility functions for validating XML localization files.

    Attributes:
        xml_files (list[str]): A list of XML filenames to be validated.
        supported_langs (list[str]): A list of supported language codes.
        used_ids (set): A set of used IDs during validation.
        fatal_errors (int): A count of encountered fatal errors during validation.
        errors (int): A count of encountered errors during validation.
        warnings (int): A count of encountered warnings during validation.
        display_limit (int): Display limit for known elements.
        show_lang (str | None): The selected language that is shown if missing.
        found_missing_lang (int): A count of missing localizations for selected language.
        total_strings (int): Total number of strings processed during validation.
        custom_xml_parser (xml.sax.xmlreader.XMLReader): Custom parser for XML validation.
        preview_formatting (bool): Flag indicating whether preview formatting is enabled.
        main_doc (dominate.document): Main document used for validation.
        warnings_as_errors (bool): Flag indicating whether warnings should be treated as errors.
    """
    xml_files: list[str] = []
    supported_langs: list[str] = ["en-US", "de-DE", "fr-FR", "nl-NL", "it-IT", "es-ES", "pt-BR",
        "pl-PL", "tr-TR", "ar-001", "zh-Hans", "zh-Hant", "hi-Latn", "vi-VN", "th-TH", "id-ID", "cs-CZ"]
    used_ids: set[str] = set()
    fatal_errors: int = 0
    errors: int = 0
    warnings: int = 0
    display_limit: int = 10
    show_lang: str | None = None
    found_missing_lang: int = 0
    total_strings: int = 0
    custom_xml_parser: xml.sax.xmlreader.XMLReader = None
    preview_formatting: bool = False
    main_doc = None
    warnings_as_errors: bool = False

    @staticmethod
    def setup_xml_parser() -> xml.sax.xmlreader.XMLReader:
        # pylint: disable=W0212
        """
        Set up a custom XML parser with additional functionality to track parse positions.

        Returns:
            xml.sax.xmlreader.XMLReader: A custom XML parser with extended features.
        """
        custom_xml_parser = xml.sax.make_parser()
        orig_set_content_handler = custom_xml_parser.setContentHandler
        def set_content_handler(dom_handler):
            def start_element_ns(name, tag_name, attrs):
                orig_start_cb(name, tag_name, attrs)
                cur_elem = dom_handler.elementStack[-1]
                cur_elem.parse_position = (
                    custom_xml_parser._parser.CurrentLineNumber,
                    custom_xml_parser._parser.CurrentColumnNumber
                )

            orig_start_cb = dom_handler.startElementNS
            dom_handler.startElementNS = start_element_ns
            orig_set_content_handler(dom_handler)
        custom_xml_parser.setContentHandler = set_content_handler
        return custom_xml_parser


    @staticmethod
    def get_location_string(location: list[str], custom_file_cursor: tuple[int] | None = None):
        """Generates a string representation of a location.

        Args:
            location (list[str]): A list of strings representing the location.

        Returns:
            str: A string representation of the location.
        """
        if len(location) == 0:
            return ""
        string = location[0]
        if custom_file_cursor is not None:
            string += f"[{custom_file_cursor[0]},{custom_file_cursor[1]+1}]"
        if len(location[1:]) != 0:
            string += '->' + '->'.join(location[1:])
        return string


    @staticmethod
    def print_error(error: str, location: list[str], custom_file_cursor: tuple[int] | None = None):
        """Prints an error message with the given location.

        Args:
            error (str): The error message to print.
            location (list[str]): A list of strings representing the location of the error.

        Returns:
            None
        """
        Validator.errors += 1
        loc_string = Validator.get_location_string(location, custom_file_cursor=custom_file_cursor)
        txt = f"[!] {loc_string}:\n{error}"
        if COLORAMA_INSTALLED:
            print(f"{colorama.Fore.RED}{txt}{colorama.Fore.RESET}")
        else:
            print(txt)
        print()


    @staticmethod
    def print_fatal_error(error: str, location: list[str], custom_file_cursor: tuple[int] | None = None):
        """Prints an error message with the given location.

        Args:
            error (str): The error message to print.
            location (list[str]): A list of strings representing the location of the error.

        Returns:
            None
        """
        Validator.fatal_errors += 1
        loc_string = Validator.get_location_string(location, custom_file_cursor=custom_file_cursor)
        txt = f"[!!!] {loc_string}:\n{error}"
        if COLORAMA_INSTALLED:
            print(f"{colorama.Fore.RED}{colorama.Style.BRIGHT}{txt}{colorama.Fore.RESET}{colorama.Style.NORMAL}")
        else:
            print(txt)
        print()


    @staticmethod
    def print_warning(warning: str, location: list[str], custom_file_cursor: tuple[int] | None = None):
        """Prints a warning message with the given location.

        Args:
            warning (str): The warning message to print.
            location (list[str]): A list of strings representing the location of the warning.

        Returns:
            None
        """
        loc_string = Validator.get_location_string(location, custom_file_cursor=custom_file_cursor)
        txt = f"[*] {loc_string}:\n{warning}"
        if COLORAMA_INSTALLED:
            print(f"{colorama.Fore.YELLOW}{txt}{colorama.Fore.RESET}")
        else:
            print(txt)
        print()


    @staticmethod
    def print_warning_or_error(warning: str, location: list[str], custom_file_cursor: tuple[int] | None = None):
        """
        Print a warning or an error based on the configuration of the Validator class.

        Args:
            warning (str): The warning or error message to be printed.
            location (list[str]): A list specifying the location information related to the warning or error.
            custom_file_cursor (tuple[int] | None): A tuple representing the custom file cursor position (line, column),
        or None if not provided.

        Note:
        The printing behavior is determined by the 'warnings_as_errors' configuration in the Validator class.
        If 'warnings_as_errors' is True, the message is treated as an error and printed accordingly.
        If 'warnings_as_errors' is False, the message is treated as a warning and printed accordingly.
        """
        if Validator.warnings_as_errors:
            Validator.print_error(warning, location, custom_file_cursor)
        else:
            Validator.print_warning(warning, location, custom_file_cursor)


    @staticmethod
    def entry_pretty_print(entry: xml.dom.minidom.Element) -> str:
        """
        Generate a pretty-printed string representation of an XML DOM Element.

        Args:
            entry (xml.dom.minidom.Element): The XML DOM Element to be pretty-printed.

        Returns:
            str: A formatted string representing the tag name and 'Id' attribute (if present) of the given element.
        Example: "TagName(Id='some_id')"
    """
        return f"{entry.tagName}({repr(dict(entry.attributes.items()).get('Id'))})"


    @staticmethod
    def check_unknown_tag(entry: xml.dom.minidom.Element, known_tags: list[str], location: list[str]) -> bool:
        """Checks if an XML element's tag is in the list of known tags.

        Args:
            entry (xml.etree.ElementTree.Element): The XML element to check.
            known_tags (list[str]): List of known tag names.
            location (list[str]): A list of strings representing the location.

        Returns:
            bool: True if the tag is known, False otherwise.
        """
        if entry.tagName in known_tags:
            return True
        known_tags_str = ', '.join(known_tags[:Validator.display_limit])
        Validator.print_error(f"Unknown tag: {repr(entry.tagName)}, "
                              f"expected one of these: {known_tags_str}", location, entry.parse_position)
        return False


    @staticmethod
    def check_xml_files():
        # pylint: disable=W0212
        """
        Validate and analyze XML files using the configured Validator settings.

        Iterates through each XML file specified in `Validator.xml_files`. Performs the following tasks for each file:
        - If DOMINATE_INSTALLED and Validator.preview_formatting are True, adds an h1 header with the file name to the main DOM.
        - Attempts to parse the XML file using the configured custom XML parser.
        - Checks for common errors, unknown tags, and processes entries within the XML file.
        - Increments the total_strings count for each valid entry.

        Note:
        - If a file is not found, a FileNotFoundError is caught and reported as an error.
        - If there's a parsing error (SAXParseException), a fatal error is reported, and the custom XML parser is reset.
        - SAXNotSupportedException is caught and ignored.

        This function operates with the assumption that the Validator class is appropriately configured.
        """
        Validator.custom_xml_parser = Validator.setup_xml_parser()
        for file in Validator.xml_files:
            if DOMINATE_INSTALLED and Validator.preview_formatting:
                with Validator.main_doc.body:
                    dominate.tags.h1(file)
            try:
                dom = xml.dom.minidom.parse(file, Validator.custom_xml_parser)
                root: xml.dom.minidom.Element = dom.documentElement
                path = [file, root.tagName]
                for child in root.childNodes:
                    child: xml.dom.minidom.Element
                    if isinstance(child, xml.dom.minidom.Text):
                        continue
                    if Validator.check_unknown_tag(child, ["Entry"], path):
                        Validator.check_entries(child, path)
                        Validator.total_strings += 1
            except FileNotFoundError as err:
                Validator.print_error(f"Invalid file: {err}", [file])
            except xml.sax.SAXParseException as err:
                Validator.print_fatal_error(f"Invalid file: {err.getMessage()}", [file],
                                            custom_file_cursor=(err.getLineNumber(), err.getColumnNumber()))
                Validator.custom_xml_parser = Validator.setup_xml_parser()
            except xml.sax._exceptions.SAXNotSupportedException:
                pass


    @staticmethod
    def check_entries(entry: xml.dom.minidom.Element, path: list[str]):
        """
        Validate and analyze the entries within an XML DOM Element.

        Args:
            entry (xml.dom.minidom.Element): The XML DOM Element representing an entry to be validated.
            path (list[str]): The path to the current XML DOM Element, used for error reporting.

        This function checks various aspects of each string entry within the given XML DOM Element, including:
            Presence of required attributes, such as 'Id' and 'xml:lang'.
            Correct usage of text formatting tags (~[s,b,r,n,y,p,g,o,h,c]~).
            Consistency and correctness of variables ({[0-9]+}) within the text.
            Presence of empty translations.
            Proper spacing between words and punctuation mark placement.

        Additionally, it reports warnings if a specific language translation is missing.

        Note:
            The function assumes that the Validator class is appropriately configured.
        """
        element_found_id = dict(entry.attributes.items()).get("Id")
        element_location = entry.parse_position
        if element_found_id is None:
            Validator.print_error("Found element without id!", path, custom_file_cursor=element_location)
        else:
            if element_found_id in Validator.used_ids:
                Validator.print_error(f"Found element duplicate with id {repr(element_found_id)}!", path, custom_file_cursor=element_location)
                Validator.total_strings -= 1
            Validator.used_ids.add(element_found_id)
            path = [*path, Validator.entry_pretty_print(entry)]
            if DOMINATE_INSTALLED and Validator.preview_formatting:
                with Validator.main_doc.body:
                    dominate.tags.h2(element_found_id)
        translations, entry_info = Validator.analyze_entry(entry, path)
        for translation in translations:
            Validator.check_translation(translation, entry_info, path)
        if (Validator.show_lang is not None) and (Validator.show_lang not in entry_info.found_langs):
            if Validator.found_missing_lang <= Validator.display_limit:
                Validator.print_warning_or_error(f"Missing translation for {repr(Validator.show_lang)}!", path, element_location)
            Validator.found_missing_lang += 1


    @staticmethod
    def analyze_entry(entry: xml.dom.minidom.Element, path: list[str]) -> tuple[list[xml.dom.minidom.Element], EntryInfo]:
        """
        Analyze an XML DOM Element representing an entry and extract relevant information.

        Args:
            entry (xml.dom.minidom.Element): The XML DOM Element representing an entry to be analyzed.
            path (list[str]): The path to the current XML DOM Element, used for error reporting.

        Returns:
            Tuple[List[xml.dom.minidom.Element], EntryInfo]: A tuple containing a list of translation elements
        within the entry and an EntryInfo object representing information about the entry.
        """
        translations: list[xml.dom.minidom.Element] = []
        entry_info = EntryInfo()
        for child_node in entry.childNodes:
            if isinstance(child_node, xml.dom.minidom.Text):
                continue
            child_node: xml.dom.minidom.Element
            if Validator.check_unknown_tag(child_node, ["String"], path):
                translations.append(child_node)
                for key, value in child_node.attributes.items():
                    if key != XML_LANG_ATTRIB:
                        Validator.print_error(f"Unknown attribute: {repr(key)}", path, child_node.parse_position)
                        continue
                    if value == "en-US":
                        found_formats = re.findall(SHORT_GTA_FORMAT_REGEX, str_from_node(child_node))
                        if len(found_formats) > 0:
                            entry_info.required_text_formatting = set(found_formats)
                            entry_info.should_end_with_format = found_formats[-1]
                        entry_info.required_variables = re.findall(TEXT_VARIABLE_REGEX, str_from_node(child_node))
                    if value in entry_info.found_langs:
                        Validator.print_error(f"Found duplicate string for {value}", path, child_node.parse_position)
                    entry_info.found_langs.append(value)
        return (translations, entry_info)


    @staticmethod
    def check_translation(string_entry: xml.dom.minidom.Element, info: EntryInfo, path: list[str]):
        """
        Validate and analyze the translation string within an XML DOM Element.

        Args:
            string_entry (xml.dom.minidom.Element): The XML DOM Element representing the translation string to be checked.
            info (EntryInfo): An EntryInfo object containing information about the entry, such as required formats and variables.
            path (list[str]): The path to the current XML DOM Element, used for error reporting.

        This function checks various aspects of the translation string, including:
        - Proper usage of text formatting tags (~[s,b,r,n,y,p,g,o,h,c]~).
        - Consistency and correctness of variables ({[0-9]+}) within the text.
        - Presence of empty translations.
        - Proper spacing between words and punctuation mark placement.

        The function uses the Validator class for error reporting and configuration.

        Note:
            The function assumes that the Validator class is appropriately configured.
        """
        text = str_from_node(string_entry)
        current_lang: str = dict(string_entry.attributes.items()).get(XML_LANG_ATTRIB)
        start_position: tuple[int] = (
            string_entry.parse_position[0],
            string_entry.parse_position[1]+len('<String xml:lang="')+len(current_lang)+len('">'))
        path1 = [*path, current_lang]
        if DOMINATE_INSTALLED and Validator.preview_formatting:
            with Validator.main_doc.body:
                dominate.tags.h3(current_lang)
                lib.html_preview.formatted_string_to_html(text)
        found_formats: list[str] = re.findall(SHORT_GTA_FORMAT_REGEX, text)
        if len(found_formats)>0 and info.should_end_with_format is not None:
            found_formats_set = set(found_formats)
            invalid_text_formatting = found_formats_set.difference(info.required_text_formatting)
            missing_text_formatting = info.required_text_formatting.difference(found_formats_set)
            formatting_duplicate = get_consecutive_duplicate(found_formats, exceptions=["~h~","~n~","~s~"])
            if invalid_text_formatting:
                pos = (start_position[0],
                       start_position[1] + text.find(list(invalid_text_formatting)[0]))
                Validator.print_error(f"Found invalid text formatting: {', '.join(invalid_text_formatting)}", path1, pos)
            if missing_text_formatting:
                Validator.print_error(f"Missing text formatting: {', '.join(missing_text_formatting)}", path1, start_position)
            if formatting_duplicate:
                pos = (start_position[0],
                       start_position[1] + text.rfind(formatting_duplicate))
                Validator.print_error(f"Found text formatting duplicate: {formatting_duplicate}", path1, pos)
            found_format = found_formats[-1]
            if found_format != info.should_end_with_format:
                pos = (start_position[0],
                       start_position[1] + text.rfind(found_format))
                Validator.print_error(f"String ends with a wrong format {repr(found_format)}, "
                                        f"expected {repr(info.should_end_with_format)}", path1, pos)
        found_variables = re.findall(TEXT_VARIABLE_REGEX, text)
        if len(found_variables) < len(info.required_variables):
            missing_variables = [var for var in info.required_variables if var not in found_variables]
            if missing_variables:
                Validator.print_error(f"Missing variables: {', '.join(missing_variables)}", path1, start_position)
        elif len(found_variables) > len(info.required_variables):
            unneeded_variables = [var for var in found_variables if var not in info.required_variables]
            if unneeded_variables:
                pos = (start_position[0],
                       start_position[1] + text.rfind(unneeded_variables[-1]))
                Validator.print_error(f"Found too many variables: {', '.join(unneeded_variables)}", path1, pos)
        if len(text) == 0:
            Validator.print_error("Found empty translation", path1, start_position)
        text_without_formatting = re.sub(SHORT_GTA_FORMAT_REGEX, "", text)
        invalid_text_formatting_loc = text_without_formatting.find("~")
        if invalid_text_formatting_loc != -1:
            offset: int = 0
            for valid_text_formatting_match in re.finditer(SHORT_GTA_FORMAT_REGEX, text):
                valid_text_formatting_match: re.Match
                if valid_text_formatting_match.end() > invalid_text_formatting_loc + offset:
                    offset += valid_text_formatting_match.end()-valid_text_formatting_match.start()
                else:
                    break
            real_location = text[(invalid_text_formatting_loc + offset):].find("~")+(invalid_text_formatting_loc + offset)
            position: tuple[int] = (start_position[0], start_position[1]+real_location)
            Validator.print_error("Found invalid text formatting (~)", path1, position)
        too_many_spaces_match: re.Match = re.search(TOO_MANY_SPACES_REGEX, text)
        if too_many_spaces_match:
            position: tuple[int] = (start_position[0], start_position[1]+too_many_spaces_match.end()-1)
            Validator.print_warning_or_error("Found too many spaces between words", path1, position)
        wrong_punctuation_match: re.Match = re.search(WRONG_PUNCTUATION_REGEX, text)
        if wrong_punctuation_match:
            position: tuple[int] = (start_position[0], start_position[1]+wrong_punctuation_match.start())
            Validator.print_warning_or_error("Found invalid punctuation mark placement", path1, position)


if __name__ == '__main__':
    if COLORAMA_INSTALLED:
        colorama.init()
    parser = argparse.ArgumentParser(description='Validates localization files')
    parser.add_argument('--show_lang', type=str, help='Show missing language localizations', choices=Validator.supported_langs)
    parser.add_argument('--preview_formatting', action='store_true', help='Show formatted localizations as HTML file')
    parser.add_argument('--treat_warnings_as_errors', action='store_true', help='Treat warnings as errors')
    parser.add_argument('--display_limit', type=int, default=10, help='Set display limit for missing translations')
    args = parser.parse_args()
    if args.preview_formatting:
        if DOMINATE_INSTALLED:
            Validator.preview_formatting = True
            Validator.main_doc = lib.html_preview.create_html_doc()
        else:
            print("Unable to generate preview, dominate is not installed")
            print("You need to install it with 'pip install dominate'")
    Validator.display_limit = args.display_limit
    Validator.warnings_as_errors = args.treat_warnings_as_errors
    Validator.show_lang = args.show_lang
    with open("index.json", "r", encoding="utf-8") as index_file:
        Validator.xml_files = json.load(index_file)
    Validator.check_xml_files()
    if Validator.show_lang is not None:
        print(f"Total missing translations for {repr(Validator.show_lang)}: {Validator.found_missing_lang}. "
              f"Progress: {Validator.total_strings - Validator.found_missing_lang}/{Validator.total_strings} "
              f"({int((Validator.total_strings - Validator.found_missing_lang)/Validator.total_strings * 100)}%)")
    if Validator.preview_formatting:
        with open("preview.html", "w", encoding="utf-8") as preview_file:
            preview_file.write(Validator.main_doc.render(pretty=False))
        print("Formatting preview has been generated in preview.html\n")
    if Validator.fatal_errors > 0:
        print(f"Fatal errors: {Validator.fatal_errors}")
    if Validator.errors > 0:
        print(f"Errors: {Validator.errors}")
    if Validator.errors > 0 or Validator.fatal_errors > 0:
        sys.exit(1)
    else:
        print("No errors found")
    if COLORAMA_INSTALLED:
        colorama.deinit()
