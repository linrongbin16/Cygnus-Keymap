#!/usr/bin/env python3

import json
import logging
import typing


KeyIconsMap = {
    "LGui": "$$mdi.apple-keyboard-command$$",
    "RGui": "$$mdi.apple-keyboard-command$$",
    "LShift": "$$mdi.apple-keyboard-shift$$",
    "RShift": "$$mdi.apple-keyboard-shift$$",
    "LSFT": "$$mdi.apple-keyboard-shift$$",
    "RSFT": "$$mdi.apple-keyboard-shift$$",
    "LCtrl": "$$mdi.apple-keyboard-control$$",
    "RCtrl": "$$mdi.apple-keyboard-control$$",
    "LCTL": "$$mdi.apple-keyboard-control$$",
    "RCTL": "$$mdi.apple-keyboard-control$$",
    "LAlt": "$$mdi.apple-keyboard-option$$",
    "RAlt": "$$mdi.apple-keyboard-option$$",
    "Bksp": "$$mdi.backspace-outline$$",
    "Tab": "$$mdi.keyboard-tab$$",
    "Space": "$$mdi.keyboard-space$$",
    "Enter": "$$mdi.keyboard-return$$",
    "Left": "$$mdi.arrow-left$$",
    "Up": "$$mdi.arrow-up$$",
    "Down": "$$mdi.arrow-down$$",
    "Right": "$$mdi.arrow-right$$",
}

def add_keycode_icons(inputs: list[str]) -> list[str]:
    outputs = []
    for line in inputs:
        result = None
        try:
            for kname, kicon in KeyIconsMap.items():
                if line.strip().startswith(f"- {kname }"):
                    result = line.replace(kname, kicon)
                    logging.debug(f"Replace mac-style icons: {kname} => {kicon}")
                    logging.debug(f"Line: {result}")
                    break
        except Exception as e:
            logging.error(f"Failed to replace mac-style icons for line: {line}")
            logging.error(e, exc_info=True)

        if not result:
            result = line
        outputs.append(result)
    return outputs


def is_json_item(line: str) -> bool:
    if not line.strip().startswith("-"):
        return False
    striped_line = line.strip()
    if not striped_line[1:].strip().startswith("{"):
        return False
    if not striped_line[-1:].strip().startswith("}"):
        return False
    return True


def json_to_string(o: typing.Any) -> str:
    return json.dumps(o, sort_keys=True, separators=(",", ":"))


def json_from_string(s: str) -> dict:
    return json.loads(s)


def replace_json_item(line: str, o: typing.Any) -> str:
    prefix = line.find("-")
    result = "".join([" " for i in range(prefix)]) + f"- " + json_to_string(o) + "\n"
    return result


def remove_s_symbols(inputs: list[str]) -> list[str]:
    RemoveSymbols = ["LSFT+", '"', "_", "+", "{", "}"]
    outputs = []
    for line in inputs:
        result = None
        if is_json_item(line):
            try:
                for symbol in RemoveSymbols:
                    line_json_data = json_from_string(line.replace("-", "", 1).strip())
                    if "s" in line_json_data and line_json_data["s"] == symbol:
                        line_json_data.pop("s")
                        result = replace_json_item(line, line_json_data)
                        logging.debug(f"Remove symbols: {symbol}")
                        logging.debug(f"Line: {result}")
                        break
            except Exception as e:
                logging.error(f"Failed to remove symbols for line: {line}")
                logging.error(e, exc_info=True)
        if not result:
            result = line
        outputs.append(result)

    return outputs


def replace_t_symbols(inputs: list[str]) -> list[str]:
    ReplaceSymbols = {"}  ]": "]", "{  [": "[", "\"  '": "'"}

    outputs = []
    for line in inputs:
        result = None
        if is_json_item(line):
            try:
                for skey, svalue in ReplaceSymbols.items():
                    line_json_data = json_from_string(line.replace("-", "", 1).strip())
                    if "t" in line_json_data and line_json_data["t"] == skey:
                        line_json_data["t"] = svalue
                        result = replace_json_item(line, line_json_data)
                        logging.debug(f"Replace symbols: {skey} => {svalue}")
                        logging.debug(f"Line: {result}")
                        break
            except Exception as e:
                logging.error(f"Failed to replace symbols for line: {line}")
                logging.error(e, exc_info=True)
        if not result:
            result = line
        outputs.append(result)

    return outputs


def remove_s_symbols_for_combos(inputs: list[str]) -> list[str]:
    RemoveSymbols = ["LSFT+", "{", "}"]

    is_combos = False
    outputs = []
    for line in inputs:
        result = None
        if line.strip().startswith("combos"):
            is_combos = True
        if is_combos and is_json_item(line):
            try:
                for symbol in RemoveSymbols:
                    line_json_data = json_from_string(line.replace("-", "", 1).strip())
                    if (
                        "k" in line_json_data
                        and "s" in line_json_data["k"]
                        and line_json_data["k"]["s"] == symbol
                    ):
                        line_json_data["k"].pop("s")
                        result = replace_json_item(line, line_json_data)
                        logging.debug(f"Remove symbols for combo: {symbol}")
                        logging.debug(f"Line: {result}")
                        break
            except Exception as e:
                logging.error(f"Failed to remove symbols for combo line: {line}")
                logging.error(e, exc_info=True)
        if not result:
            result = line
        outputs.append(result)

    return outputs


def add_keycode_icons_for_combos(inputs: list[str]) -> list[str]:
    is_combos = False
    outputs = []
    for line in inputs:
        result = None
        if line.strip().startswith("combos"):
            is_combos = True
        if is_combos and is_json_item(line):
            try:
                line_json_data = json_from_string(line.replace("-", "", 1).strip())
                for kname, kicon in KeyIconsMap.items():
                    if (
                        "k" in line_json_data
                        and line_json_data["k"] == kname
                    ):
                        line_json_data["k"] = kicon
                        result = replace_json_item(line, line_json_data)
                        logging.debug(f"Replace mac-style icon for combo: {kname} => {kicon}")
                        logging.debug(f"Line: {result}")
                        break
            except Exception as e:
                logging.error(f"Failed to replace mac-style icon for combo line: {line}")
                logging.error(e, exc_info=True)
 
        if not result:
            result = line
        outputs.append(result)
    return outputs
    

if __name__ == "__main__":
    logging.basicConfig(format="%(levelname)s - %(message)s", level=logging.DEBUG)
    with open("vail-layout.yml", "r") as src:
        lines = src.readlines()
        lines = add_keycode_icons(lines)
        lines = remove_s_symbols(lines)
        lines = replace_t_symbols(lines)
        lines = remove_s_symbols_for_combos(lines)
        lines = add_keycode_icons_for_combos(lines)
        with open("vail-layout-processed.yml", "w") as dst:
            dst.writelines(lines)
