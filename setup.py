from setuptools import setup

test_deps = [
    'pytest',
    'pytest-cov',
    'coveralls',
    'validate_version_code',
    'codacy-coverage',
    'parameterized'
]

extras = {
    'test': test_deps,
}

setup(
    name='oaksim',
    version='0.1',
    packages=[''],
    url='https://github.com/Knowledge-Graph-Hub/oaksim',
    license='BSD3',
    author='Justin Reese',
    author_email='Justin Reese',
    description='',

    # add package dependencies
    install_requires=[
                       'oaklib',
                       ],
    extras_require=extras,
)
