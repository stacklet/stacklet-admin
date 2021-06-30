from setuptools import setup

setup(
    name="stacklet.cli",
    version="0.0.1",
    install_requires=["Click"],
    entry_points={
        "console_scripts": ["stacklet-admin = stacklet.platform_cli.cli:cli"]
    },
)
