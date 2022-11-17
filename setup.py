from distutils.core import setup

setup(
    name='SmithWagnerCV',
    version='0.0.3',
    packages=['SmithWagnerCV',],
    license='MIT',
    install_requires=[
        'numpy',
        'pandas',
        'tqdm'
    ],
    author='Ben Smith',
    author_email='bosmith@unomaha.edu',
    classifiers=[
    'Development Status :: 3 - Alpha', 
    'Intended Audience :: Science/Research', 
    'License :: OSI Approved :: MIT License',  
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    ],
    keywords = ['Monte Carlo', 'Value-added Learning', 'Statistics'],
    url = 'https://github.com/tazzben/SmithWagnerCV',
    download_url = 'https://github.com/tazzben/SmithWagnerCV/archive/v0.0.3.tar.gz',  
    description = 'Produces critical values for value-added learning scores proposed in Smith and Wagner (2018) through Monte Carlo simulations.'
)
