from jira import JIRA


class JiraTicketDescriptionParser(object):
    def __init__(self, server, project, username, password):
        self.server = server
        self.project = project
        self.username = username
        self.password = password
        self.client = self.__authenticate()

    def __authenticate(self):
        client = JIRA(
            server=self.server,
            basic_auth=(
                self.username,
                self.password
            )
        )
        client.project(self.project)
        return client

    @staticmethod
    def __get_text_between_words(full_text, first_word, second_word, offset=0):
        try:
            start_index = full_text.index(first_word, offset) + len(first_word)
            end_index = full_text.index(second_word, start_index)
            return full_text[start_index:end_index], end_index + 1
        except ValueError:
            return "", 0

    @staticmethod
    def __reformat(list_of_key_values):
        key_values = {}
        for kvs in list_of_key_values:
            if len(kvs) != 2:
                continue
            else:
                key = kvs[0].strip().replace("\"", "").replace("'", "")
                value = kvs[1].strip().replace("\"", "").replace("'", "")
                key_values[key] = value
        return key_values

    def __parse(self, raw_data):
        text_per_line = raw_data.replace("\r", "").split("\n")
        cleansed_data = list(map(lambda x: x.split("="), filter(None, text_per_line)))

        open_bracket_indexes = []
        for i in range(len(cleansed_data)):
            if len(cleansed_data[i]) == 2 and "{" in cleansed_data[i][1]:
                open_bracket_indexes.append(i)
            elif len(cleansed_data[i]) == 1 and "{" in cleansed_data[i][0]:
                open_bracket_indexes.append(i)

        close_bracket_indexes = []
        for i in range(len(cleansed_data)):
            if len(cleansed_data[i]) == 1 and "}" in cleansed_data[i][0]:
                close_bracket_indexes.append(i)

        if len(open_bracket_indexes) != len(close_bracket_indexes):
            raise IndexError("Don't have symmetric brackets!")

        key_values = {}
        offset = 0
        for i in range(len(open_bracket_indexes)):
            nested_data = cleansed_data[open_bracket_indexes[i] - offset:close_bracket_indexes[i] - offset]
            del cleansed_data[open_bracket_indexes[i] - offset:close_bracket_indexes[i] + 1 - offset]
            offset = offset + close_bracket_indexes[i] - open_bracket_indexes[i] + 1

            key = nested_data[0][0].replace("{", "").strip()
            value = self.__reformat(list_of_key_values=nested_data[1:])
            key_values[key] = value

        key_values.update(self.__reformat(list_of_key_values=cleansed_data))
        return key_values

    @staticmethod
    def __get_resource_type(parameters):
        k = parameters.keys()
        if all(x in k for x in ["count", "instance_type", "ebs_optimized", "disable_api_termination"]):
            return "EC2"
        elif all(x in k for x in ["name", "security_groups", "internal", "idle_timeout", "enable_deletion_protection"]):
            return "ALB"
        elif all(x in k for x in ["name", "port", "protocol", "deregistration_delay"]):
            return "TG"
        elif all(x in k for x in ["port", "protocol"]):
            return "LISTENER"
        elif all(x in k for x in ["identifier", "allocated_storage", "engine_version", "instance_class"]):
            return "RDS"
        else:
            return "UNKNOWN"

    def parse(self, ticket_id):
        description = self.client.issue(id=ticket_id).fields.description

        offset = 0
        output = []
        while True:
            extracted_text, new_offset = self.__get_text_between_words(
                full_text=description,
                first_word="{code}",
                second_word="{code}",
                offset=offset
            )
            if extracted_text == "":
                break
            else:
                parsed = self.__parse(raw_data=extracted_text)
                output.append(parsed)
                offset = new_offset
        return [{self.__get_resource_type(x): x} for x in filter(None, output)]
