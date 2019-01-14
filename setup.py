from setuptools import setup, find_packages

with open("svgoutline/version.py", "r") as f:
    exec(f.read())

setup(
    name="svgoutline",
    version=__version__,
    packages=find_packages(),

    # Metadata for PyPi
    url="https://github.com/mossblaser/svgoutline",
    author="Jonathan Heathcote",
    description="Convert SVG files (including text) into simple lines and curves for plotters.",
    license="LGPLv3",
    classifiers=[
        "Development Status :: 3 - Alpha",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",

        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",

        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
    ],
    keywords="svg outline plotter cutter",

    # Requirements
    install_requires=["PySide2>=5.11.0"],
)
