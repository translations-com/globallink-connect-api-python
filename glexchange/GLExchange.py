from suds.client import Client
from suds.wsse import *
from suds.sax.element import Element
import os
import datetime
import time
import base64

from .model import ProjectDirectorConfig
from .model import Project
from .model import Document
from .model import Submission
from .model import Target

class GLExchange:
	"""Main glexchange manager class"""
	
	_connectionConfig = None
	_submission = None
	_documentService = None
	_projectService = None
	_submissionService = None
	_targetService = None
	_userProfileService = None
	_workflowService = None
	
	_modelNamespace = "{http://dto.model.projectdirector.gs4tr.org/xsd}"
	
	def __init__(self, config):
		self.setConnectionConfig(config)
		
	def setConnectionConfig(self, config):
		if config is None: 
			raise Exception("Config is None")
		elif config.url is None or len(config.url)<7:
			raise Exception("PD Url not set")
		elif config.username is None or len(config.username)<=0:
			raise Exception("Username not set")
		elif config.password is None or len(config.password)<=0:
			raise Exception("Password not set")
		elif config.userAgent is None or len(config.userAgent)<=0:
			raise Exception("UserAgent not set")
		
		self._connectionConfig = config
		
		if self._connectionConfig.url[-1]=='/':
			self._connectionConfig.url = self._connectionConfig.url[:-1]
		
		path = os.path.dirname(os.path.abspath(__file__))
		if path[0]=='/':
			path = path[1:]
                
		self._projectService = Client("file:///"+path+"/wsdl/ProjectService_580.wsdl")
		self._projectService.sd[0].service.setlocation(self._connectionConfig.url+"/services/ProjectService_580")
		self._targetService = Client("file:///"+path+"/wsdl/TargetService_580.wsdl")
		self._targetService.sd[0].service.setlocation(self._connectionConfig.url+"/services/TargetService_580")
		self._documentService = Client("file:///"+path+"/wsdl/DocumentService_580.wsdl")
		self._documentService.sd[0].service.setlocation(self._connectionConfig.url+"/services/DocumentService_580")
		self._submissionService = Client("file:///"+path+"/wsdl/SubmissionService_580.wsdl")
		self._submissionService.sd[0].service.setlocation(self._connectionConfig.url+"/services/SubmissionService_580")
		self._userProfileService = Client("file:///"+path+"/wsdl/UserProfileService_580.wsdl")
		self._userProfileService.sd[0].service.setlocation(self._connectionConfig.url+"/services/UserProfile_580")
		self._workflowService = Client("file:///"+path+"/wsdl/WorkflowService_580.wsdl")
		self._workflowService.sd[0].service.setlocation(self._connectionConfig.url+"/services/WorkflowService_580")
		self.__setHeaders()
		
	def __setHeaders(self):
		security = Security()
		token = UsernameToken(self._connectionConfig.username, self._connectionConfig.password)
		security.tokens.append(token)
		uans = ('commons', 'http://commons.ws.projectdirector.gs4tr.org')
		ua = Element('userAgent', ns=uans).setText(self._connectionConfig.userAgent)
		self._projectService.set_options(wsse=security, soapheaders=ua)
		self._targetService.set_options(wsse=security, soapheaders=ua)
		self._submissionService.set_options(wsse=security, soapheaders=ua)
		self._documentService.set_options(wsse=security, soapheaders=ua)
		self._userProfileService.set_options(wsse=security, soapheaders=ua)
		self._workflowService.set_options(wsse=security, soapheaders=ua)
		
	def __createSubmissionInfo(self):
		submissionInfo = self._submissionService.factory.create(self._modelNamespace+"SubmissionInfo")
		submissionInfo.projectTicket = self._submission.project.ticket
		submissionInfo.name = self._submission.name
		if self._submission.pmNotes != None and self._submission.pmNotes != "":
			submissionInfo.internalNotes = self._submission.pmNotes
		
		dateRequested = self._submissionService.factory.create(self._modelNamespace+"Date")
		dateRequested.date = "0"
		if self._submission.dueDate != None and self._submission.dueDate != "" and self._submission.dueDate != 0:
			dateRequested.date = self._submission.dueDate*1000
			
		dateRequested.critical = "false"
		submissionInfo.dateRequested = dateRequested
			
		metadatas = []
		if self._submission.metadata != None and len(self._submission.metadata)>0:
			for key, value in document.metadata.iteritems():
				meta = self._submissionService.factory.create(self._modelNamespace+"Metadata")
				meta.key = key[0:255]
				meta.value = value[0:1024]
				metadatas.append(meta)
		submissionInfo.metadata = metadatas
		
		if self._submission.submitter != None and self._submission.submitter != "":
			submissionInfo.submitters = [self._submission.submitter ]
		
		priority = self._submissionService.factory.create(self._modelNamespace+"Priority")
		priority.value = 1
		if self._submission.isUrgent != None and self._submission.isUrgent == "true":
			priority.value = 2
		submissionInfo.priority = priority
		
		attributes = []
		if self._submission.customAttributes != None and len(self._submission.customAttributes)>0:
			for key, value in self._submission.customAttributes.iteritems():
				customField = self._submissionService.factory.create(self._modelNamespace+"SubmissionCustomFields")
				customField.fieldName = key
				customField.fieldValue = value
				attributes.append(customField)
				
		submissionInfo.submissionCustomFields = attributes
		
		if self._submission.workflow != None and self._submission.workflow.ticket != "":
			submissionInfo.workflowDefinitionTicket = self._submission.workflow.ticket
		
		submissionInfo.claimScope = None
		return submissionInfo
		
	def __getDocumentInfo(self, document):
		documentInfo = self._projectService.factory.create(self._modelNamespace+"DocumentInfo")
		documentInfo.projectTicket = self._submission.project.ticket
		documentInfo.name = document.name
		documentInfo.sourceLocale = document.sourceLanguage
		
		if self._submission.ticket != "":
			documentInfo.submissionTicket = self._submission.ticket
		
		metadatas=[]
		if document.metadata != None and len(document.metadata)>0:
			for key, value in document.metadata.iteritems():
				meta = self._projectService.factory.create(self._modelNamespace+"Metadata")
				meta.key = key[0:255]
				meta.value = value[0:1024]
				metadatas.append(meta)
				
		documentInfo.metadata = metadatas
		
		if document.clientIdentifier != None and document.clientIdentifier != "":
			documentInfo.clientIdentifier = document.clientIdentifier
			
		if document.instructions != None and document.instructions != "":
			documentInfo.instructions = document.instructions
		else:
			documentInfo.instructions = self._submission.instructions
			
		documentInfo.targetInfos = self.__getDocumentTargetInfos (document)
		documentInfo.dateRequested = None
		return documentInfo
		
	def __getDocumentTargetInfos (self, document):
		targetInfos = []
		for language in document.targetLanguages:
			targetInfo = self._documentService.factory.create(self._modelNamespace+"TargetInfo")
			targetInfo.targetLocale = language
			
			targetInfo.requestedDueDate = 0
			if self._submission.dueDate != None and self._submission.dueDate != "":
				targetInfo.requestedDueDate = self._submission.dueDate*1000
				
			
			targetInfo.encoding = document.encoding
			targetInfo.priority = None
			targetInfo.dateRequested = None
			targetInfos.append(targetInfo)
			
		return targetInfos
		
	def __getDocumentResourceInfo(self, document):
		resourceInfo = self._documentService.factory.create(self._modelNamespace+"ResourceInfo")
		resourceInfo.encoding = document.encoding
		resourceInfo.size = len(document.data)
		resourceInfo.classifier = document.fileformat
		resourceInfo.name = document.name
		resourceInfo.mimeType = "text/xml"
		if document.clientIdentifier != None and document.clientIdentifier != "":
			resourceInfo.clientIdentifier = document.clientIdentifier
		resourceInfo.type = None
		
		return resourceInfo
		
	def __validateDocument (self, document):
		if document == None or document.data == None or len(document.data) < 1:
			raise Exception("Document is empty")
		
		if document.name == None:
			raise Exception("Document name not set")
		
		if document.fileformat != "Non-Parsable":
			for fileFormat in self._submission.project.fileFormats:
				if fileFormat == document.fileformat:
					break
			else:
				raise Exception("Specified file format '"+document.fileformat+"' doesn`t exist in specified project")
		
		if document.sourceLanguage == None or len(document.sourceLanguage) < 2:
			raise Exception("Source language not set")
		
		if document.targetLanguages == None or len(document.targetLanguages) < 1:
			raise Exception("Target languages are not set")
		
		for language in document.targetLanguages:
			for languageDirection in self._submission.project.languageDirections:
				if languageDirection.sourceLanguage == document.sourceLanguage and languageDirection.targetLanguage == language:
					break
			else:
				raise Exception("Project is not configured for language direction '"+document.sourceLanguage+" - "+language+"'")
		
	def __validateSubmission (self, submission):
		if submission == None:
			raise Exception("Please initialize submission first.")
		
		if submission.project == None:
			raise Exception("Please set submission project")
		
		if submission.name == None or submission.name == '':
			raise Exception("Please set submission name")
		
		if submission.workflow != None:
			for workflow in submission.project.workflows:
				if workflow.ticket == submission.workflow.ticket:
					break
			else:
				raise Exception("Invalid submission workflow "+submission.workflow.name)
	
		if submission.dueDate != None and submission.dueDate != 0:
			now = datetime.datetime.now()
			ticks = int(time.mktime(now.timetuple()))
			if ticks > submission.dueDate :
				raise Exception("Submission due date should be greater than current date")
		
		if submission.submitter != None and submission.submitter != "":
			if not self.isSubmitterValid(submission.project.shortCode, submission.submitter):
				raise Exception("Specified submitter '"+submission.submitter+"' doesn`t exist")
		
		if submission.project.customAttributes != None and len(submission.project.customAttributes)>0:
			for projectCustomAttribute in submission.project.customAttributes:
				if projectCustomAttribute.mandatory:
					isSet = False
					if submission.customAttributes != None and len(submission.customAttributes)>0:
						for key, value in submission.customAttributes.iteritems():
							if key == projectCustomAttribute.name:
								isSet = True
								break

					if not isSet:
						raise Exception("Mandatory custom field '"+projectCustomAttribute.name+"' is not set")

			if submission.customAttributes != None and len(submission.customAttributes)>0:
				for key, value in submission.customAttributes.iteritems():
					isExists = False
					for projectCustomAttribute in submission.project.customAttributes:
						if key == projectCustomAttribute.name:
							isExists = True
							if projectCustomAttribute.type=="COMBO" and projectCustomAttribute.values != None:
								comboValueCorrect = False
								va = projectCustomAttribute.values.split(',')
								for option in va:
									if option == value:
										comboValueCorrect = True
										break

								if not comboValueCorrect:
									raise Exception("Value '"+value+"' for custom field '"+key+"' is not allowed. Allowed values:"+projectCustomAttribute.values)

					if not isExists:
						raise Exception("Custom field '"+key+"' is not allowed in project")
		else:
			if submission.customAttributes != None and len(submission.customAttributes)>0:
				raise Exception("Project doesn't have custom attributes")
		
	def cancelDocument (self, documentTicket, locale = None):
		if locale != None:
			return self._targetService.service.cancelTarget(documentTicket)
		else:
			return self._targetService.service.cancelTargetByDocumentId(documentTicket, locale)
		
	def cancelSubmission (self, submissionTicket, comment = None):
		if comment is None:
			return self._submissionService.service.cancelSubmission(submissionTicket)
		else:
			return self._submissionService.service.cancelSubmissionWithComment(submissionTicket, comment)
		
	def downloadTarget (self, ticket):
		resourceItem = self._targetService.service.downloadTargetResource(ticket)
		return base64.b64decode(resourceItem.data)
		
	def getCancelledTargets (self, maxResults):
		projects = self.getProjects(True)
		tickets = []
		for project in projects:
			tickets.append(project.ticket)
		
		cancelledTargets = self._targetService.service.getCanceledTargetsByProjects ( tickets, maxResults )
		
		result = []
		for externalTarget in cancelledTargets:
			result.append(Target.PDTarget(externalTarget))
		
		return result

	def getCancelledTargetsByProject (self, project, maxResults):
		cancelledTargets = self._targetService.service.getCanceledTargetsByProjects ( [project.ticket], maxResults )
		
		result = []
		for externalTarget in cancelledTargets:
			result.append(Target.PDTarget(externalTarget))
		
		return result

	def getCancelledTargetsByProjects (self, projects, maxResults):
		tickets = []
		for project in projects:
			tickets.append(project.ticket)
		
		cancelledTargets = self._targetService.service.getCanceledTargetsByProjects ( tickets, maxResults )
		
		result = []
		for externalTarget in cancelledTargets:
			result.append(Target.PDTarget(externalTarget))
		
		return result

	def getCancelledTargetsByProjectTickets (self, projectTickets, maxResults):
		cancelledTargets = self._targetService.service.getCanceledTargetsByProjects ( projectTickets, maxResults )
		result = []
		for externalTarget in cancelledTargets:
			result.append(Target.PDTarget(externalTarget))
		
		return result
		
	def getCancelledTargetsBySubmission(self, submissionTicket, maxResults):
		cancelledTargets = self._targetService.service.getCanceledTargetsBySubmissions ( [submissionTicket], maxResults )
		result = []
		for externalTarget in cancelledTargets:
			result.append(Target.PDTarget(externalTarget))
		return result

	def getCancelledTargetsBySubmissions(self, submissionTickets, maxResults):
		cancelledTargets = self._targetService.service.getCanceledTargetsBySubmissions ( submissionTickets, maxResults )
		result = []
		for externalTarget in cancelledTargets:
			result.append(Target.PDTarget(externalTarget))
		return result

	def getCancelledTargetsByDocument(self, documentTicket, maxResults):
		cancelledTargets = self._targetService.service.getCanceledTargetsByDocuments ( [documentTicket], maxResults )
		result = []
		for externalTarget in cancelledTargets:
			result.append(Target.PDTarget(externalTarget))
		return result

	def getCancelledTargetsByDocuments(self, documentTickets, maxResults):
		cancelledTargets = self._targetService.service.getCanceledTargetsByDocuments ( documentTickets, maxResults )
		result = []
		for externalTarget in cancelledTargets:
			result.append(Target.PDTarget(externalTarget))
		return result
		
	def getCompletedTargets (self, maxResults):
		projects = self.getProjects(True)
		tickets = []
		for project in projects:
			tickets.append(project.ticket)
		
		completedTargets = self._targetService.service.getCompletedTargetsByProjects ( tickets, maxResults )
		
		result = []
		for externalTarget in completedTargets:
			result.append(Target.PDTarget(externalTarget))
		
		return result
		
	def getCompletedTargetsByProject (self, project, maxResults ):
		completedTargets = self._targetService.service.getCompletedTargetsByProjects ( [project.ticket], maxResults )
		result = []
		for externalTarget in completedTargets:
			result.append(Target.PDTarget(externalTarget))
		
		return result

	def getCompletedTargetsByProjects (self, projectTickets, maxResults ):
		completedTargets = self._targetService.service.getCompletedTargetsByProjects ( projectTickets, maxResults )
		result = []
		for externalTarget in completedTargets:
			result.append(Target.PDTarget(externalTarget))
		
		return result

	def getCompletedTargetsByDocuments (self, documentTickets, maxResults ):
		completedTargets = self._targetService.service.getCompletedTargetsByDocuments ( documentTickets, maxResults )
		result = []
		for externalTarget in completedTargets:
			result.append(Target.PDTarget(externalTarget))
		
		return result
		
	def getCompletedTargetsBySubmission(self, submissionTicket, maxResults):
		completedTargets = self._targetService.service.getCompletedTargetsBySubmissions ( [submissionTicket], maxResults )
		
		for externalTarget in completedTargets:
			result.append(Target.PDTarget(externalTarget))
		
		return result

	def getCompletedTargetsBySubmissions(self, submissionTickets, maxResults):
		completedTargets = self._targetService.service.getCompletedTargetsBySubmissions ( submissionTickets, maxResults )
		
		for externalTarget in completedTargets:
			result.append(Target.PDTarget(externalTarget))
		
		return result
		
	def getProject(self, shortCode):
		project = self._projectService.service.findProjectByShortCode(shortCode)
		return Project.PDProject(project)
		
	def getProjects(self, includeSubProjects):
		projects = []
		response = self._projectService.service.getUserProjects(includeSubProjects)
		for project in response:
			projects.append(Project.PDProject(project))
			
		return projects
		
	def getSubmissionName (self, submissionTicket):
		submission = self._submissionService.service.findByTicket ( submissionTicket )
		if submission != None:
			return submission.submissionInfo.name
		else:
			raise Exception("Invalid submission ticket")

	def getSubmissionStatus (self, submissionTicket):
		submission = self._submissionService.service.findByTicket ( submissionTicket )
		if submission != None:
			return submission.status
		else:
			raise Exception("Invalid submission ticket")

	def getSubmissionId (self, submissionTicket):
		submission = self._submissionService.service.findByTicket ( submissionTicket )
		if submission != None:
			return submission.submissionId
		else:
			raise Exception("Invalid submission ticket")
		
	def getSubmissionTicket(self):
		if self.submission != None and self.submission.ticket != None:
			return self.submission.ticket
		else:
			raise Exception("Submission not initialized")
		
	def getUnstartedSubmissions (self, project):
		submissions = []
		creatingSubmissions = self._submissionService.service.findCreatingSubmissionsByProjectShortCode(project.shortCode)
		for creatingSubmission in creatingSubmissions:
			sub = Submission.PDSubmission()
			sub.ticket = creatingSubmission.ticket
			sub.name = creatingSubmission.submissionInfo.name
			submissions.append(sub)
			
		return submissions
		
	def initSubmission(self, submission):
		self.__validateSubmission ( submission )

		self._submission = submission
		self._submission.ticket = ""
		
	def isSubmitterValid(self, shortCode, submitter):
		submitters = self._userProfileService.service.getSubmitters(shortCode)
		for submitter in submitters:
			info = submitter.userInfo
			if info.userName == submitter and info.enabled and not info.accountLocked and info.accountNonExpired:
			    return True
		
		return False
		
	def sendDownloadConfirmation (self, ticket):
		return self._targetService.service.sendDownloadConfirmation ( ticket )
		
	def startSubmission(self):
		if self._submission is None or self._submission.project is None or self._submission.name is None:
			raise Exception("Please initialize submission first.")
		
		if self._submission.ticket is None or self._submission.ticket == "":
			raise Exception("Please upload a translatable document first.")
		
		submissionInfo = self.__createSubmissionInfo()
		
		self._submissionService.service.startSubmission(self._submission.ticket, submissionInfo)
		submissionTicket = self._submission.ticket
		self._submission = None
		
		return submissionTicket
		
	def uploadReference (self, referenceDocument):
		if referenceDocument == None or referenceDocument.data == None:
			raise Exception("Document is empty")
		if referenceDocument.name == None or referenceDocument.name == '':
			raise Exception("Document name not set" )
		
		if self._submission == None or self._submission.ticket == None:
			raise Exception("Submission not initialized.")
		
		if self._submission.ticket == None:
			raise Exception("Invalid submission ticket. Please upload a translatable document before attempting to upload reference documents.")
		
		resourceInfo = self.__getDocumentResourceInfo(referenceDocument)
		return self._submissionService.service.uploadReference ( self._submission.ticket, resourceInfo, referenceDocument.data )
		
	def uploadTranslatable(self, document):
		if self._submission is None or self._submission.ticket is None:
			raise Exception("Submission not initialized.")
		
		self.__validateDocument ( document )
		
		documentInfo = self.__getDocumentInfo ( document )
		resourceInfo = self.__getDocumentResourceInfo(document)
		data = base64.b64encode(document.data.encode("utf-8")).decode("utf-8")

		documentTicket = self._documentService.service.submitDocumentWithBinaryResource(documentInfo, resourceInfo, data)
		if documentTicket != None:
			self._submission.ticket = documentTicket.submissionTicket
			
		return documentTicket.ticketId
