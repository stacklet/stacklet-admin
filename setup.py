from setuptools import setup

setup(
    name="stacklet",
    version="0.0.1",
    install_requires=["Click"],
    entry_points={"console_scripts": ["stacklet = cli.cli:cli"]},
)
