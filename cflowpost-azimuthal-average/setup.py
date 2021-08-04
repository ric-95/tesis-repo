from setuptools import setup, find_namespace_packages

setup(
    name="cflowpost-azimuthal-average",
    description="Simple package for averaging and "
                "processing axisymmetric flow data.",
    author="Ricardo Franco Estrada",
    author_email="ricardo.franco@pucp.edu.pe",
    packages=find_namespace_packages(include=["cflowpost.*"],
                                     where="src"),
    package_dir={"": "src"}
)
