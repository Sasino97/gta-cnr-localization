import argparse
import json
import sys
import xml.dom.minidom
import xml.sax
import re

COLORAMA_INSTALLED = True
DOMINATE_INSTALLED  = True


try:
    import colorama
except ModuleNotFoundError:
    COLORAMA_INSTALLED = False

try:
    import dominate
    import dominate.tags
except ModuleNotFoundError:
    DOMINATE_INSTALLED = False

GTA_HUD_COLORS = {
    "HUD_COLOUR_PURE_WHITE": "rgba(255, 255, 255, 255)",
    "HUD_COLOUR_WHITE": "rgba(240, 240, 240, 255)",
    "HUD_COLOUR_BLACK": "rgba(0, 0, 0, 255)",
    "HUD_COLOUR_GREY": "rgba(155, 155, 155, 255)",
    "HUD_COLOUR_GREYLIGHT": "rgba(205, 205, 205, 255)",
    "HUD_COLOUR_GREYDARK": "rgba(77, 77, 77, 255)",
    "HUD_COLOUR_RED": "rgba(224, 50, 50, 255)",
    "HUD_COLOUR_REDLIGHT": "rgba(240, 153, 153, 255)",
    "HUD_COLOUR_REDDARK": "rgba(112, 25, 25, 255)",
    "HUD_COLOUR_BLUE": "rgba(93, 182, 229, 255)",
    "HUD_COLOUR_BLUELIGHT": "rgba(174, 219, 242, 255)",
    "HUD_COLOUR_BLUEDARK": "rgba(47, 92, 115, 255)",
    "HUD_COLOUR_YELLOW": "rgba(240, 200, 80, 255)",
    "HUD_COLOUR_YELLOWLIGHT": "rgba(254, 235, 169, 255)",
    "HUD_COLOUR_YELLOWDARK": "rgba(126, 107, 41, 255)",
    "HUD_COLOUR_ORANGE": "rgba(255, 133, 85, 255)",
    "HUD_COLOUR_ORANGELIGHT": "rgba(255, 194, 170, 255)",
    "HUD_COLOUR_ORANGEDARK": "rgba(127, 66, 42, 255)",
    "HUD_COLOUR_GREEN": "rgba(114, 204, 114, 255)",
    "HUD_COLOUR_GREENLIGHT": "rgba(185, 230, 185, 255)",
    "HUD_COLOUR_GREENDARK": "rgba(57, 102, 57, 255)",
    "HUD_COLOUR_PURPLE": "rgba(132, 102, 226, 255)",
    "HUD_COLOUR_PURPLELIGHT": "rgba(192, 179, 239, 255)",
    "HUD_COLOUR_PURPLEDARK": "rgba(67, 57, 111, 255)",
    "HUD_COLOUR_PINK": "rgba(203, 54, 148, 255)",
    "HUD_COLOUR_RADAR_HEALTH": "rgba(53, 154, 71, 255)",
    "HUD_COLOUR_RADAR_ARMOUR": "rgba(93, 182, 229, 255)",
    "HUD_COLOUR_RADAR_DAMAGE": "rgba(235, 36, 39, 255)",
    "HUD_COLOUR_NET_PLAYER1": "rgba(194, 80, 80, 255)",
    "HUD_COLOUR_NET_PLAYER2": "rgba(156, 110, 175, 255)",
    "HUD_COLOUR_NET_PLAYER3": "rgba(255, 123, 196, 255)",
    "HUD_COLOUR_NET_PLAYER4": "rgba(247, 159, 123, 255)",
    "HUD_COLOUR_NET_PLAYER5": "rgba(178, 144, 132, 255)",
    "HUD_COLOUR_NET_PLAYER6": "rgba(141, 206, 167, 255)",
    "HUD_COLOUR_NET_PLAYER7": "rgba(113, 169, 175, 255)",
    "HUD_COLOUR_NET_PLAYER8": "rgba(211, 209, 231, 255)",
    "HUD_COLOUR_NET_PLAYER9": "rgba(144, 127, 153, 255)",
    "HUD_COLOUR_NET_PLAYER10": "rgba(106, 196, 191, 255)",
    "HUD_COLOUR_NET_PLAYER11": "rgba(214, 196, 153, 255)",
    "HUD_COLOUR_NET_PLAYER12": "rgba(234, 142, 80, 255)",
    "HUD_COLOUR_NET_PLAYER13": "rgba(152, 203, 234, 255)",
    "HUD_COLOUR_NET_PLAYER14": "rgba(178, 98, 135, 255)",
    "HUD_COLOUR_NET_PLAYER15": "rgba(144, 142, 122, 255)",
    "HUD_COLOUR_NET_PLAYER16": "rgba(166, 117, 94, 255)",
    "HUD_COLOUR_NET_PLAYER17": "rgba(175, 168, 168, 255)",
    "HUD_COLOUR_NET_PLAYER18": "rgba(232, 142, 155, 255)",
    "HUD_COLOUR_NET_PLAYER19": "rgba(187, 214, 91, 255)",
    "HUD_COLOUR_NET_PLAYER20": "rgba(12, 123, 86, 255)",
    "HUD_COLOUR_NET_PLAYER21": "rgba(123, 196, 255, 255)",
    "HUD_COLOUR_NET_PLAYER22": "rgba(171, 60, 230, 255)",
    "HUD_COLOUR_NET_PLAYER23": "rgba(206, 169, 13, 255)",
    "HUD_COLOUR_NET_PLAYER24": "rgba(71, 99, 173, 255)",
    "HUD_COLOUR_NET_PLAYER25": "rgba(42, 166, 185, 255)",
    "HUD_COLOUR_NET_PLAYER26": "rgba(186, 157, 125, 255)",
    "HUD_COLOUR_NET_PLAYER27": "rgba(201, 225, 255, 255)",
    "HUD_COLOUR_NET_PLAYER28": "rgba(240, 240, 150, 255)",
    "HUD_COLOUR_NET_PLAYER29": "rgba(237, 140, 161, 255)",
    "HUD_COLOUR_NET_PLAYER30": "rgba(249, 138, 138, 255)",
    "HUD_COLOUR_NET_PLAYER31": "rgba(252, 239, 166, 255)",
    "HUD_COLOUR_NET_PLAYER32": "rgba(240, 240, 240, 255)",
    "HUD_COLOUR_SIMPLEBLIP_DEFAULT": "rgba(159, 201, 166, 255)",
    "HUD_COLOUR_MENU_BLUE": "rgba(140, 140, 140, 255)",
    "HUD_COLOUR_MENU_GREY_LIGHT": "rgba(140, 140, 140, 255)",
    "HUD_COLOUR_MENU_BLUE_EXTRA_DARK": "rgba(40, 40, 40, 255)",
    "HUD_COLOUR_MENU_YELLOW": "rgba(240, 160, 0, 255)",
    "HUD_COLOUR_MENU_YELLOW_DARK": "rgba(240, 160, 0, 255)",
    "HUD_COLOUR_MENU_GREEN": "rgba(240, 160, 0, 255)",
    "HUD_COLOUR_MENU_GREY": "rgba(140, 140, 140, 255)",
    "HUD_COLOUR_MENU_GREY_DARK": "rgba(60, 60, 60, 255)",
    "HUD_COLOUR_MENU_HIGHLIGHT": "rgba(30, 30, 30, 255)",
    "HUD_COLOUR_MENU_STANDARD": "rgba(140, 140, 140, 255)",
    "HUD_COLOUR_MENU_DIMMED": "rgba(75, 75, 75, 255)",
    "HUD_COLOUR_MENU_EXTRA_DIMMED": "rgba(50, 50, 50, 255)",
    "HUD_COLOUR_BRIEF_TITLE": "rgba(95, 95, 95, 255)",
    "HUD_COLOUR_MID_GREY_MP": "rgba(100, 100, 100, 255)",
    "HUD_COLOUR_NET_PLAYER1_DARK": "rgba(93, 39, 39, 255)",
    "HUD_COLOUR_NET_PLAYER2_DARK": "rgba(77, 55, 89, 255)",
    "HUD_COLOUR_NET_PLAYER3_DARK": "rgba(124, 62, 99, 255)",
    "HUD_COLOUR_NET_PLAYER4_DARK": "rgba(120, 80, 80, 255)",
    "HUD_COLOUR_NET_PLAYER5_DARK": "rgba(87, 72, 66, 255)",
    "HUD_COLOUR_NET_PLAYER6_DARK": "rgba(74, 103, 83, 255)",
    "HUD_COLOUR_NET_PLAYER7_DARK": "rgba(60, 85, 88, 255)",
    "HUD_COLOUR_NET_PLAYER8_DARK": "rgba(105, 105, 64, 255)",
    "HUD_COLOUR_NET_PLAYER9_DARK": "rgba(72, 63, 76, 255)",
    "HUD_COLOUR_NET_PLAYER10_DARK": "rgba(53, 98, 95, 255)",
    "HUD_COLOUR_NET_PLAYER11_DARK": "rgba(107, 98, 76, 255)",
    "HUD_COLOUR_NET_PLAYER12_DARK": "rgba(117, 71, 40, 255)",
    "HUD_COLOUR_NET_PLAYER13_DARK": "rgba(76, 101, 117, 255)",
    "HUD_COLOUR_NET_PLAYER14_DARK": "rgba(65, 35, 47, 255)",
    "HUD_COLOUR_NET_PLAYER15_DARK": "rgba(72, 71, 61, 255)",
    "HUD_COLOUR_NET_PLAYER16_DARK": "rgba(85, 58, 47, 255)",
    "HUD_COLOUR_NET_PLAYER17_DARK": "rgba(87, 84, 84, 255)",
    "HUD_COLOUR_NET_PLAYER18_DARK": "rgba(116, 71, 77, 255)",
    "HUD_COLOUR_NET_PLAYER19_DARK": "rgba(93, 107, 45, 255)",
    "HUD_COLOUR_NET_PLAYER20_DARK": "rgba(6, 61, 43, 255)",
    "HUD_COLOUR_NET_PLAYER21_DARK": "rgba(61, 98, 127, 255)",
    "HUD_COLOUR_NET_PLAYER22_DARK": "rgba(85, 30, 115, 255)",
    "HUD_COLOUR_NET_PLAYER23_DARK": "rgba(103, 84, 6, 255)",
    "HUD_COLOUR_NET_PLAYER24_DARK": "rgba(35, 49, 86, 255)",
    "HUD_COLOUR_NET_PLAYER25_DARK": "rgba(21, 83, 92, 255)",
    "HUD_COLOUR_NET_PLAYER26_DARK": "rgba(93, 98, 62, 255)",
    "HUD_COLOUR_NET_PLAYER27_DARK": "rgba(100, 112, 127, 255)",
    "HUD_COLOUR_NET_PLAYER28_DARK": "rgba(120, 120, 75, 255)",
    "HUD_COLOUR_NET_PLAYER29_DARK": "rgba(152, 76, 93, 255)",
    "HUD_COLOUR_NET_PLAYER30_DARK": "rgba(124, 69, 69, 255)",
    "HUD_COLOUR_NET_PLAYER31_DARK": "rgba(10, 43, 50, 255)",
    "HUD_COLOUR_NET_PLAYER32_DARK": "rgba(95, 95, 10, 255)",
    "HUD_COLOUR_BRONZE": "rgba(180, 130, 97, 255)",
    "HUD_COLOUR_SILVER": "rgba(150, 153, 161, 255)",
    "HUD_COLOUR_GOLD": "rgba(214, 181, 99, 255)",
    "HUD_COLOUR_PLATINUM": "rgba(166, 221, 190, 255)",
    "HUD_COLOUR_GANG1": "rgba(29, 100, 153, 255)",
    "HUD_COLOUR_GANG2": "rgba(214, 116, 15, 255)",
    "HUD_COLOUR_GANG3": "rgba(135, 125, 142, 255)",
    "HUD_COLOUR_GANG4": "rgba(229, 119, 185, 255)",
    "HUD_COLOUR_SAME_CREW": "rgba(252, 239, 166, 255)",
    "HUD_COLOUR_FREEMODE": "rgba(45, 110, 185, 255)",
    "HUD_COLOUR_PAUSE_BG": "rgba(0, 0, 0, 186)",
    "HUD_COLOUR_FRIENDLY": "rgba(93, 182, 229, 255)",
    "HUD_COLOUR_ENEMY": "rgba(194, 80, 80, 255)",
    "HUD_COLOUR_LOCATION": "rgba(240, 200, 80, 255)",
    "HUD_COLOUR_PICKUP": "rgba(114, 204, 114, 255)",
    "HUD_COLOUR_PAUSE_SINGLEPLAYER": "rgba(114, 204, 114, 255)",
    "HUD_COLOUR_FREEMODE_DARK": "rgba(22, 55, 92, 255)",
    "HUD_COLOUR_INACTIVE_MISSION": "rgba(154, 154, 154, 255)",
    "HUD_COLOUR_DAMAGE": "rgba(194, 80, 80, 255)",
    "HUD_COLOUR_PINKLIGHT": "rgba(252, 115, 201, 255)",
    "HUD_COLOUR_PM_MITEM_HIGHLIGHT": "rgba(252, 177, 49, 255)",
    "HUD_COLOUR_SCRIPT_VARIABLE": "rgba(0, 0, 0, 255)",
    "HUD_COLOUR_YOGA": "rgba(109, 247, 204, 255)",
    "HUD_COLOUR_TENNIS": "rgba(241, 101, 34, 255)",
    "HUD_COLOUR_GOLF": "rgba(214, 189, 97, 255)",
    "HUD_COLOUR_SHOOTING_RANGE": "rgba(112, 25, 25, 255)",
    "HUD_COLOUR_FLIGHT_SCHOOL": "rgba(47, 92, 115, 255)",
    "HUD_COLOUR_NORTH_BLUE": "rgba(93, 182, 229, 255)",
    "HUD_COLOUR_SOCIAL_CLUB": "rgba(234, 153, 28, 255)",
    "HUD_COLOUR_PLATFORM_BLUE": "rgba(11, 55, 123, 255)",
    "HUD_COLOUR_PLATFORM_GREEN": "rgba(146, 200, 62, 255)",
    "HUD_COLOUR_PLATFORM_GREY": "rgba(234, 153, 28, 255)",
    "HUD_COLOUR_FACEBOOK_BLUE": "rgba(66, 89, 148, 255)",
    "HUD_COLOUR_INGAME_BG": "rgba(0, 0, 0, 186)",
    "HUD_COLOUR_DARTS": "rgba(114, 204, 114, 255)",
    "HUD_COLOUR_WAYPOINT": "rgba(164, 76, 242, 255)",
    "HUD_COLOUR_MICHAEL": "rgba(101, 180, 212, 255)",
    "HUD_COLOUR_FRANKLIN": "rgba(171, 237, 171, 255)",
    "HUD_COLOUR_TREVOR": "rgba(255, 163, 87, 255)",
    "HUD_COLOUR_GOLF_P1": "rgba(240, 240, 240, 255)",
    "HUD_COLOUR_GOLF_P2": "rgba(235, 239, 30, 255)",
    "HUD_COLOUR_GOLF_P3": "rgba(255, 149, 14, 255)",
    "HUD_COLOUR_GOLF_P4": "rgba(246, 60, 161, 255)",
    "HUD_COLOUR_WAYPOINTLIGHT": "rgba(210, 166, 249, 255)",
    "HUD_COLOUR_WAYPOINTDARK": "rgba(82, 38, 121, 255)",
    "HUD_COLOUR_PANEL_LIGHT": "rgba(0, 0, 0, 77)",
    "HUD_COLOUR_MICHAEL_DARK": "rgba(72, 103, 116, 255)",
    "HUD_COLOUR_FRANKLIN_DARK": "rgba(85, 118, 85, 255)",
    "HUD_COLOUR_TREVOR_DARK": "rgba(127, 81, 43, 255)",
    "HUD_COLOUR_OBJECTIVE_ROUTE": "rgba(240, 200, 80, 255)",
    "HUD_COLOUR_PAUSEMAP_TINT": "rgba(0, 0, 0, 215)",
    "HUD_COLOUR_PAUSE_DESELECT": "rgba(100, 100, 100, 127)",
    "HUD_COLOUR_PM_WEAPONS_PURCHASABLE": "rgba(45, 110, 185, 255)",
    "HUD_COLOUR_PM_WEAPONS_LOCKED": "rgba(240, 240, 240, 191)",
    "HUD_COLOUR_END_SCREEN_BG": "rgba(0, 0, 0, 186)",
    "HUD_COLOUR_CHOP": "rgba(224, 50, 50, 255)",
    "HUD_COLOUR_PAUSEMAP_TINT_HALF": "rgba(0, 0, 0, 215)",
    "HUD_COLOUR_NORTH_BLUE_OFFICIAL": "rgba(0, 71, 133, 255)",
    "HUD_COLOUR_SCRIPT_VARIABLE_2": "rgba(0, 0, 0, 255)",
    "HUD_COLOUR_H": "rgba(33, 118, 37, 255)",
    "HUD_COLOUR_HDARK": "rgba(37, 102, 40, 255)",
    "HUD_COLOUR_T": "rgba(234, 153, 28, 255)",
    "HUD_COLOUR_TDARK": "rgba(225, 140, 8, 255)",
    "HUD_COLOUR_HSHARD": "rgba(20, 40, 0, 255)",
    "HUD_COLOUR_CONTROLLER_MICHAEL": "rgba(48, 255, 255, 255)",
    "HUD_COLOUR_CONTROLLER_FRANKLIN": "rgba(48, 255, 0, 255)",
    "HUD_COLOUR_CONTROLLER_TREVOR": "rgba(176, 80, 0, 255)",
    "HUD_COLOUR_CONTROLLER_CHOP": "rgba(127, 0, 0, 255)",
    "HUD_COLOUR_VIDEO_EDITOR_VIDEO": "rgba(53, 166, 224, 255)",
    "HUD_COLOUR_VIDEO_EDITOR_AUDIO": "rgba(162, 79, 157, 255)",
    "HUD_COLOUR_VIDEO_EDITOR_TEXT": "rgba(104, 192, 141, 255)",
    "HUD_COLOUR_HB_BLUE": "rgba(29, 100, 153, 255)",
    "HUD_COLOUR_HB_YELLOW": "rgba(234, 153, 28, 255)",
    "HUD_COLOUR_VIDEO_EDITOR_SCORE": "rgba(240, 160, 1, 255)",
    "HUD_COLOUR_VIDEO_EDITOR_AUDIO_FADEOUT": "rgba(59, 34, 57, 255)",
    "HUD_COLOUR_VIDEO_EDITOR_TEXT_FADEOUT": "rgba(41, 68, 53, 255)",
    "HUD_COLOUR_VIDEO_EDITOR_SCORE_FADEOUT": "rgba(82, 58, 10, 255)",
    "HUD_COLOUR_HEIST_BACKGROUND": "rgba(37, 102, 40, 186)",
    "HUD_COLOUR_VIDEO_EDITOR_AMBIENT": "rgba(240, 200, 80, 255)",
    "HUD_COLOUR_VIDEO_EDITOR_AMBIENT_FADEOUT": "rgba(80, 70, 34, 255)",
    "HUD_COLOUR_VIDEO_EDITOR_AMBIENT_DARK": "rgba(255, 133, 85, 255)",
    "HUD_COLOUR_VIDEO_EDITOR_AMBIENT_LIGHT": "rgba(255, 194, 170, 255)",
    "HUD_COLOUR_VIDEO_EDITOR_AMBIENT_MID": "rgba(255, 133, 85, 255)",
    "HUD_COLOUR_LOW_FLOW": "rgba(240, 200, 80, 255)",
    "HUD_COLOUR_LOW_FLOW_DARK": "rgba(126, 107, 41, 255)",
    "HUD_COLOUR_G1": "rgba(247, 159, 123, 255)",
    "HUD_COLOUR_G2": "rgba(226, 134, 187, 255)",
    "HUD_COLOUR_G3": "rgba(239, 238, 151, 255)",
    "HUD_COLOUR_G4": "rgba(113, 169, 175, 255)",
    "HUD_COLOUR_G5": "rgba(160, 140, 193, 255)",
    "HUD_COLOUR_G6": "rgba(141, 206, 167, 255)",
    "HUD_COLOUR_G7": "rgba(181, 214, 234, 255)",
    "HUD_COLOUR_G8": "rgba(178, 144, 132, 255)",
    "HUD_COLOUR_G9": "rgba(0, 132, 114, 255)",
    "HUD_COLOUR_G10": "rgba(216, 85, 117, 255)",
    "HUD_COLOUR_G11": "rgba(30, 100, 152, 255)",
    "HUD_COLOUR_G12": "rgba(43, 181, 117, 255)",
    "HUD_COLOUR_G13": "rgba(233, 141, 79, 255)",
    "HUD_COLOUR_G14": "rgba(137, 210, 215, 255)",
    "HUD_COLOUR_G15": "rgba(134, 125, 141, 255)",
    "HUD_COLOUR_ADVERSARY": "rgba(109, 34, 33, 255)",
    "HUD_COLOUR_DEGEN_RED": "rgba(255, 0, 0, 255)",
    "HUD_COLOUR_DEGEN_YELLOW": "rgba(255, 255, 0, 255)",
    "HUD_COLOUR_DEGEN_GREEN": "rgba(0, 255, 0, 255)",
    "HUD_COLOUR_DEGEN_CYAN": "rgba(0, 255, 255, 255)",
    "HUD_COLOUR_DEGEN_BLUE": "rgba(0, 0, 255, 255)",
    "HUD_COLOUR_DEGEN_MAGENTA": "rgba(255, 0, 255, 255)",
    "HUD_COLOUR_STUNT_1": "rgba(38, 136, 234, 255)",
    "HUD_COLOUR_STUNT_2": "rgba(224, 50, 50, 255)",
    "HUD_COLOUR_SPECIAL_RACE_SERIES": "rgba(154, 178, 54, 255)",
    "HUD_COLOUR_SPECIAL_RACE_SERIES_DARK": "rgba(93, 107, 45, 255)",
    "HUD_COLOUR_CS": "rgba(206, 169, 13, 255)",
    "HUD_COLOUR_CS_DARK": "rgba(103, 84, 6, 255)",
    "HUD_COLOUR_TECH_GREEN": "rgba(0, 151, 151, 255)",
    "HUD_COLOUR_TECH_GREEN_DARK": "rgba(5, 119, 113, 255)",
    "HUD_COLOUR_TECH_RED": "rgba(151, 0, 0, 255)",
    "HUD_COLOUR_TECH_GREEN_VERY_DARK": "rgba(0, 40, 40, 255)",
    "HUD_COLOUR_PLACEHOLDER_01": "rgba(255, 255, 255, 255)",
    "HUD_COLOUR_PLACEHOLDER_02": "rgba(255, 255, 255, 255)",
    "HUD_COLOUR_PLACEHOLDER_03": "rgba(255, 255, 255, 255)",
    "HUD_COLOUR_PLACEHOLDER_04": "rgba(255, 255, 255, 255)",
    "HUD_COLOUR_PLACEHOLDER_05": "rgba(255, 255, 255, 255)",
    "HUD_COLOUR_PLACEHOLDER_06": "rgba(255, 255, 255, 255)",
    "HUD_COLOUR_PLACEHOLDER_07": "rgba(255, 255, 255, 255)",
    "HUD_COLOUR_PLACEHOLDER_08": "rgba(255, 255, 255, 255)",
    "HUD_COLOUR_PLACEHOLDER_09": "rgba(255, 255, 255, 255)",
    "HUD_COLOUR_PLACEHOLDER_10": "rgba(255, 255, 255, 255)"
}

GTA_FORMAT_REPLACEMENT_TABLE = [
    [r"~r~", '~HUD_COLOUR_RED~'],
    [r"~g~", '~HUD_COLOUR_GREEN~'],
    [r"~b~", '~HUD_COLOUR_BLUE~'],
    [r"~f~", '~HUD_COLOUR_FRIENDLY~'],
    [r"~y~", '~HUD_COLOUR_YELLOW~'],
    [r"~c~", '~HUD_COLOUR_MENU_GREY~'],
    [r"~t~", '~HUD_COLOUR_MENU_GREY~'],
    [r"~o~", '~HUD_COLOUR_ORANGE~'],
    [r"~p~", '~HUD_COLOUR_PURPLE~'],
    [r"~q~", '~HUD_COLOUR_PINK~'],
    [r"~m~", '~HUD_COLOUR_MID_GREY_MP~'],
    [r"~l~", '~HUD_COLOUR_BLACK~'],
    [r"~d~", '~HUD_COLOUR_BLUEDARK~'],
    [r"~s~", '~HUD_COLOUR_GREYLIGHT~']
]

def get_text_from_node(node: xml.dom.minidom.Node):
    return "".join(t.nodeValue for t in node.childNodes if t.nodeType == t.TEXT_NODE)

def regex_replace_multiple(text: str, replacement_table: list[list[str]]) -> str:
    for replacement in replacement_table:
        text = re.sub(replacement[0], replacement[1], text)
    return text

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
    preview_formatting = False
    main_doc = None

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
        if COLORAMA_INSTALLED:
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
        if COLORAMA_INSTALLED:
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
    
    
    def setup_html_doc():
        if Validator.preview_formatting:
            Validator.main_doc = dominate.document(title="Text formatting preview")
            with Validator.main_doc.head:
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
    

    def add_formatted_text_to_html(text: str):
        text = regex_replace_multiple(text, GTA_FORMAT_REPLACEMENT_TABLE)
        GROUP_REGEX = r"~h~|~n~|~bold~|~italic~|\(C\)|\(\/C\)|~HUD_COLOUR_.+?~|~HC_.+?~|~CC_[0-9]{1,3}_[0-9]{1,3}_[0-9]{1,3}~"
        bolded = False
        italic = False
        color = "rgb(205,205,205)"
        condensed = 0
        new_line = False
        text_fragments = re.split(GROUP_REGEX, text)
        matchedActions = re.findall(GROUP_REGEX, text)
        with Validator.main_doc.body:
            if text_fragments[0] != "":
                dominate.tags.span(text_fragments[0], style=f"color: {color};")
        for i, fragment in enumerate(text_fragments[1:]):
            formatting = matchedActions[i]
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
                    HUDColorMatches = re.findall(r"(?<=~)(HUD_COLOUR_.+?)(?=~)|(?<=~)(HC_.+?)(?=~)", formatting)
                    if HUDColorMatches:
                        color = GTA_HUD_COLORS[HUDColorMatches[0][0]]
                    CustomColorMatches = re.findall(r"(?<=~CC_)([0-9]{1,3}_[0-9]{1,3}_[0-9]{1,3})(?=~)", formatting)
                    if CustomColorMatches:
                        color = f'rgba(${CustomColorMatches[0].split("_").join(",")})'
            classes = []
            if (condensed > 0):
                classes.append("condensed")
            if bolded:
                classes.append("bolded")
            style = ""
            if italic:
                style += "font-style: italic;"
            style += f"color: {color};"
            with Validator.main_doc.body:
                if fragment != "":
                    with dominate.tags.span(fragment):
                        if classes:
                            dominate.tags.attr(cls=' '.join(classes), style=style)
                        else:
                            dominate.tags.attr(style=style)
                if new_line:
                    dominate.tags.br()


    @staticmethod
    def check_xml_files():
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
            if DOMINATE_INSTALLED and Validator.preview_formatting:
                with Validator.main_doc.body:
                    dominate.tags.h2(element_found_id)
        found_langs: list[str] = []
        lang_attrib =  "xml:lang"
        should_end_with_format = None
        required_text_formatting = set()
        required_variables = []
        good_string_entries = []
        FORMAT_REGEX = r"~[s,b,r,n,y,p,g,o,h,c]~"
        VARIABLE_REGEX = r"{[0-9]+}"
        WRONG_PUNCTUATION_REGEX = r"\s[.,?,!]"
        for string_entry in entry.childNodes:
            if isinstance(string_entry, xml.dom.minidom.Text):
                continue
            string_entry: xml.dom.minidom.Element
            if Validator.check_unknown_tag(string_entry, ["String"], path):
                good_string_entries.append(string_entry)
                for key, value in string_entry.attributes.items():
                    if key == lang_attrib:
                        if value == "en-US":
                            found_formats = re.findall(FORMAT_REGEX, get_text_from_node(string_entry))
                            if (len(found_formats)>0):
                                required_text_formatting = set(found_formats)
                                should_end_with_format = found_formats[-1]
                            required_variables = re.findall(VARIABLE_REGEX, get_text_from_node(string_entry))
                        found_langs.append(value)
                    else:
                        Validator.print_error(f"Unknown attribute: {repr(key)}", path, string_entry.parse_position)
        for string_entry in good_string_entries:
            text = get_text_from_node(string_entry)
            current_lang = dict(string_entry.attributes.items()).get(lang_attrib)
            path1 = [*path, current_lang]
            if DOMINATE_INSTALLED and Validator.preview_formatting:
                with Validator.main_doc.body:
                    dominate.tags.h3(current_lang)
                Validator.add_formatted_text_to_html(text)
            found_formats = re.findall(FORMAT_REGEX, text)
            if len(found_formats)>0 and should_end_with_format is not None:
                found_formats_set = set(found_formats)
                invalid_text_formatting = found_formats_set.difference(required_text_formatting)
                missing_text_formatting = required_text_formatting.difference(found_formats_set)
                if invalid_text_formatting:
                    Validator.print_error(f"Found invalid text formatting: {', '.join(invalid_text_formatting)}", path1, string_entry.parse_position)
                if missing_text_formatting:
                    Validator.print_error(f"Missing text formatting: {', '.join(missing_text_formatting)}", path1, string_entry.parse_position)
                found_format = found_formats[-1]
                if found_format != should_end_with_format:
                    Validator.print_error(f"String ends with a wrong format {repr(found_format)}, expected {repr(should_end_with_format)}", path1, string_entry.parse_position)
            found_variables = re.findall(VARIABLE_REGEX, text)
            if len(found_variables) < len(required_variables):
                missing_variables = [var for var in required_variables if var not in found_variables]
                if missing_variables:
                    Validator.print_error(f"Missing variables: {', '.join(missing_variables)}", path1, string_entry.parse_position)
            elif len(found_variables) > len(required_variables):
                unneeded_variables = [var for var in found_variables if var not in required_variables]
                if unneeded_variables:
                    Validator.print_error(f"Found too many variables: {', '.join(unneeded_variables)}", path1, string_entry.parse_position)
            text_without_formatting = re.sub(FORMAT_REGEX, "", text)
            if text_without_formatting.find("~") != -1:
                Validator.print_error(f"Found invalid text formatting (~)", path1, string_entry.parse_position)
            if re.findall(r"\s\s+", text_without_formatting):
                Validator.print_error(f"Found too many spaces between words", path1, string_entry.parse_position)
            if re.findall(WRONG_PUNCTUATION_REGEX, text_without_formatting):
                Validator.print_error(f"Found invalid punctuation mark placement", path1, string_entry.parse_position)
        if (Validator.show_lang is not None) and (Validator.show_lang not in found_langs):
            if Validator.found_missing_lang <= Validator.display_limit:
                Validator.print_warning(f"Missing translation for {repr(Validator.show_lang)}!", path, element_location)
            Validator.found_missing_lang += 1


if __name__ == '__main__':
    if COLORAMA_INSTALLED:
        colorama.init()
    parser = argparse.ArgumentParser(description='Validates localization files')
    parser.add_argument('--show_lang', type=str, help='Show missing language localizations', choices=Validator.supported_langs)
    parser.add_argument('--preview_formatting', action='store_true', help='Show formatted localizations as HTML file')
    parser.add_argument('--display_limit', type=int, default=10, help='Set display limit for missing translations')
    args = parser.parse_args()
    Validator.custom_xml_parser = Validator.setup_xml_parser()
    if args.preview_formatting and DOMINATE_INSTALLED:
        Validator.preview_formatting = True
        Validator.setup_html_doc()
    Validator.display_limit = args.display_limit
    Validator.show_lang = args.show_lang
    with open("index.json", "r", encoding="utf-8") as index_file:
        Validator.xml_files = json.load(index_file)
    Validator.check_xml_files()
    if Validator.show_lang is not None:
        print(f"Total missing translations for {repr(Validator.show_lang)}: {Validator.found_missing_lang}. "
              f"Progress: {Validator.total_strings - Validator.found_missing_lang}/{Validator.total_strings}")
    if Validator.preview_formatting and DOMINATE_INSTALLED:
        with open("preview.html", "w", encoding="utf-8") as file:
            file.write(Validator.main_doc.render(pretty=False))
    if Validator.errors > 0:
        print(f"Errors: {Validator.errors}")
        sys.exit(1)
    else:
        print("No errors found")
    if COLORAMA_INSTALLED:
        colorama.deinit()
