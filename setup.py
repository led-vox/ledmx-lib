from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ledmx",
    version="0.2a",
    license='MIT',
    author="Sergei Michenko",
    author_email="mserg@tih.ru",
    description="ArtDMX Multiverse lib",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mserg/ledmx-lib",
    install_requires=[
        'pytest',
        'PyYAML',
        'numpy',
        'mock',
        'schema'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.10",
)
