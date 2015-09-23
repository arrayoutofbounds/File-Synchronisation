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


def addToLocalSyncFile(hex_dig,last_modified_date,dictionary,f,directory):
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


			if(storedModifiedTime != last_modified_date):
				#if the two strings are equal then the time also must be the same
				#((dictionary[f])[0])[0] = last_modified_date
				#latestValues[0] = last_modified_date
				# then the times are different, then replace the latest time (which is the last_modified_time that was passed in)
				# latest values are known
				print(storedModifiedTime + "THIS")

				# update the modified time of the file to the time from the stored sync file 
				os.utime(directory + os.sep + f,(time.mktime(time.strptime(storedModifiedTime, "%Y-%m-%d %H:%M:%S %z")),time.mktime(time.strptime(storedModifiedTime, "%Y-%m-%d %H:%M:%S %z"))))
				#((dictionary[f])[0])[0] = last_modified_date
				#latestValues[0] = last_modified_date

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

def dumpJson(dictionary,directory):
	with open(directory +  os.sep + ".sync", 'w') as outfile:
		json.dump(dictionary, outfile,indent = 4)	

def checkForDeletedFiles(directory,dictionary,dir2):
	''' this will loop through all the keys in the dictionary and from the .sync file. Any miss will signal that the file was deleted'''

	# step 1 = loop through directory and get list of files
	# step 2 = loop through all keys in dict
	# step 3 = if key in dict but NOT IN list of files, then it is deleted. So edit the dictionary. 


	listOfFiles = [] # that are in the dir
	listOfKeys = [] # from the sync file of the dir

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

		# if a file has already been deleted then just change the time to the current time
		if (digest == "deleted"):
			# then just change the time to the current time as the entry for deletion already exists
			now = datetime.datetime.now()
			now = now.replace(microsecond=0)

			# CHEAT ADD IN
			now = str(now) + " +1200"

			((dictionary[key])[0])[0] = str(now)
		else:	

			# DELETED file has not been recorded as deleted. So add it into the .sync file

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

				# CHEAT ADD IN
				now = str(now) + " +1200"


				dictionary[key] = [[now,"deleted"]] + dictionary[key]


				# the file in the other directory has to also be deleted.
				with open(dir2 + os.sep + '.sync') as g:
					try: 
						dict2 = json.load(g)
					except ValueError: 
						dict2 = {}	


				for root,dirs,files in os.walk('.' + os.sep + dir2,topdown=True):

					if key in files:
						os.remove(dir2 + os.sep + key)
						dict2[key] = [[now,"deleted"]] + dict2[key]
						dumpJson(dict2,dir2)	


	return dictionary		
	



def updateSync(directory,dir2):
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

			
			last_modified_date = time.strftime("%Y-%m-%d %H:%M:%S %z", time.localtime(os.path.getmtime(directory + os.sep + f)))

			print(last_modified_date + " " + f + " " + directory)


			#print (utils.formatdate(os.path.getmtime(directory + "/" + f))) # can use this for getting time zone also

			# for testing
			#print(last_modified_date + " " + f )

			'''
			try:
				mtime = os.path.getmtime(directory + os.sep + f)
			except OSError:
				mtime = 0

			last_modified_date2 = dt.fromtimestamp(mtime)
			last_modified_date2 = last_modified_date2.replace(microsecond=0) # this truncates the microseconds .......for obvious reasons.
			last_modified_date2 = str(last_modified_date2) + " +1200" # adds a 1200 to the end....idk why the hell...it was shown in the requirements

			'''

			# also converted to string above so it can be storable in json

			#print(last_modified_date2)


			# THIS IS TO CONVERT THE TIME IN STRING BACK TO DATETIME TO COMPARE
			#print(datetime.datetime.strptime(last_modified_date2, "%Y-%m-%d %H:%M:%S +1200"))

			# now call the check function. params to pass in are : new hashed value, the dictionary, file name
			# all params in python are passed as reference

			#dictionary = addToLocalSyncFile(hex_dig,last_modified_date2,dictionary,f)

			dictionary = addToLocalSyncFile(hex_dig,last_modified_date,dictionary,f,directory)


			#dictionary[f] = [last_modified_date,hex_dig]  this is a useless line


			# open the .sync file in the directory given and then write to it in json format
			with open(directory +  os.sep + ".sync", 'w') as outfile:
				json.dump(dictionary, outfile,indent = 4)


			# step3: go back to step 1 till no more files left
			print(last_modified_date)

		# check for deleted files and then json dump to file again to update it as something may have been deleted	
		dictionary = checkForDeletedFiles(directory,dictionary,dir2)	

		print(dictionary)
		with open(directory +  os.sep + ".sync", 'w') as outfile:
				json.dump(dictionary, outfile,indent = 4)

def move(directory_1,directory_2,key):

	#print(directory_1)
	#print(directory_2)
	#print(key)

	# move from dir1 to dir 2
	# this copies the metadata as well
	shutil.copy2(directory_1 + os.sep + key,directory_2)



def mergeMissingFiles(directory_1,directory_2,dictionary_1,dictionary_2):

	''' this method just ensure that any files that are missing in either directory are sent to the other dir'''

	print(dictionary_1)
	print(dictionary_2)

	for key in dictionary_1.keys(): # go through the sync file for the first directory

		a = dictionary_1[key] # get all the values
		b = a[0] # get the first value
		c = b[1] # get the digest from the first value....latest content hash

		if(c == "deleted"):  # if the latest content was deleted then just skip this key as file does not exist so no way to merge
			continue

		#print(key + " " +  directory_1)

		# if key is in the second dir dictoinary then continue...this is hack as if it is not done then a file that was deleted will not be put back
		# hence both dirs will not have the same number of files
		if(key in dictionary_2.keys()):
			try:
				value = dictionary_2[key]
				latestValue = value[0]
				latestDigest = latestValue[1]
			except ValueError:
				latestDigest = "nothing"	

		# only goes through the if statement if the value in the second dir was "deleted". That would mean the key was there but the file wasnt, hence the file
		# would need to be copied.
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

			# updates the dictionary
			dictionary_2[key] = [[storedModifiedTime,latestDigest]]


	# same as the above for loop, except this moves files that are not in dir 1 but are in dir 2 to dir 1.
	for key in dictionary_2.keys():

		d = dictionary_2[key]
		e = d[0]
		f = e[1]

		if(f == "deleted"):
			continue

		#print(key + " " + directory_2)	
		if(key in dictionary_1.keys()):
			try:
				value = dictionary_1[key]
				latestValue = value[0]
				latestDigest = latestValue[1]
			except:
				latestDigest = "nothing"
	
		if key in dictionary_1 and (latestDigest != "deleted"):
			pass
		else:
			move(directory_2,directory_1,key)	 # move file from dir 2 to dir 1 as dir 1 does not have the file

			values = dictionary_2[key]
			latestValue = values[0]
			storedModifiedTime = latestValue[0]
			latestDigest = latestValue[1]

			# update the dir 1 dictionary
			dictionary_1[key] = [[storedModifiedTime,latestDigest]]


	# update the sync files on both dirs
	dumpJson(dictionary_1,directory_1)
	dumpJson(dictionary_2,directory_2)

def syncDirs(directory_1, directory_2, dictionary_1,dictionary_2):

	''' both dirs have same number and type of files. This method ensure that all files are the same and up to date'''

	# return the dictionaries in the end. Then they will be stored back using json.dump in the calling function.

	# first compare the digest for a key in both sync files. 

	for key in dictionary_1: # can choose any dictionary as the keys will be the same
		# dict 1 points to the first directory sync file

		#get the values
		values1 = dictionary_1[key]
		values2 = dictionary_2[key]

		# get the array of latest value
		latestValue_1 = values1[0]
		latestValue_2 = values2[0]

		# get the latest modified time from the array 
		last_modified_time_1 = latestValue_1[0]
		last_modified_time_2 = latestValue_2[0]

		# get the latest hash digest from the array
		digest_1 = latestValue_1[1]
		digest_2 = latestValue_2[1]


		# if the digest are the same then only the modified time needs to be changed
		if(digest_1 == digest_2):
			# this means that the content of both the files is the same
			# now check the modification times


			time_1 = datetime.datetime.strptime(last_modified_time_1, "%Y-%m-%d %H:%M:%S %z")
			time_2 = datetime.datetime.strptime(last_modified_time_2, "%Y-%m-%d %H:%M:%S %z")




			# if time is greater than another then it is the earliest 
			#print(time_1)
			#print(time_2)
			#print(time_1 > time_2)

			#CHANGE MOD TIME OF FILE AND SYNC FILE
			if(time_1 > time_2):
				# then time 1 is closer to current time
				# so set the time in the .sync files of both to that time
				((dictionary_1[key])[0])[0] = str(time_1).replace("+12:00"," +1200")
				((dictionary_2[key])[0])[0] = str(time_1).replace("+12:00"," +1200")

				os.utime(directory_1 + os.sep + f,(time.mktime(time.strptime(last_modified_time_1, "%Y-%m-%d %H:%M:%S %z")),time.mktime(time.strptime(last_modified_time_1, "%Y-%m-%d %H:%M:%S %z"))))
				os.utime(directory_2 + os.sep + f,(time.mktime(time.strptime(last_modified_time_1, "%Y-%m-%d %H:%M:%S %z")),time.mktime(time.strptime(last_modified_time_1, "%Y-%m-%d %H:%M:%S %z"))))

			elif(time_2 > time_1):
				# latest time is the time 2
				((dictionary_1[key])[0])[0] = str(time_2).replace("+12:00"," +1200")
				((dictionary_2[key])[0])[0] = str(time_2).replace("+12:00"," +1200")

				os.utime(directory_1 + os.sep + f,(time.mktime(time.strptime(last_modified_time_2, "%Y-%m-%d %H:%M:%S %z")),time.mktime(time.strptime(last_modified_time_2, "%Y-%m-%d %H:%M:%S %z"))))
				os.utime(directory_2 + os.sep + f,(time.mktime(time.strptime(last_modified_time_2, "%Y-%m-%d %H:%M:%S %z")),time.mktime(time.strptime(last_modified_time_2, "%Y-%m-%d %H:%M:%S %z"))))
			else:
				# they are both the same...so dont change anything
				pass
		else:
			#this means that the content they hold is different.
			# check if the values length is 2 or greater.
			# if it is then compare second value of 2nd dir with 1st of dir1
			# then .....
			
			# if dictionary 2 has a length of 2 or more then it can have the same version as that of most recent of dict 1.

			matchFound = False # this is there to check whether a match is found for any of the previous versions of files on opp dir

			if(len(values2) >= 2):
				# then we can check the 1st index, which is the previous version, with the current version of dir 1

				listValues = values2

				del listValues[0] # because we want to check if digest is same as earlier version in second directory
				
				# we have list of values for a given key	

				# get  earlier digest of 2nd dir and check if it matches 
				for j in listValues:

					if(digest_1 == j[1]):

						# then the first version of dir 1 is same as the currently examined but previous in dir 2
						# so copy over the file with the current key to dir 1 and then update the sync file

						move(directory_2,directory_1,key) # this copies the file from dir 2 to dir 1 with all the metadata

						# update the .sync file. Update the dictionary. The dict will be json dumped at the end of this method. so its updated the .sync
						# you have to
						# put the [modified time, digest] to the .sync file of the directory_1

						hex_dig = j[1]
						modified_date = j[0]

						dictionary_1[key] = [[modified_date,hex_dig]] + dictionary_1[key]

						matchFound = True # this is set true as there is a file that is a earlier version in the other dir

			if(len(values1)>=2):

				# check if the current file in dir 2 is same as any of the previous versions of dir 1
				listValues = values1

				del listValues[0] # because we want to check if digest is same as earlier version in second directory
				
				# we have list of values for a given key	

				# get  earlier digest of 2nd dir and check if it matches 
				for j in listValues:

					if(digest_2 == j[1]):

						# then the first version of dir 1 is same as the currently examined but previous in dir 2
						# so copy over the file with the current key to dir 1 and then update the sync file

						move(directory_1,directory_2,key) # this copies the file from dir 1 to dir 2 with all the metadata

						# update the .sync file. Update the dictionary. The dict will be json dumped at the end of this method. so its updated the .sync
						# you have to
						# put the [modified time, digest] to the .sync file of the directory_1

						hex_dig = j[1]
						modified_date = j[0]

						dictionary_2[key] = [[modified_date,hex_dig]] + dictionary_2[key]

						matchFound = True # set true as there is a file in dir 1 that is an earlier version as current of dir 2

			# now the if statements has been run to ensure that if there were previous versions then they have been updated with the sync file
			# however, if both the if statements are not fulfilled because the digests are both unique and there is nothing with the same content anywhere
			# in the opposite directory, then 

			# get most recent time for the key from both dir and then apply that file and sync it

			# so if the match found variable is false, then neither dir was able to find a file that was matching in the other dir

			if (not matchFound): # if both files are unique amongst the SET of all files contents from opposite directories then just get the file with the latest time

			# both lists bigger than 1
			# check index 1 
			# if they are both same tehn top one ins diff....then check time

				time_1 = datetime.datetime.strptime(last_modified_time_1, "%Y-%m-%d %H:%M:%S %z")
				time_2 = datetime.datetime.strptime(last_modified_time_2, "%Y-%m-%d %H:%M:%S %z")

				if(time_1 > time_2):

					# from dir 1 as it is newer
					mod_time = ((dictionary_1[key])[0])[0]
					digest = ((dictionary_1[key])[0])[1]


					# should add a new entry into the dict, hence the sync file
					dictionary_2[key] = [[mod_time,digest]] + dictionary_2[key]


					move(directory_1,directory_2,key) # copy the latest file from dir 1 to dir2

					#((dictionary_2[key])[0])[0] = str(time_1)


				elif(time_2 > time_1):

					mod_time = ((dictionary_2[key])[0])[0]
					digest = ((dictionary_2[key])[0])[1]

					# should add a new entry into the dict, hence the sync file
					dictionary_1[key] = [[mod_time,digest]] + dictionary_1[key]

					move(directory_2,directory_1,key) # copy the latest file from dir 2 to dir 1



					#((dictionary_1[key])[0])[0] = str(time_2)
				else:
					pass


	# load the dict in the .sync files for each

	# the dict has been changed for each of the files present

	print(dictionary_1)
	print(dictionary_2)

	with open(directory_1 +  os.sep + ".sync", 'w') as outfile:
		json.dump(dictionary_1, outfile,indent = 4)

	with open(directory_2 +  os.sep + ".sync", 'w') as outfile:
		json.dump(dictionary_2, outfile,indent = 4)



def merging(directory_1,directory_2):

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

	# now that missing files have been copied over.
	# merge the directories
	syncDirs(directory_1, directory_2, dictionary_1,dictionary_2)

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

	updateSync(directory_1,directory_2) #dir 1 updated and deleted files checked
	updateSync(directory_2,directory_1) # same as above but for dir 2

	merging(directory_1,directory_2)



main()
