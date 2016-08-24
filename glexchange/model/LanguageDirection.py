class PDLanguageDirection:
	sourceLanguage = ''
	targetLanguage = ''
	def __init__(self, externalLanguageDirection) :
		self.sourceLanguage = externalLanguageDirection.sourceLanguage.locale
		self.targetLanguage = externalLanguageDirection.targetLanguage.locale
		