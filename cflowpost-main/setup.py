from setuptools import setup, find_packages

requirements = ["numpy", "pandas", "matplotlib",
                "scipy", "seaborn", "toolz"]

setup(name="cflowpost",
      author="Ricardo Franco Estrada",
      author_email="ricardo.franco@pucp.edu.pe",
      packages=find_packages(where="src", include=["cflowpost.*"]),
      package_dir={"": "src"},
      install_requires=requirements)
