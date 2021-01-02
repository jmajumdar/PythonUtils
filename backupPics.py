import os
import glob
import sys
import getopt

# The function processes the command line arguments and determines the year that we want to process
def getYearToProcess(argv) :
	year = ''

	if ( len(argv) < 2 ) :
		print('Incorrect Arguments >> Usage: backupPics.py <year>')
		sys.exit(2)

	year=argv[1]
	print('Year to process is', year)
	return year


# We want to process one month at a time. Get the set of months under the year
def getMonths(basedir, year) :
	months = []
	pathToProcess = basedir + "\\" + year + "\\*"

	for full_file_name in glob.iglob(pathToProcess, recursive=False) :
		if ( os.path.isdir(full_file_name) == True ) :
			idx = full_file_name.rfind('\\')
			month = full_file_name[idx+1:]
			months.append(month)
	print(months)

	return months


# Visit all months of the year
def visitYear(sourcePath, destPath, year) :
	months = getMonths(sourcePath, year)
	for month in months :
		sourceDict = buildFileDict(sourcePath + '\\' + year, month)
		destDict = buildFileDict(destPath + '\\' + year, month)
		printPlan(preparePlan(sourceDict, destDict), False)


# Build the list of files under the directory for the specific month
def buildFileDict(basedir, year) :
	fileDict = {}
	pathToProcess = basedir + "\\" + year + "\\**"
	print("Processing path", pathToProcess)

	basedirLen = len(basedir)
	for full_file_name in glob.iglob(pathToProcess, recursive=True) :
		fileType = FT_FILE
		if ( os.path.isdir(full_file_name) == True ) :
			fileType = FT_DIR

		idx = full_file_name.rfind('\\')
		if ( idx >= 0 ) :
			file_info = {}
			file_info['name'] = file_name = full_file_name[idx+1:]
			file_info['path'] = full_file_name[basedirLen+1:idx]
			file_info['type'] = fileType
			fileDict[file_name] = file_info

	return fileDict


# Print the list of files
def printFileDict(prompt, fileDict) :
	print(prompt, ':')
	for file_info in fileDict.values() :
		str_ft = 'FILE'
		if ( file_info['type'] == FT_DIR ) :
			str_ft = 'DIR'
		print(file_info['path'] + "\\" + file_info['name'] + " (" + str_ft + ")")


# Prepare a plan of what to do with files form the source directory
def preparePlan(sourceDict, destDict) :
	plan = {}
	file_plan = {}
	count_create_dir = count_copy = count_move = count_skip = count_total = 0

	for source_file, source_file_info in sourceDict.items() :
		dest_file_info = destDict.get(source_file)
		if ( dest_file_info == None ) :
			this_plan = file_plan[source_file] = preparePlanForNewFile(source_file_info)
		else :
			this_plan = file_plan[source_file] = preparePlanForExistingFile(source_file_info, dest_file_info)

		if ( this_plan['action'] == ACTION_COPY_FILE ) :
			count_copy = count_copy+1
		elif ( this_plan['action'] == ACTION_MOVE_FILE ) :
			count_move = count_move+1
		elif ( this_plan['action'] == ACTION_CREATE_DIR ) :
			count_create_dir = count_create_dir+1
		else :
			count_skip = count_skip+1
		count_total = count_total+1

	plan['skips'] = count_skip
	plan['copies'] = count_copy
	plan['moves'] = count_move
	plan['creates'] = count_create_dir
	plan['totals'] = count_total
	plan['file_plan'] = file_plan
	return plan


# Prepare the plan for a single file that doesn't already exist on the destination
def preparePlanForNewFile(source_file_info) :
	action = ACTION_COPY_FILE
	if ( source_file_info['type'] == FT_DIR ) :
		action = ACTION_CREATE_DIR
	destination = source_file_info['path']
	plan = {}
	plan['path'] = source_file_info['path']
	plan['name'] = source_file_info['name']
	plan['action'] = action
	plan['destPath'] = source_file_info['path']		# Source path and destination paths are the same
	
	return plan


# Prepare a plan for a file or directory that already exists.
# If the path on the source is the same as the path on destination, then we can skip that file.
# If the path on the source is different from that on the destination, we need to move the file on
# the destination to bring it in compliance with the source.
def preparePlanForExistingFile(source_file_info, dest_file_info) :
	if ( source_file_info['type'] == FT_DIR ) :
		action = ACTION_SKIP					# Always skip for directories
	elif ( source_file_info['path'] == dest_file_info['path'] ) :
		action = ACTION_SKIP					# Regular file already at destination. Skip.
	else :
		action = ACTION_MOVE_FILE				# Regular file in a different location. Move it.

	plan = {}
	plan['path'] = source_file_info['path']
	plan['name'] = source_file_info['name']
	plan['action'] = action
	plan['destPath'] = dest_file_info['path']		# Source path and destination paths could be different

	return plan


# Print the plan that has been prepared
def printPlan(plan, showDetails=True) :
	if ( showDetails == True ) :
		print('This is the plan for the set of files:')
		for file_name, file_plan in plan['file_plan'].items() :
			action = file_plan['action']
			if ( action == ACTION_COPY_FILE ) :
				print(f"{file_name} in folder {file_plan['path']} --> COPY FILE into {file_plan['destPath']}")
			elif ( action == ACTION_CREATE_DIR ):
				print(f"{file_name} in folder {file_plan['path']} --> CREATE DIRECTORY in {file_plan['destPath']}")
			elif ( action == ACTION_MOVE_FILE ) :
				print(f"{file_name} in folder {file_plan['path']} --> MOVE FILE form {file_plan['destPath']} to {file_plan['path']}")
			else :
				print(f"{file_name} in folder {file_plan['path']} --> SKIP exists in {file_plan['destPath']}")

	print(f"TOTAL FILES: {plan['totals']}")
	print(f"Skip folders/files: {plan['skips']};",
		  f"Copy files: {plan['copies']}; Move files: {plan['moves']}; Create folders: {plan['creates']};")
	print("")


#
# The main entry to this script is here.
#

# Constants for types of files
FT_DIR = 1
FT_FILE = 2

# Constants for the types of actions to take
ACTION_COPY_FILE = 1
ACTION_CREATE_DIR = 2
ACTION_MOVE_FILE = 3
ACTION_SKIP = 4

# Get the year to process from the command line
year = getYearToProcess(sys.argv)

sourcePath="C:\\Users\\Jhumnu\\Pictures\\PicturesByMonths"
destPath="H:\\My Stuff\\All Pictures\\PicturesByMonths"

# Get the months in the year
visitYear(sourcePath, destPath, year)
