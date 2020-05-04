from distutils.core import setup
setup(
	name = 'glexchange',
	packages = ['glexchange', 'glexchange.model'],
	data_files=[('wsdl', ['glexchange/wsdl/DocumentService_580.wsdl','glexchange/wsdl/ProjectService_580.wsdl', 'glexchange/wsdl/SubmissionService_580.wsdl',
		'glexchange/wsdl/TargetService_580.wsdl', 'glexchange/wsdl/UserProfileService_580.wsdl', 'glexchange/wsdl/WorkflowService_580.wsdl',
		'glexchange/wsdl/types.xsd', 'glexchange/wsdl/xmime.xsd'])],
	version = '5.8.0',
	description = 'GlobalLink Connect Python is a SDK to connect your system to GlobalLink Project Director&apos;s API.',
	author = 'Translations.com',
	author_email = 'info@translations.com',
	url = 'https://github.com/translations-com/globallink-connect-api-python',
	keywords = ['glexchange', 'glx', 'globallink', 'translations.com','transperfect','localization','translation','project director','PD'],
	install_requires=[
		'suds','datetime','soap',
	],
	classifiers = [
	'Development Status :: 5 - Production/Stable',
	'Intended Audience :: Developers',
	'License :: OSI Approved :: Apache Software License',
	'Programming Language :: Python :: 3',
	'Programming Language :: Python :: 3.6',],
)