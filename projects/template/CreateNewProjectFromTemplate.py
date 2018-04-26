#!/usr/bin/env python

#Note that this script must be located in the same directory as the template for new projects!

import sys, os, shutil, re
from itertools import count

_script_dir = os.path.dirname(os.path.realpath(__file__))
_rel_project_dir = '..' #Directory to put new projects relative to this script.

def createProjectFromTemplate(newProjectPath, dontMakeLibraries):
	
	projectExt = '.PrjPcb' #File extension of the project file
	libFileExts = ('.SchLib', '.PcbLib')
	projectFileExts = libFileExts + ('.PcbDoc', '.SchDoc', '.OutJob') #File types to consder as part of the template in addition to projectExt
	
	newProjectPath = os.path.normpath(newProjectPath)
	newProjectPathParts = newProjectPath.split(os.sep)
	newProjectName = newProjectPathParts[-1]
	
	newProjectRealDir = os.path.realpath(os.path.join(_script_dir, _rel_project_dir, newProjectPath))
	
	templateProjectFileName = None
	templateFileNames = []
	for fileName in os.listdir(_script_dir):
		fileBase, fileExt = os.path.splitext(fileName)
		if fileExt == projectExt:
			if templateProjectFileName:
				print('More than one project file in template directory!')
				return
			templateProjectFileName = fileName
		elif fileExt in projectFileExts:
			templateFileNames.append((fileName, fileBase, fileExt))

	if not templateProjectFileName:
		print('No project file found in template directory!')

	templateProjectPath = os.path.join(_script_dir, templateProjectFileName)
	templateProjectFile = open(templateProjectPath, 'r')
	projectFileStr = templateProjectFile.read()
	templateProjectFile.close()
	
	if os.path.exists(newProjectRealDir):
		if len(next(os.walk(newProjectRealDir))[2]):
			print('Sorry, the directory for the project you want to make already has files in it!')
			return
	else:
		os.makedirs(newProjectRealDir)
	
	for fileName, fileBase, fileExt in templateFileNames:
		if dontMakeLibraries and (fileExt in libFileExts):
			print(fileName)
			projectFileStr = re.sub(r'\[Document[0-9]+\]\sDocumentPath='+re.escape(fileName)+r'[^\[]+', '', projectFileStr, 1, re.S)
		else:
			filePath = os.path.join(_script_dir, fileName)
			newFileName = newProjectName + fileExt
			newFilePath = os.path.join(newProjectRealDir, newFileName)
			
			projectFileStr = projectFileStr.replace(fileName, newFileName)
			
			shutil.copyfile(filePath, newFilePath)
		
	projectFileStr = projectFileStr.replace('DocumentPath=..\\', 'DocumentPath=' + ('..\\' * len(newProjectPathParts)))
	print(newProjectPathParts)
	if dontMakeLibraries or len(newProjectPathParts) >= 2: #don't make libraries for nested projects
		_docCounter = count(1);
		projectFileStr = re.sub(r'^(\[Document)([0-9]+)(\])$', lambda mo: mo.group(1) + str(next(_docCounter)) + mo.group(3), projectFileStr, 0, re.M)
	
	newProjectFilePath = os.path.join(newProjectRealDir, newProjectName + projectExt)
	newProjectFile = open(newProjectFilePath, 'w+')
	newProjectFile.write(projectFileStr)
	newProjectFile.close()

	print('Done!')
	return
	
if len(sys.argv) > 1 and sys.argv[1]: #command line argument given
	createProjectFromTemplate(str(sys.argv[1]), False)
else:
	createProjectFromTemplate( \
	str(raw_input('Enter the name of the new project you would like to create: ')), \
	str(raw_input('Would you like to generate a library for this project? (Y/n): ')).lower().startswith('n') \
	)