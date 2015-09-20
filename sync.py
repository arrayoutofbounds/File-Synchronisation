#!/usr/bin/env python3
import os.path
import sys
import os
import hashlib
import json
import time
from email import utils

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
	a.close()


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

	return True	


def updateSync(directory):
	''' go through the list of files in the directory, get their content and write to .sync file in json format'''

	# how to create digest
	#hash_object = hashlib.sha256(b'Hello World')
	#hex_dig = hash_object.hexdigest()
	
	#fileNames = os.listdir(directory)

	# step 1: loop though each file and then call the digest method. 
	for root,dirs,files in os.walk('./' + directory,topdown=True):

		# this got the files in the directory we entered
		for f in files:

			# if the file is a .sync file then do get information from it. i.e skip it as it does not need to be read.
			if(f == ".sync"):
				continue

			# open a file
			openedFile = open(directory + "/" + f, 'r')
			text = openedFile.read()


			# step 2: Store the digest method in the .sync file in json format
			hash_object = hashlib.sha256(text.encode())
			hex_dig = hash_object.hexdigest()
			#print(hex_dig)
			last_modified_date = time.strftime("%Y-%m-%d %H:%M:%S %z", time.gmtime(os.path.getmtime(directory + "/" + f)))

			#print (utils.formatdate(os.path.getmtime(directory + "/" + f))) # can use this for getting time zone also

			print(last_modified_date)

			dictionary = {f: [last_modified_date,1]}


			# open the .sync file in the directory given and then write to it in json format
			with open(directory + "/.sync", 'w') as outfile:
				json.dump(dictionary, outfile,indent = 4)


			# step3: go back to step 1 till no more files left



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

	# check if the sync file is created well
	syncExists = checkSyncFile(directory_1,directory_2)
	
	if(not syncExists):
		print("There were errors when creating the .sync file. Please try again!")
		return


	# now .... examine all the files present in the directories individually.
	# and use SHA 256 to create a digest and APPEND to the .sync file in that dir

	updateSync(directory_1)





main()
