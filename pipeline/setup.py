from setuptools import find_packages, setup

setup(
    name="etl",
    packages=find_packages(exclude=["etl_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud",
        "dagster-celery",
        "julia",
        "numpy",
        "scipy",
        "cbor2",
        "waveform_analysis",
        "paho-mqtt",
    ],
    extras_require={"dev": ["dagit", "pytest"]},
    include_package_data=True,
)
