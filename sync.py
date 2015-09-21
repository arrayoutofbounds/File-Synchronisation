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

import datetime

import shutil

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

def checkForDeletedFiles(directory,dictionary):
	''' this will loop through all the keys in the dictionary and from the .sync file. Any miss will signal that the file was deleted'''

	# step 1 = loop through directory and get list of files
	# step 2 = loop through all keys in dict
	# step 3 = if key in dict but NOT IN list of files, then it is deleted. So edit the dictionary. Since it is a reference....no need to return it.


	listOfFiles = []
	listOfKeys = []

	#step 1
	for root,dirs,files in os.walk('.' + os.sep + directory,topdown=True):

		for f in files:
			if(f == ".sync"):
				continue	
			listOfFiles.append(f)

	
	#step 2
	for key in dictionary.keys():
		listOfKeys.append(key)

	#step 3
	for key in listOfKeys:

		value = dictionary[key]
		latestValue = value[0]
		digest = latestValue[1]

		if (digest == "deleted"):
			# then just change the time to the current time as the entry for deletion already exists
			now = datetime.datetime.now()
			now = now.replace(microsecond=0)
			latestValue[0] = str(now)
		else:	
			# deleted string is not there
			if key in listOfFiles:
				# then file is not deleted
				# carry on by doing nothing
				pass
			else:
				# the file is obviously deleted because it is not there in dir but is there in sync dictionary
				# hence add the current time and the "deleted" keyword
				now = datetime.datetime.now()
				now = now.replace(microsecond=0)

				dictionary[key] = [[str(now),"deleted"]] + dictionary[key]

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
		dictionary = checkForDeletedFiles(directory,dictionary)	
		with open(directory +  os.sep + ".sync", 'w') as outfile:
				json.dump(dictionary, outfile,indent = 4)

def move(directory_1,directory_2,key):

	print(directory_1)
	print(directory_2)
	print(key)

	shutil.copy(directory_1 + os.sep + key,directory_2)

def dumpJson(dictionary,directory):
	with open(directory +  os.sep + ".sync", 'w') as outfile:
		json.dump(dictionary, outfile,indent = 4)

def mergeMissingFiles(directory_1,directory_2,dictionary_1,dictionary_2):

	for key in dictionary_1.keys():

		a = dictionary_1[key]
		b = a[0]
		c = b[1]

		if(c == "deleted"):
			continue

		print(key + " " +  directory_1)

		try:
			value = dictionary_2[key]
			latestValue = value[0]
			latestDigest = latestValue[1]
		except ValueError:
			latestDigest = "nothing"	

		if key in dictionary_2 and (latestDigest != "deleted") :
			pass
		else:
			# copy to directory 2 and and key,value to .sync file of the 2nd dir
			move(directory_1,directory_2,key)

			# get latest values for the key that is to be copied
			values = dictionary_1[key]
			latestValue = values[0]
			storedModifiedTime = latestValue[0]
			latestDigest = latestValue[1]

			dictionary_2[key] = [[storedModifiedTime,latestDigest]]


	for key in dictionary_2.keys():

		d = dictionary_2[key]
		e = d[0]
		f = e[1]

		if(f == "deleted"):
			continue

		print(key + " " + directory_2)	
		try:
			value = dictionary_1[key]
			latestValue = value[0]
			latestDigest = latestValue[1]
		except:
			latestDigest = "nothing"
	
		if key in dictionary_1 and (latestDigest != "deleted"):
			pass
		else:
			move(directory_2,directory_1,key)	

			values = dictionary_2[key]
			latestValue = values[0]
			storedModifiedTime = latestValue[0]
			latestDigest = latestValue[1]

			dictionary_1[key] = [[storedModifiedTime,latestDigest]]

	dumpJson(dictionary_1,directory_1)
	dumpJson(dictionary_2,directory_2)
			

def merge(directory_1,directory_2):

	''' the purpose of this method is to merge the files on the 2 directories give'''

	#step 1. open the sync file from both dirs
	with open(directory_1 + os.sep + '.sync') as g:
		#dictionary = json.load(g)
		try: 
			dictionary_1 = json.load(g)
		except ValueError: 
			#print("error caught")
			dictionary_1 = {}

	with open(directory_2 + os.sep + '.sync') as h:

		try:
			dictionary_2 = json.load(h)
		except ValueError:
			dictionary_2 = {}

	# now do the sync for any files that are not in either directories
	mergeMissingFiles(directory_1, directory_2, dictionary_1,dictionary_2)		

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

	merge(directory_1,directory_2)




main()
