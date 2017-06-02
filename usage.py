send = False
retrieve=True
if __name__ == "__main__":
	from glexchange.GLExchange import GLExchange
	import glexchange.model.ProjectDirectorConfig
	import glexchange.model.Submission
	import glexchange.model.Document
	import datetime
	import time
	import os
	
	import config
	pdconfig = glexchange.model.ProjectDirectorConfig.ProjectDirectorConfig()
	pdconfig.url=config.url
	pdconfig.username = config.username
	pdconfig.password = config.password
	pdconfig.userAgent = config.userAgent
	glx = GLExchange(pdconfig)
	
	if send:
		project = glx.getProject(config.project)
		print "Using project "+project.name
		submission = glexchange.model.Submission.PDSubmission()
		submission.name = config.submissionPrefix + str(datetime.datetime.now())[:-7]
		submission.project = project
		dueDate = datetime.datetime(2018,1,1,12,0,0)
		submission.dueDate = int(time.mktime(dueDate.timetuple()))
		glx.initSubmission(submission)
		print "Submission initialized"
		
		for file in os.listdir("resources/"+config.sourceLanguage):
			document = glexchange.model.Document.PDDocument()
			document.fileformat = config.fileFormatProfile
			document.sourceLanguage = config.sourceLanguage
			document.name = file
			document.targetLanguages = config.targetLanguages
			with open("resources/"+document.sourceLanguage+"/"+file, 'r') as f:
				document.data = f.read()
		
			ticket = glx.uploadTranslatable ( document )
			print "Document '"+document.name+"' submitted with ticket '"+ticket+"'"
		submissionTicket = glx.startSubmission()
		print "Submission '"+submission.name+"' started. Ticket:"+submissionTicket
		
	if retrieve:
		import os
		print "Starting retrieve"
		project = glx.getProject(config.project)
		targets = glx.getCompletedTargetsByProject (project, 100)
		if len(targets)>0:
			for target in targets:
				data = glx.downloadTarget(target.ticket)
				directory = 'resources/retrieved/'+target.targetLocale+"/"
				if not os.path.exists(directory):
					os.makedirs(directory)
				with open(directory+target.documentName, 'w+') as f:
					f.write(data)
				try:
					print target.documentName  + " [" + target.ticket + "] downloaded to "+directory+target.documentName
				except UnicodeEncodeError:
					print "[Unprintable filename] [" + target.ticket + "] downloaded to "+directory
				glx.sendDownloadConfirmation(target.ticket)
		else:
			print "No completed targets"
		print "Retrieving finished"
		
