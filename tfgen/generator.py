#!/usr/bin/env python3

import os

from jinja2 import FileSystemLoader, Environment
from tfgen.client import AWSClient


class CodeGenerator(object):
    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        loader = FileSystemLoader("{}/templates/".format(dir_path))
        self.environment = Environment(loader=loader)
        self.client = AWSClient()

    def __render(self, template, context):
        return self.environment.get_template(template).render(context)

    def generate(self, data):
        output = ""
        product_domain = []
        service_name = []
        need_vpc = False
        create_ec2 = False
        for d in filter(lambda x: "UNKNOWN" not in x, data):
            key = list(d)[0]
            context = d[key]
            output = output + self.__render(template="{}.jinja2".format(key.lower()), context=context)

            if key == "EC2":
                need_vpc = True
                create_ec2 = True
            elif key in ["ALB", "TG", "LISTENER", "RDS"]:
                need_vpc = True

            if "tags" in context:
                product_domain.append(context["tags"]["ProductDomain"])
                service_name.append(context["tags"]["Service"])

        product_domain = list(set(product_domain))
        service_name = list(set(service_name))

        if len(product_domain) == 1:
            product_domain = product_domain[0]
        else:
            raise ValueError("More than one ProductDomain detected in resources' tags!")

        if len(service_name) == 1:
            service_name = service_name[0]
        else:
            raise ValueError("More than one Service name detected in resources' tags!")

        main_context = {
            "product_domain": product_domain,
            "service_name": service_name,
            "need_vpc": need_vpc,
            "create_ec2": create_ec2
        }
        return self.__render(template="main.jinja2", context=main_context) + output
