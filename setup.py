from setuptools import setup, find_packages
from sys import path
from os import environ

path.insert(0, '.')

NAME = "eco_aprs_weather"

if __name__ == "__main__":

    setup(
        name=NAME,
        version=environ.get('APP_VERSION', '0.0.1'),
        author="N5IPT Jonathan Kelley",
        author_email="jonk@omg.lol",
        url="https://github.com/jondkelley/eco_aprs_weather",
        license='BSD',
        packages=find_packages(),
        include_package_data=True,
        package_dir={NAME: NAME},
        description="eco_aprs_weather - Python based HTTP bridge to DireWolf to beacon WX packets",
        install_requires=['redis==3.3.11', 'multidict==4.7.6', 'chardet==3.0.4', 'diskcache', 'Eve', 'cachetools', 'okta', 'Authlib', 'requests'],
        entry_points={
            'console_scripts': ['eco_aprs_weather = eco_aprs_weather.main:main'],
        },
        #zip_safe = False,
    )
