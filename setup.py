import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nexusraven",
    version="0.1.6",
    author="Nexusflow AI",
    author_email="info@nexusflow.ai",
    description="This package is for using NexusRaven-V2, an open source function calling model, for function calling using OpenAI semantics.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nexusflowai/NexusRavenPython",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10',
    install_requires=[
       "openai",
       "requests"
    ],
)

