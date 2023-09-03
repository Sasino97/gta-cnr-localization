import argparse
import json
import sys
import xml.dom.minidom
import xml.sax
import re

USE_COLORAMA = True

try:
    import colorama
except ModuleNotFoundError:
    USE_COLORAMA = False


def get_text_from_node(node: xml.dom.minidom.Node):
    return "".join(t.nodeValue for t in node.childNodes if t.nodeType == t.TEXT_NODE)


class Validator:
    """XML Validation

    This class provides utility functions for validating XML localization files.
    
    Attributes:
        xml_files (list[str]): A list of XML filenames to be validated.
        supported_langs (list[str]): A list of supported language codes.
        nsmap (dict): A namespace mapping for XML namespaces.
        used_ids (set): A set of used IDs during validation.
        errors (int): A count of encountered errors during validation.
        warnings (int): A count of encountered warnings during validation.
        known_display_limit (int): Display limit for known elements.
        show_lang (str | None): The selected language that is shown if missing.
        found_missing_lang (int): A count of missing localizations for selected language.
        customXMLParser(XMLReader): Custom parser for XML validation.
    """
    xml_files: list[str] = []
    supported_langs: list[str] = ["en-US", "de-DE", "fr-FR", "nl-NL", "it-IT", "es-ES", "pt-BR", "pl-PL", "tr-TR", "ar-001", "zh-Hans", "zh-Hant", "hi-Latn", "vi-VN", "th-TH"]
    used_ids: set = set()
    errors: int = 0
    warnings: int = 0
    display_limit: int = 10
    show_lang: str | None = None
    found_missing_lang: int = 0
    total_strings: int = 0
    custom_xml_parser = None

    @staticmethod
    def setup_xml_parser():
        customXMLParser = xml.sax.make_parser()
        orig_set_content_handler = customXMLParser.setContentHandler
        def set_content_handler(dom_handler):
            def start_element_ns(name, tag_name, attrs):
                orig_start_cb(name, tag_name, attrs)
                cur_elem = dom_handler.elementStack[-1]
                cur_elem.parse_position = (
                    customXMLParser._parser.CurrentLineNumber,
                    customXMLParser._parser.CurrentColumnNumber
                )

            orig_start_cb = dom_handler.startElementNS
            dom_handler.startElementNS = start_element_ns
            orig_set_content_handler(dom_handler)
        customXMLParser.setContentHandler = set_content_handler
        return customXMLParser


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
        txt = f"[!] {Validator.get_location_string(location, custom_file_cursor=custom_file_cursor)}:\n{error}"
        if USE_COLORAMA:
            print(f"{colorama.Fore.RED}{txt}{colorama.Fore.RESET}")
        else:
            print(txt)


    @staticmethod
    def print_warning(warning: str, location: list[str], custom_file_cursor: tuple[int] | None = None):
        """Prints a warning message with the given location.

        Args:
            warning (str): The warning message to print.
            location (list[str]): A list of strings representing the location of the warning. 

        Returns: 
            None 
        """
        txt = f"[*] {Validator.get_location_string(location, custom_file_cursor=custom_file_cursor)}:\n{warning}"
        if USE_COLORAMA:
            print(f"{colorama.Fore.YELLOW}{txt}{colorama.Fore.RESET}")
        else:
            print(txt)


    @staticmethod
    def entry_pretty_print(entry: xml.dom.minidom.Element) -> str:
        return f"{entry.tagName}<Id:{repr(dict(entry.attributes.items()).get('Id'))}>"


    @staticmethod
    def check_unknown_tag(entry: xml.dom.minidom.Element, known_tags: list[str], location: list[str])->bool:
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
        Validator.print_error(f"Unknown tag: {repr(entry.tagName)}, expected one of these: {', '.join(known_tags[:Validator.display_limit])}", location, entry.parse_position)
        return False


    @staticmethod
    def check_xml_files():
        for file in Validator.xml_files:
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
                Validator.print_error(f"Invalid file: {err.getMessage()}", [file], custom_file_cursor=(err.getLineNumber(), err.getColumnNumber()))
            except xml.sax._exceptions.SAXNotSupportedException:
                pass


    @staticmethod
    def check_entries(entry: xml.dom.minidom.Element, path: list[str]):
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
        found_langs: list[str] = []
        lang_attrib =  "xml:lang"
        should_end_with_format = None
        good_string_entries = []
        for string_entry in entry.childNodes:
            if isinstance(string_entry, xml.dom.minidom.Text):
                continue
            string_entry: xml.dom.minidom.Element
            if Validator.check_unknown_tag(string_entry, ["String"], path):
                good_string_entries.append(string_entry)
                for key, value in string_entry.attributes.items():
                    if key == lang_attrib:
                        if value == "en-US":
                            found_formats = re.findall(r"~.~", get_text_from_node(string_entry))
                            if (len(found_formats)>0):
                                should_end_with_format = found_formats[-1]
                        found_langs.append(value)
                    else:
                        Validator.print_error(f"Unknown attribute: {repr(key)}", path, string_entry.parse_position)
        for string_entry in good_string_entries:
            text = get_text_from_node(string_entry)
            found_formats = re.findall(r"~.~", text)
            if len(found_formats)>0 and should_end_with_format is not None:
                found_format = found_formats[-1]
                if found_format != should_end_with_format:
                    Validator.print_error(f"String ends with a wrong format {repr(found_format)}, expected {repr(should_end_with_format)}", path, string_entry.parse_position)
                    print(text)
        if (Validator.show_lang is not None) and (Validator.show_lang not in found_langs):
            if Validator.found_missing_lang <= Validator.display_limit:
                Validator.print_warning(f"Missing translation for {repr(Validator.show_lang)}!", path, element_location)
            Validator.found_missing_lang += 1


if __name__ == '__main__':
    if USE_COLORAMA:
        colorama.init()
    parser = argparse.ArgumentParser(description='Validates localization files')
    parser.add_argument('--show_lang', type=str, help='Show missing language localizations', choices=Validator.supported_langs)
    parser.add_argument('--display_limit', type=int, default=10, help='Set display limit for missing translations')
    args = parser.parse_args()
    Validator.custom_xml_parser = Validator.setup_xml_parser()
    Validator.display_limit = args.display_limit
    Validator.show_lang = args.show_lang
    with open("index.json", "r", encoding="utf-8") as index_file:
        Validator.xml_files = json.load(index_file)
    Validator.check_xml_files()
    if Validator.show_lang is not None:
        print(f"Total missing translations for {repr(Validator.show_lang)}: {Validator.found_missing_lang}. "
              f"Progress: {Validator.total_strings - Validator.found_missing_lang}/{Validator.total_strings}")
    if Validator.errors > 0:
        print(f"Errors: {Validator.errors}")
        sys.exit(1)
    else:
        print("No errors found")
    if USE_COLORAMA:
        colorama.deinit()
