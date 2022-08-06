from setuptools import setup

setup(
    name="src",
    version="0.1",
    packages=["src"],
    install_requires=[
        "pandas==1.1.2", 
        "numpy==1.19.1", 
        "streamlit==1.11.1", 
        "plotly==4.13.0"],
    zip_safe=False,
)
