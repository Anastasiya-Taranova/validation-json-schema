import json
from typing import Dict, List

import jsonschema
from loguru import logger

import dirs

JSONPATH = dirs.DIR_TASK_EVENTS
SCHEMAPATH = dirs.DIR_TASK_SCHEMA

JSONFILES = JSONPATH.glob("*.json")
SCHEMAFILES = list(SCHEMAPATH.glob("*.schema.json"))


def load_schemas_map() -> Dict:
    schemas = {}

    for file in SCHEMAFILES:
        with open(file, "r") as f:
            schema = json.load(f)
            if "activity_name" in schema["required"]:
                schemas["workout"] = schema
            elif "cmarkers" in schema["required"]:
                schemas["cmarker"] = schema
            elif "labels" in schema["required"]:
                schemas["labels"] = schema
            else:
                schemas["sleep"] = schema

    return schemas


def load_json(file_path):
    with open(file_path, "r") as src:
        data = json.load(src)
    return data


def select_schema(data: Dict, schemas: Dict) -> Dict:
    default_schema = schemas["sleep"]

    if not data:
        return default_schema

    keys = data.get("data", {}).keys()
    if not keys:
        return default_schema

    if "labels" in keys:
        return schemas["labels"]
    elif "cmarkers" in keys:
        return schemas["cmarker"]
    elif "activity_name" in keys:
        return schemas["workout"]

    return schemas["sleep"]


def build_error_path(error):
    path = "." + ".".join(error.path)
    return path


def convert_error(error):
    path = build_error_path(error)
    if "is a required property" in error.message:
        return f"Missed required field {path}"
    elif "is not of type" in error.message:
        value = error.message.split(" ")[-1]
        return f"Field value in {path} does not match {value} ({error.message})"
    else:
        return error.message


def display_reports(reports: List[Dict]) -> None:
    for report in reports:
        logger.info(f"[ {report['File']} ]")
        logger.info("")
        logger.info(f"Field:   \t{report['Field']}")
        logger.info(f"Result:  \t{report['Result']}")
        logger.info(f"Message: \t{report['Message']}")
        logger.info("")


def generate_report(file_path, /, result="OK", field="OK", message="OK"):
    report = {
        "File": file_path,
        "Result": result,
        "Field": field,
        "Message": message,
    }

    return report


def main():
    schemas = load_schemas_map()

    reports = []

    for data_file in JSONFILES:
        data_file_path = data_file.as_posix()

        try:
            data = load_json(data_file)
            schema = select_schema(data, schemas)
            validator = jsonschema.Draft3Validator(schema)
            errors = list(validator.iter_errors(data))

            if errors:
                for error in errors:
                    message = convert_error(error)
                    error_path = build_error_path(error)
                    report = generate_report(data_file_path, result="ERROR", field=error_path, message=message)
                    reports.append(report)
            else:
                report = generate_report(data_file_path)
                reports.append(report)

        except (KeyError, TypeError):
            report = generate_report(data_file_path, result="NO DATA", field="ALL_DATA", message="NO DATA AVAILABLE")
            reports.append(report)
        except AttributeError:
            report = generate_report(data_file_path, result="NO DATA", field="DATA", message="NOT ENOUGH DATA")
            reports.append(report)

    display_reports(reports)


if __name__ == "__main__":
    main()
