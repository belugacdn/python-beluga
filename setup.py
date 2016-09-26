try:
    from setuptools import setup, find_packages
except ImportError:
    print "You need to install setuptools to continue"
setup(
    name='beluga',
    version='1.0.0',
    author='Adam Jacob Muller',
    packages=find_packages(),
    author_email='adam@belugacdn.com',
    entry_points={
        "console_scripts": [
            "beluga = beluga.cli:main",
        ]
    },
    install_requires=[
        'requests'
    ]
)
