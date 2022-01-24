import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
VERSION = open(os.path.join(here, 'VERSION')).read()
README = open(os.path.join(here, 'README.md')).read()

setup(
    name='django-helper',
    version=VERSION,
    package_dir={'helper': 'helper'},
    include_package_data=True,
    packages=find_packages(),
    description='Django Helper module for standardizing microservices',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/growsimplee/django-helper',
    install_requires=[
        "boto3>=1.16.35",
        "Django>=3.1",
        "djangorestframework>=3.12"
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Framework :: Django'
    ]
)
