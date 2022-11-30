import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="red-py-sdk",
    version="0.1.8",
    author="Reddio",
    author_email="contact@reddio.com",
    description="https://github.com/reddio-com/red-py-sdk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/reddio-com/red-py-sdk",
    keywords='reddio sdk',
    classifiers=[
        "Programming Language :: Python :: 3",
        'Topic :: Education',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Utilities',
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    packages=['redpysdk'],
    package_data={'redpysdk': ['*.json']},
    install_requires=[
        "mpmath",
        "ecdsa",
        "sympy",
        "web3"
    ],
)
