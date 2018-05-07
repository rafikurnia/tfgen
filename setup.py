#!/usr/bin/env python3

from setuptools import setup, find_packages

from tfgen import VERSION

setup(
    name="tfgen",
    version=VERSION,
    packages=find_packages(),
    url="https://github.com/rafikurnia/tf-gen",
    license="Apache License 2.0",
    author="Rafi Kurnia Putra",
    author_email="rafi.putra@traveloka.com",
    description="Tools to generate Terraform code for several AWS Resources",
    install_requires=[
        "jira==1.0.15",
        "Jinja2==2.10",
        "boto3==1.7.14",
    ],
    package_data={
        "tfgen": ["templates/*.jinja2"],
    },
    include_package_data=True,
    python_requires=">=3.5",
    entry_points={
        "console_scripts": [
            "tfgen=tfgen.main:main"
        ],
    }
)
