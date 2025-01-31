import pathlib
import setuptools

setuptools.setup(
    name="ps_beet_bolt",
    version="0.2.2",
    description="A collection of beet and bolt plugins",
    long_description=pathlib.Path("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://pucki.zip",
    author="PuckiSilver",
    license="MIT",
    project_urls={
        "Source": "https://github.com/PuckiSilver/ps_beet_bolt",
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=["beet","mecha","bolt"],
    packages=setuptools.find_namespace_packages(),
    include_package_data=True,
)
