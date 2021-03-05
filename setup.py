from setuptools import setup


setup(
    name='txq',
    zip_safe=True,
    version='0.2.0',
    description='Modular asynchronous application service',
    url='https://github.com/agratoth/txq',
    maintainer='Anton Berdnikov',
    maintainer_email='agratoth@yandex.ru',
    packages=[
        'txq',
        'txq.apps',
        'txq.apps.users_app',
        'txq.apps.users_app.messages',
        'txq.apps.users_app.models',
        'txq.config',
        'txq.pipes'
    ],
    package_dir={'txq': 'txq'},
    install_requires=[
        'uvloop>=0.15.2',
        'aiohttp>=3.7.4',
        'nkeys>=0.1.0',
        'asyncio-nats-client>=0.11.4',
        'pynsodm>=0.3.3',
        'PyYAML>=5.4.1',
        'txq-messages>=0.1.0',
        'aiojobs>=0.3.0'
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires='>=3.8',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
