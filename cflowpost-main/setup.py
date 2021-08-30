from setuptools import setup, find_packages

setup(name="cflowpost",
      author="Ricardo Franco Estrada",
      author_email="ricardo.franco@pucp.edu.pe",
      packages=find_packages(where="src", include=["cflowpost.*"]),
      package_dir={"": "src"})
