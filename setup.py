import io
import setuptools

with io.open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="energyprotector-socket", # Replace with your own username
    version="0.1",
    author="yunseo-h68",
    author_email="yunseo.h68@gmail.com",
    description="A package for socket communication in energyprotector project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dsm-change-maker/energyprotector-socket",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.6',
)
