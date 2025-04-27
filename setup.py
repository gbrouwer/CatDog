from setuptools import setup, find_packages

setup(
    name="catdog",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pyaudio",
    ],
    python_requires=">=3.8",
)
