
from . import WordCount
class PDTarget:
	clientIdentifier = None
	documentName = None
	documentTicket = None
	sourceLocale = None
	targetLocale = None
	metadata = None
	ticket = None
	wordCount = None
	def __init__(self, externalTarget):
		self.documentName = externalTarget.document.documentInfo.name
		self.sourceLocale = externalTarget.sourceLanguage.locale
		self.targetLocale = externalTarget.targetLanguage.locale
		self.ticket = externalTarget.ticket
		self.documentTicket = externalTarget.document.ticket
		self.clientIdentifier = externalTarget.document.documentInfo.clientIdentifier
		
		if hasattr(externalTarget, 'tmStatistics'):
			self.wordCount = WordCount.PDWordCount(externalTarget.tmStatistics.goldWordCount, externalTarget.tmStatistics.oneHundredMatchWordCount, externalTarget.tmStatistics.repetitionWordCount, externalTarget.tmStatistics.noMatchWordCount, externalTarget.tmStatistics.totalWordCount )
		
		self.metadata = {}
		if hasattr(externalTarget.targetInfo, 'metadata'):
			for externalMetadata in externalTarget.targetInfo.metadata:
				self.metadata[externalMetadata.key] = externalMetadata.value
				