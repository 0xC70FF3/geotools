from setuptools import setup, find_packages


def requires():
    with open('requirements.txt') as f:
        return [item.strip() for item in f.readlines()]


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='pygeotools',
    version='0.0.9',
    description='Geolocation Tools for Python3',
    long_description=readme(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Geolocation'
    ],
    keywords='geohash',
    url='http://github.com/0xC70FF3/pygeotools',
    author='Christophe Cassagnabère',
    author_email='christophe@hotmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=requires(),
    test_suite='nose.collector',
    tests_require=['nose', 'coverage', 'nose-cover3'],
    entry_points={
        'console_scripts': ['pygeotools=pygeotools.__main__:main'],
    },
    include_package_data=True,
    zip_safe=True
)
