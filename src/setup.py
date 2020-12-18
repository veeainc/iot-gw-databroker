from setuptools import setup

setup(
    name='myapp',
    version='',
    packages=['myapp'],
    description='',
    install_requires=[
        'vbus @ git+https://bitbucket.org/vbus/vbus.py'
    ],
    entry_points={
        'console_scripts': ['myapp=myapp.main:main'],
    }
)

