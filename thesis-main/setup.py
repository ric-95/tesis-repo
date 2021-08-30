from setuptools import setup, find_packages

setup(
    name="thesis",
    author="Ricardo Franco Estrada",
    author_email="ricardo.franco@pucp.edu.pe",
    packages=find_packages(where="src", include=["thesis",
                                                 "thesis.*"]),
    package_dir={"": "src"}
)
