import json
import os

from jira import JIRA


def get_resource_type(parameters):
    keys = parameters.keys()
    if (
            "count" in keys and
            "instance_type" in keys and
            "ebs_optimized" in keys and
            "disable_api_termination" in keys
    ):
        return "EC2"
    elif (
            "name" in keys and
            "security_groups" in keys and
            "internal" in keys and
            "idle_timeout" in keys and
            "enable_deletion_protection" in keys
    ):
        return "ALB"
    elif (
            "name" in keys and
            "port" in keys and
            "protocol" in keys and
            "deregistration_delay" in keys
    ):
        return "Target Group"
    elif (
            "port" in keys and
            "protocol" in keys
    ):
        return "Listener"
    elif (
            "identifier" in keys and
            "allocated_storage" in keys and
            "allow_major_version_upgrade" in keys and
            "auto_minor_version_upgrade" in keys and
            "engine_version" in keys and
            "instance_class" in keys and
            "maintenance_window" in keys
    ):
        return "RDS Postgres"


def get_text_between(s, word, offset=0):
    try:
        start = s.index(word, offset) + len(word)
        end = s.index(word, start)
        return s[start:end], end + 1
    except ValueError:
        return "", 0


def parsing(input_data):
    open_bracket_indexes = []
    for x in range(len(input_data)):
        if len(input_data[x]) == 2:
            if "{" in input_data[x][1]:
                open_bracket_indexes.append(x)
        elif len(input_data[x]) == 1:
            if "{" in input_data[x][0]:
                open_bracket_indexes.append(x)
    close_bracket_indexes = []
    for x in range(len(input_data)):
        if len(input_data[x]) == 1 and "}" in input_data[x][0]:
            close_bracket_indexes.append(x)
    if len(open_bracket_indexes) != len(close_bracket_indexes):
        raise IndexError("Don't have matching bracket")

    kvs = {}
    offset = 0
    for x in range(len(open_bracket_indexes)):
        nested_data = input_data[open_bracket_indexes[x] - offset:close_bracket_indexes[x] - offset]
        del input_data[open_bracket_indexes[x] - offset:close_bracket_indexes[x] + 1 - offset]
        offset = offset + close_bracket_indexes[x] - open_bracket_indexes[x] + 1
        kvs[nested_data[0][0].replace("{", "").strip()] = formatting(nested_data[1:])
    return {**kvs, **formatting(input_data)}


def formatting(key_value):
    keys = {}
    for kv in key_value:
        if len(kv) != 2:
            continue
        keys[kv[0].strip().replace("\"", "").replace("'", "")] = kv[1].strip().replace("\"", "").replace("'", "")
    return keys


def get_all_codes(ticket_id):
    config_file = os.getenv("HOME") + "/.opscli/config.json"

    with open(config_file) as json_data:
        config = json.load(json_data)

    client = JIRA(
        server=config["jira"]["server"],
        basic_auth=(
            config["jira"]["username"],
            config["jira"]["password"]
        ),
        max_retries=1
    )
    client.project(config["jira"]["project"])
    description = client.issue(id=ticket_id).fields.description
    codes = []
    offset = 0
    while True:
        return_value, new_offset = get_text_between(description, "{code}", offset=offset)
        if return_value != "":
            key_value = list(
                map(
                    lambda x: x.split("="),
                    filter(
                        None,
                        return_value.split("\r\n")
                    )
                )
            )
            parsed = parsing(key_value)
            codes.append(parsed)
            offset = new_offset
        else:
            break
    return list(filter(None, codes))


if __name__ == "__main__":
    ret = get_all_codes("TOSD-3304")
    for r in ret:
        print(get_resource_type(r))
    print(json.dumps(ret, indent=4))
