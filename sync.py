#!/usr/bin/env python3
import os.path
import sys
import os
import hashlib
import json
import time
from email import utils
from datetime import datetime as dt

from datetime import datetime

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
	a.write("{\n}")
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


def addToLocalSyncFile(hex_dig,last_modified_date,dictionary,f):
	''' this function takes in the calculated hash value, last modification date, values in current .sycn file and the file name'''

	# purpose of this function is to update the .sync file.

	#print(dictionary)

	# check if the file name is in the dictionary as a key
	if f in dictionary:
		# then key exists, so first check the digest to see if same. If they are same then check mod time. else add to dictionary

		# get the digest from the dictionary
		values = dictionary[f]
		latestValues = values[0]
		latestDigest = latestValues[1]
		storedModifiedTime = latestValues[0]
		
		if(latestDigest == hex_dig):
			# old value is same as new value. So look at modification time now.


			if(storedModifiedTime == last_modified_date):
				#if the two strings are equal then the time also must be the same
				latestValues[0] = last_modified_date
			else:
				# then the times are different, then replace the latest time (which is the last_modified_time that was passed in)
				# latest values are known
				latestValues[0] = last_modified_date

		else:
			# old value is not the same as new value
			# hence add new value to the list of values	
			dictionary[f] = [[last_modified_date,hex_dig]] + dictionary[f]

	else:
		# key is not in the dictionary. So add key, value pair to the dictionary. The dictionary is empty hence you only need to add the new pair and not
		# worry about any other key that exists.
		dictionary[f] = [[last_modified_date,hex_dig]]
		#print("this is being done each time a new key is added")


	return dictionary



def updateSync(directory):
	''' go through the list of files in the directory, get their content and write to .sync file in json format'''

	# how to create digest
	#hash_object = hashlib.sha256(b'Hello World')
	#hex_dig = hash_object.hexdigest()
	
	#fileNames = os.listdir(directory)

	# step 1: loop though each file and then call the digest method. 
	for root,dirs,files in os.walk('.' + os.sep + directory,topdown=True):

		# create the dictionary that you will hold the values from the json file and use it to put to the json sync file.
		#dictionary = {}

		# open the .sync file and 
		with open(directory + os.sep + '.sync') as g:
			#dictionary = json.load(g)
			try: 
				dictionary = json.load(g)
			except ValueError: 
				#print("error caught")
				dictionary = {}
    
		
		# testing to ensure that something is read
		#print(dictionary)

		# now that the dict holds the information from the .sync file.

		#objectives:
		# 1. check if the file key exists in the dictionary
		# 2. If it does, then get the first value compare the calculated hash value with the first hashed value
		# 3. if the values are the same then check the modification time. If the modification times are same do thing, else just change mod time
		# 4. deal with delete

		# this got the files in the directory we entered
		for f in files:

			# if the file is a .sync file then do get information from it. i.e skip it as it does not need to be read.
			if(f == ".sync"):
				continue		

			# open a file
			openedFile = open(directory + os.sep + f, 'r')
			text = openedFile.read()

			# step 2: Store the digest method in the .sync file in json format
			hash_object = hashlib.sha256(text.encode())
			hex_dig = hash_object.hexdigest()
			#print(hex_dig)
			
			#last_modified_date = time.strftime("%y %m %d %T %z", time.gmtime(os.path.getmtime(directory + os.sep + f)))
			#print(last_modified_date)


			#print (utils.formatdate(os.path.getmtime(directory + "/" + f))) # can use this for getting time zone also

			# for testing
			#print(last_modified_date + " " + f )

			try:
				mtime = os.path.getmtime(directory + os.sep + f)
			except OSError:
				mtime = 0

			last_modified_date2 = dt.fromtimestamp(mtime)
			last_modified_date2 = last_modified_date2.replace(microsecond=0) # this truncates the microseconds .......for obvious reasons.
			last_modified_date2 = str(last_modified_date2) + " +1200" # adds a 1200 to the end....idk why the hell...it was shown in the requirements

			# also converted to string above so it can be storable in json

			#print(last_modified_date2)


			# now call the check function. params to pass in are : new hashed value, the dictionary, file name
			# all params in python are passed as reference
			dictionary = addToLocalSyncFile(hex_dig,last_modified_date2,dictionary,f)


			#dictionary[f] = [last_modified_date,hex_dig]  this is a useless line


			# open the .sync file in the directory given and then write to it in json format
			with open(directory +  os.sep + ".sync", 'w') as outfile:
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
	updateSync(directory_2)




main()
