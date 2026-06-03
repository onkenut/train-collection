from setuptools import setup, find_packages

setup(
    name="dungeonscript",
    version="1.0.0",
    description="A terminal roguelike text adventure game engine",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["../game_data/*.yaml"],
    },
    install_requires=[
        "rich>=13.0.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "dungeonscript=dungeonscript.__main__:main",
        ],
    },
    python_requires=">=3.10",
)
