#!/usr/bin/env python3

import argparse
import json
import os

from tfgen import VERSION
from tfgen.generator import CodeGenerator
from tfgen.parser import JiraTicketDescriptionParser


def __tfgen(args):
    config_file = os.getenv("HOME") + "/.opscli/config.json"
    with open(config_file) as json_data:
        config = json.load(json_data)

    parser = JiraTicketDescriptionParser(
        server=config["jira"]["server"],
        project=config["jira"]["project"],
        username=config["jira"]["username"],
        password=config["jira"]["password"],
    )

    ticket_id = args.ticket_id
    parsed_data = parser.parse(ticket_id=ticket_id)
    print("{}: {}\r\n".format(ticket_id, json.dumps(parsed_data, indent=4)))

    generator = CodeGenerator()
    output = generator.generate(data=parsed_data)
    print(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("--ticket-id", required=True, help="ticket id. Example: TOSD-3310")
    parser.set_defaults(func=__tfgen)
    args = parser.parse_args()
    try:
        args.func(args)
    except TypeError:
        parser.print_help()


if __name__ == "__main__":
    main()
