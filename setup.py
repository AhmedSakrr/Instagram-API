from setuptools import setup

with open('README.md', 'r') as f:
    README = f.read()

setup(
    name="ig-web-api",
    version="1.0.0",
    author="TheDevFromKer",
    license="MIT",
    description="Simple Instagram API.",
    url="https://github.com/TheDevFromKer/Instagram-API",
    packages=[str('ig-web-api')],
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    install_requires=["requests", "fake_headers", "Pillow"]
)
