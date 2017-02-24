# -*- coding: utf-8 -*-

## Reads the band names on reddit/r/Bandnames

import praw
import os
from time import time,sleep

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def downloadBandNames(get_all_or_new = 'new', quiet = False):
	# Download band names
	# When get_all_or_new == 'all', more duplicates are downloaded, but
	# up votes are also updated.  When it == 'new', it breaks sooner
	global current_band_names, unsaved_band_names
	# Fix get_all_or_new variable in case of user error
	get_all_or_new = get_all_or_new.lower()
	if get_all_or_new not in ['all', 'new']:
		get_all_or_new = 'new'
	
	# Login credentials
	reddit = praw.Reddit(client_id = '[CLIENT ID (no brackets)]',
					client_secret = '[CLIENT SECRET (no brackets)]',
					password = '[PASSWORD (no brackets)',
					user_agent = 'linux:bandnamegenerator:v0.0.3 (by [USER NAME] (no brackets))',
					user_name = '[USER NAME] (no brackets)'
					)

	# Break when there are duplicates
	duplicates = 0
	if get_all_or_new == 'new':
		duplicate_limit = 50
	else:
		duplicate_limit = 500
	
	for submission in reddit.subreddit("Bandnames").new(limit = None):
		band_name = submission.title
		band_name_score = submission.score
		
		# Remove ampersand from band_name
		band_name = band_name.replace('&', 'and')
		
		if band_name in current_band_names:
			new_band_name = False
			# Update score
			current_band_names[band_name] = band_name_score
			# Break if duplicate_limit has been hit
			duplicates += 1
			if duplicates >= duplicate_limit:
				print 'Info: Duplicate limit reached ({})'.format(duplicates)
				break
		else:
			new_band_name = True
		
		if not quiet:
			if new_band_name:
				print 'Band Name: {} ({})'.format(band_name, band_name_score)
			else:
				#print 'Band Name Already Saved ({})'.format(band_name)
				pass

		if new_band_name: 
			unsaved_band_names[band_name] = band_name_score
		
		
		# Save new bands to file periodically
		if len(unsaved_band_names) > 25:
			current_band_names = mergeDicts(current_band_names, unsaved_band_names)
			unsaved_band_names = saveBandNames(unsaved_band_names)
		

def loadBandNames():
	# Set band names to empty dict in case of error
	band_names = {}
	if os.path.exists(band_name_list_filename):
		# Read band names and scores from file
		with open(band_name_list_filename,'r') as f:
			for line in f:
				# Strip line
				line = line.strip()
				# Get score from end of line
				band_name = ', '.join(line.split(', ')[:-1])
				band_name_score = line.split(', ')[-1]
				# Add name and score to dictionary
				band_names[band_name] = band_name_score
	else:
		print 'Band Name List not found:', band_name_list_filename
		
	return band_names
	
	
def saveBandNames(band_names):
	# Append new band names to file
	with open(band_name_list_filename, 'a') as f:
		for band_name in band_names.keys():
			f.write('{}, {} \n'.format(band_name, band_names[band_name]))
		
	print '{} Band Names saved.'.format(len(band_names))
	
	# Return blank dict after appending save file
	return {}


def mergeDicts(x, y):
    # Merge two dictionaries
    z = x.copy()
    z.update(y)
    return z


def getTopRated(limit = 5):
	# Get top rated band names from list
	# Check if dictionary has values
	if current_band_names:
		return sorted(current_band_names, key=current_band_names.get, reverse=True)[:limit]
	else:
		print 'ERROR: No band name list loaded!'
		return []


# Save file where band names are stored
band_name_list_filename = 'bandnames.txt'

# Dict to keep track of new downloaded names
unsaved_band_names = {}

# Dict to store loaded band names
current_band_names = {}


if __name__ == "__main__":
	# Get start_time
	start_time = time()
	
	# Load band name list
	print 'Loading saved band names...'
	current_band_names = loadBandNames()

	# Store previous name list len before downloading
	loaded_band_len = len(current_band_names)
	
	print '{} band names loaded'.format(loaded_band_len)

	# Download new name submissions
	print 'Downloading new band names...'
	downloadBandNames(get_all_or_new = 'new')
	
	# Merge and save new downloaded band names if available
	if unsaved_band_names:
		current_band_names = mergeDicts(current_band_names, unsaved_band_names)
		saveBandNames(unsaved_band_names)
	
	# Get top rated list
	top_rated = getTopRated(10)
	print '----------\nTop rated:\n----------'
	for tr in top_rated:
		print '{} ({})'.format(tr, current_band_names[tr])
	
	# Print list update results
	print '----------'
	print 'New Names Downloaded: {}'.format(len(current_band_names) - loaded_band_len)
	print 'Time: {}s'.format(round(time()-start_time, 2))
	
