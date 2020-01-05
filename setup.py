import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyslurpers",
    version="0.1.2",
    author="Sergey Yanzin",
    author_email="yanzinsg@gmail.com",
    description="Python slurpers package for simple XML, JSON, config, etc. processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xuthus/pyslurpers",
    packages=['pyslurpers'],
    package_dir={'pyslurpers': 'src'},
    license="MIT License",
    keywords="pyslurpers xml json config cfg ini parse processing",
    platforms=["any"],
    install_requires=[
        "configparser"
    ],
    package_data={
        'pyslurpers':
            [
                'testdata/google.config',
                'testdata/baez.json',
                'testdata/balalaika.json',
                'testdata/attributes.xml',
                'testdata/balalaika.xml',
                'testdata/beatles.xml',
                'testdata/cdata.xml',
                'testdata/logback.xml',
                'testdata/singletag.xml',
                'testdata/tags-illegals.xml',
                'testdata/test.xml',
                'testdata/test1.xml',
                'testdata/test2.xml'
            ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
)
