import json
import os

from parser import JiraTicketDescriptionParser

if __name__ == "__main__":
    config_file = os.getenv("HOME") + "/.opscli/config.json"
    with open(config_file) as json_data:
        config = json.load(json_data)

    parser = JiraTicketDescriptionParser(
        server=config["jira"]["server"],
        project=config["jira"]["project"],
        username=config["jira"]["username"],
        password=config["jira"]["password"],
    )

    ticket_id = "TOSD-3310"
    output = parser.parse(ticket_id=ticket_id)
    print("{}: {}".format(ticket_id, json.dumps(output, indent=4)))

    ticket_id = "TOSD-3309"
    output = parser.parse(ticket_id=ticket_id)
    print("{}: {}".format(ticket_id, json.dumps(output, indent=4)))
