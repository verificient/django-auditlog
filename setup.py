import os

from setuptools import setup

# Readme as long description
with open(os.path.join(os.path.dirname(__file__), "README.md"), "r") as readme_file:
    long_description = readme_file.read()

setup(
    name="django-auditlog",
    use_scm_version={"version_scheme": "post-release"},
    setup_requires=["setuptools_scm"],
    packages=[
        "auditlog",
        "auditlog.migrations",
        "auditlog.management",
        "auditlog.management.commands",
    ],
    url="https://github.com/jazzband/django-auditlog",
    license="MIT",
    author="Jan-Jelle Kester",
    description="Audit log app for Django",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.10",
    install_requires=["Django>=4.2", "python-dateutil>=2.6.0"],
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.2",
        "License :: OSI Approved :: MIT License",
    ],
)
