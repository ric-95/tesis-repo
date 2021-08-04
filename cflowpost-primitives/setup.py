from setuptools import setup, find_namespace_packages

setup(
    name="cflowpost-primitives",
    description="Primitive code to be reused throughout "
                "the `cflowpost` environment.",
    author="Ricardo Franco Estrada",
    author_email="ricardo.franco@pucp.edu.pe",
    packages=find_namespace_packages(include=["cflowpost.*"],
                                     where="src"),
    package_dir={"": "src"}
)