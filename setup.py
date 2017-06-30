from distutils.core import setup
setup(
	name = 'glexchange',
	packages = ['glexchange'],
	version = '4.18.1',
	description = 'GlobalLink Connect Python is a SDK to connect your system to GlobalLink Project Director&apos;s API.',
	author = 'Translations.com',
	author_email = 'info@translations.com',
	url = 'https://github.com/translations-com/globallink-connect-api-python',
	download_url = 'https://github.com/translations-com/globallink-connect-api-python/archive/4.18.1.zip',
	keywords = ['glexchange', 'glx', 'globallink', 'translations.com','transperfect','localization','translation','project director','PD'],
	install_requires=[
		'suds','datetime','soap',
	],
	classifiers = [
	'Development Status :: 5 - Production/Stable',
	'Intended Audience :: Developers',
	'License :: OSI Approved :: Apache Software License',
	'Programming Language :: Python :: 2',
	'Programming Language :: Python :: 2.6',
	'Programming Language :: Python :: 2.7',],
)