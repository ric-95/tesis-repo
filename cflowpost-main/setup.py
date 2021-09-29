from setuptools import setup, find_packages

requirements = ["numpy", "pandas", "matplotlib",
                "scipy", "seaborn", "toolz", "dask"]

setup(name="cflowpost",
      author="Ricardo Franco Estrada",
      author_email="ricardo.franco@pucp.edu.pe",
      version="0.1.0",
      packages=find_packages(where="src", include=["cflowpost.*"]),
      package_dir={"": "src"},
      install_requires=requirements,
      package_data={"cflowpost.pvx": ["README.md"]})
