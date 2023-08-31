import xml.etree.ElementTree as ET
import argparse
import json
import sys

USE_COLORAMA = True

try:
    import colorama
except ModuleNotFoundError:
    USE_COLORAMA = False


def find_index_without_spaces(main_string: str, sub_string: str) -> int:
    main_no_space = main_string.replace(" ", "")
    sub_no_space = sub_string.replace(" ", "")    
    index_no_spaces = main_no_space.find(sub_no_space)    
    if index_no_spaces != -1:
        count = 0
        for i, char in enumerate(main_string):
            if char != " ":
                count += 1
                if count == index_no_spaces + 1:
                    return i
    return -1


def rfind_index_without_spaces(main_string: str, sub_string: str) -> int:
    main_no_space = main_string.replace(" ", "")
    sub_no_space = sub_string.replace(" ", "")
    index_no_spaces = main_no_space.rfind(sub_no_space)    
    if index_no_spaces != -1:
        count = 0
        for i, char in enumerate(main_string):
            if char != " ":
                count += 1
                if count == index_no_spaces + 1:
                    return i
    return -1


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
    """
    xml_files: list[str] = []
    supported_langs: list[str] = ["en-US", "de-DE", "fr-FR", "nl-NL", "it-IT", "es-ES", "pt-BR", "pl-PL", "tr-TR", "ar-001", "zh-Hans", "zh-Hant", "hi-Latn", "vi-VN", "th-TH"]
    nsmap = {"xml": "http://www.w3.org/XML/1998/namespace"}
    used_ids: set = set()
    errors: int = 0
    warnings: int = 0
    display_limit: int = 10
    show_lang: str | None = None
    found_missing_lang: int = 0


    @staticmethod
    def get_element_location(element: ET.Element, file_path, reversed_search=False) -> tuple[int]:
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
        element_string = ET.tostring(element).decode()
        element_start = 0
        if reversed_search:
            #Faster but more prone to errors (spaces)
            #element_start = content.rfind(element_string.split("\n")[0])
            element_start = rfind_index_without_spaces(content, element_string.split("\n")[0])
        else:
            #element_start = content.find(element_string.split("\n")[0])
            element_start = find_index_without_spaces(content, element_string.split("\n")[0])        
        # Find the line number and character position
        line_number = content.count('\n', 0, element_start) + 1
        char_position = element_start - content.rfind('\n', 0, element_start)
        # Something went wrong - print the string representation of xml element to find out why
        if char_position<0:
            print(file_path, ET.tostring(element).decode())        
        return line_number, char_position


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
            string += f"[{custom_file_cursor[0]},{custom_file_cursor[1]}]"
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
    def entry_pretty_print(entry: ET.Element) -> str:
        return f"{entry.tag}<Id:{repr(entry.attrib.get('Id'))}>"


    @staticmethod
    def check_unknown_tag(entry: ET.Element, known_tags: list[str], location: list[str])->bool:
        """Checks if an XML element's tag is in the list of known tags.

        Args:
            entry (xml.etree.ElementTree.Element): The XML element to check.
            known_tags (list[str]): List of known tag names.
            location (list[str]): A list of strings representing the location.

        Returns:
            bool: True if the tag is known, False otherwise.
        """
        if entry.tag in known_tags:
            return True
        Validator.print_error(f"Unknown tag: {repr(entry.tag)}, expected one of these: {', '.join(known_tags[:Validator.display_limit])}", location, Validator.get_element_location(entry, location[0]))
        return False


    @staticmethod
    def check_xml_files():
        for file in Validator.xml_files:
            try:
                tree = ET.parse(file)
                root = tree.getroot()
                path = [file, root.tag]
                for child in root:
                    if Validator.check_unknown_tag(child, ["Entry"], path):
                        Validator.check_entries(child, path)
            except (ET.ParseError, FileNotFoundError) as err:    
                Validator.print_error(f"Invalid file: {err}", [file])


    @staticmethod
    def check_entries(entry: ET.Element, path: list[str]):
        element_found_id = entry.attrib.get("Id")
        element_location = Validator.get_element_location(entry, path[0])
        if element_found_id is None:
            Validator.print_error("Found element without id!", path, custom_file_cursor=element_location)
        else:
            if element_found_id in Validator.used_ids:
                Validator.print_error(f"Found element duplicate with id {repr(element_found_id)}!", path, custom_file_cursor=element_location)
            Validator.used_ids.add(element_found_id)
        found_langs: list[str] = []
        lang_attrib =  f"{{{Validator.nsmap['xml']}}}lang"
        for string_entry in entry:
            if Validator.check_unknown_tag(string_entry, ["String"], path):
                for key, value in string_entry.attrib.items():
                    if key==lang_attrib:
                        found_langs.append(value)
                    else:
                        Validator.print_error(f"Unknown attribute: {repr(key)}", path, element_location)
        if Validator.show_lang is not None and Validator.show_lang not in found_langs:
            if Validator.found_missing_lang <= Validator.display_limit:
                Validator.print_warning(f"Missing translation for {repr(Validator.show_lang)}!", path, element_location)
            Validator.found_missing_lang += 1



if __name__ == '__main__':
    if USE_COLORAMA:
        colorama.init()
    parser = argparse.ArgumentParser(description='Validates localization files')
    parser.add_argument('--show_lang', type=str, help='Show missing language localizations')
    parser.add_argument('--display_limit', type=int, default=10, help='Set display limit for missing translations')
    args = parser.parse_args()
    Validator.display_limit = args.display_limit
    if args.show_lang is not None:
        if args.show_lang not in Validator.supported_langs:
            print(f"Unknown language: {args.show_lang}, expected one of these: {', '.join(Validator.supported_langs)}")
        else:
            Validator.show_lang = args.show_lang
    with open("index.json", "r", encoding="utf-8") as index_file:
        Validator.xml_files = json.load(index_file)
    Validator.check_xml_files()
    if (Validator.show_lang is not None):
        print(f"Total missing translations for {repr(Validator.show_lang)}: {Validator.found_missing_lang}")
    if Validator.errors > 0:
        print(f"Errors: {Validator.errors}")
        sys.exit(1)
    else:
        print("No errors found")
    if USE_COLORAMA:
        colorama.deinit()
