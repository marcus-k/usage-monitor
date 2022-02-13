from setuptools import setup

namespace = {}
with open("monitor/version.py", "r") as f:
    exec(f.read(), namespace)

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='monitor',
    version=namespace["__version__"],    
    description='Python CPU, GPU and Runtime Monitors.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/marcus-k/usage-monitor',
    author='Marcus Kasdorf',
    author_email='marcus@kasdorf.net',
    license='MIT License',
    packages=['monitor'],
    python_requires='>=3.7'
)