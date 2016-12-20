
from . import LanguageDirection
from . import Workflow
from . import CustomAttribute

class PDProject:
	shortCode = ''
	name = ''
	ticket = ''
	languageDirections = []
	fileFormats = []
	workflows = []
	customAttributes = []

	def __init__(self, externalProject):
		self.name = externalProject.projectInfo.name;
		self.shortCode = externalProject.projectInfo.shortCode;
		self.ticket = externalProject.ticket
		
		for externalLanguageDirection in externalProject.projectLanguageDirections:
			self.languageDirections.append(LanguageDirection.PDLanguageDirection(externalLanguageDirection))
			
		for fileFormatProfile in externalProject.fileFormatProfiles:
			self.fileFormats.append(fileFormatProfile.profileName)
			
		if hasattr(externalProject, 'workflowDefinitions') :
			for externalWorkflowDefinition in externalProject.workflowDefinitions:
				self.workflows.append(Workflow.PDWorkflow(externalWorkflowDefinition))
				
			
		if hasattr(externalProject, 'projectCustomFieldConfiguration'):
			for externalCustomField in externalProject.projectCustomFieldConfiguration:
				self.customAttributes.append(CustomAttribute.PDCustomAttribute(externalCustomField))
				
		

