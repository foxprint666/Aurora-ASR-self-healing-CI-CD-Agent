from setuptools import setup, find_packages

setup(
    name="aurora-asr",
    version="1.0.0",
    description="Aurora ASR: OpenEnv-v4 Compliant Self-Healing CI/CD Agent",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Aurora Contributor",
    url="https://github.com/foxprint666/Aurora-ASR-self-healing-CI-CD-Agent",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "gym>=0.21.0",
        "gymnasium>=0.27.0",
        "docker>=5.0.0",
        "tree-sitter>=0.20.0",
        "pytest>=7.0.0",
        "numpy>=1.21.0",
        "openai>=1.0.0",
        "pydantic>=2.0.0",
        "openenv-core>=0.1.0",
        "rich>=13.0.0",
    ],
    entry_points={
        'console_scripts': [
            'aurora-inference=inference:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)