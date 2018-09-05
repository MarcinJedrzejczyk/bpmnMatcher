from setuptools import setup, find_packages

setup(
    name='bpmnMatcher',
    version='1.0',
    packages=[''],
    install_requires=[
	'wiktionaryparser==0.0.5',
'bpmn_python==0.0.18',
'networkx==1.11',
'nltk==3.2.5',
'numpy==1.13.3',
'pip==9.0.1',
'JCC==3.0'
],
    url='https://github.com/MarcinJedrzejczyk/bpmnMatcher',
    license='',
    author='Marcin Jędrzejczyk',
    author_email='marcinjaj@gmail.com',
    description=''
)
