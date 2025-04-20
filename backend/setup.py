from setuptools import setup, find_packages

setup(
    name='cheapest-price-finder',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn',
        'scrapy',
        'celery',
        'sqlalchemy',
        'pydantic',
        'redis',
        'requests',
        'numpy',
        'pandas',
        'scikit-learn',
    ],
    test_suite='tests',
)
