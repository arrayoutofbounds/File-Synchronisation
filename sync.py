#!/usr/bin/env python3

import sys
import os

def makeDir(directory):
	os.makedirs(directory)


def check(directory_1,directory_2):
	''' check if path exists and return a list'''

	dir1_exists = False
	dir2_exists = False


	if(os.path.exists(directory_1)):  # if path exists then check if it is a dir
		if (os.path.isdir(directory_1)): # if the path is a dir then carry on
			dir1_exists = True
			pass
		else: # if there is a path and it is not a dir then print and return False
			print("Please ensure that path is to a directory, not a file")
			return False

	if(os.path.exists(directory_2)): # if the path exists then check to see if it is dir
		if (os.path.isdir(directory_2)): # if it is a dir then carry on, else return False
			dir2_exists = True
			pass
		else:
			print("Please ensure that path is to a directory, not a file")
			return False

	# now check that dir1_exists and dir2_exists are true. If not then make the directory in another function and then return.

	if(dir1_exists): # if dir exists and carry on else make it
		pass
	else:
		makeDir(directory_1)

	if(dir2_exists): # if dir exists then carry on else make it
		pass
	else:
		makeDir(directory_2)
	
	return True


def makeSync(path):

	a = open(path,"w+")



def checkSyncFile(directory_1,directory_2):
	''' check if a .sync file exists in both directories. If it does then carry on, else make the file'''

	fileName = '.sync'

	path1 = os.path.join(directory_1,fileName)
	path2 = os.path.join(directory_2,fileName)

	if(os.path.isfile(path1)):
		pass
	else:
		makeSync(path1)

	if(os.path.isfile(path2)):
		pass
	else:
		makeSync(path2)	



def main():
	
	# get list of arguments. It will be liike ['./sync.py', 'dir1', 'dir2']
	arguments = sys.argv


	# if not enough arguments then exit
	if(len(arguments) < 3):
		print("Please enter 2 arguments")
		return

	# get the directories as variables
	directory_1 = arguments[1]
	directory_2 = arguments[2]

	result = check(directory_1,directory_2)

	# if the result of making and checking the directories was true then carry on, else return with a failed value.
	if(not result):
		return


	syncExists = checkSyncFile(directory_1,directory_2)
	





main()
