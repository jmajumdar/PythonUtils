import os
import glob
import sys
import getopt


# The function processes the command line arguments and determines the various options
def getOptions(argv) :
	options = { 'year' : '2020', 'month' : '', 'verbose' : 'False' }
	usage = 'Usage >> backupPics.py [-h|--help] [-v|--verbose] [--year|-y <year>] [--month|-m <month>]' 
	try:
		opts, args = getopt.getopt(argv[1:],"hvy:m:",["year=","month=","help","verbose"])
	except getopt.GetoptError :
		print(usage)
		sys.exit(2)

	for opt, value in opts:
		if opt in ('-h', "--help") :
			print(usage)
			sys.exit()
		elif opt in ("-y", "--year") :
			options['year'] = value
		elif opt in ("-m", "--month") :
			options['month'] = value
		elif opt in ('-v', '--verbose') :
			options['verbose'] = 'True'

	#print('Execution Options', options)
	return options


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
def visitYear(sourcePath, destPath, options) :
	year = options['year']
	if ( options['month'] == '' ) :
		months = getMonths(sourcePath, year)
	else :
		months = [ options['month'] ]
	showDetails = ( options['verbose'] == 'True' )
	
	for month in months :
		sourceDict = buildFileDict(sourcePath + '\\' + year, month)
		destDict = buildFileDict(destPath + '\\' + year, month)
		printPlan(preparePlan(sourceDict, destDict), showDetails)


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
	overall_plan = { 'copies':[], 'moves':[], 'creates':[], 'skips':[] }
	
	for source_file, source_file_info in sourceDict.items() :
		dest_file_info = destDict.get(source_file)
		if ( dest_file_info == None ) :
			appendPlan(preparePlanForNewFile(source_file_info), overall_plan)
		else :
			appendPlan(preparePlanForExistingFile(source_file_info, dest_file_info), overall_plan)

	overall_plan['copy_count'] = copy_count = len(overall_plan['copies'])
	overall_plan['move_count'] = move_count = len(overall_plan['moves'])
	overall_plan['create_count'] = create_count = len(overall_plan['creates'])
	overall_plan['skip_count'] = skip_count = len(overall_plan['skips'])
	overall_plan['total_count'] = copy_count+move_count+create_count+skip_count
	return overall_plan


# Append paln for the file to the appropriate list
def appendPlan(file_plan, overall_plan) :
	if ( file_plan['action'] == ACTION_COPY_FILE ) :
		overall_plan['copies'].append(file_plan)
	elif ( file_plan['action'] == ACTION_MOVE_FILE ) :
		overall_plan['moves'].append(file_plan)
	elif ( file_plan['action'] == ACTION_CREATE_DIR ) :
		overall_plan['creates'].append(file_plan)
	else :
		overall_plan['skips'].append(file_plan)
	return overall_plan


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
		for file_plan in plan['creates'] :
			print(f"{file_plan['name']} in folder {file_plan['path']} --> CREATE DIRECTORY in {file_plan['destPath']}")
		for file_plan in plan['copies'] :
			print(f"{file_plan['name']} in folder {file_plan['path']} --> COPY FILE into {file_plan['destPath']}")
		for file_plan in plan['moves'] :
			print(f"{file_plan['name']} in folder {file_plan['path']} --> MOVE FILE form {file_plan['destPath']} to {file_plan['path']}")
		for file_plan in plan['skips'] :
			print(f"{file_plan['name']} in folder {file_plan['path']} --> SKIP exists in {file_plan['destPath']}")

	print(f"TOTAL FILES: {plan['total_count']}")
	print(f"Skip folders/files: {plan['skip_count']};",
		  f"Copy files: {plan['copy_count']}; Move files: {plan['move_count']}; Create folders: {plan['create_count']};")
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

# Get the options from the command line and collect these into a dictionary
options = getOptions(sys.argv)

sourcePath="C:\\Users\\Jhumnu\\Pictures\\PicturesByMonths"
destPath="H:\\My Stuff\\All Pictures\\PicturesByMonths"

# Get the months in the year
visitYear(sourcePath, destPath, options)
