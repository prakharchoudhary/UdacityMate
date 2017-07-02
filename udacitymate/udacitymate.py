#!/usr/bin/python

"""
This script is developed as a full scale CLI project with multiple check features
to find all the 'free courses' for given categories from Udacity's catalog.
"""

import sys
import pprint
from tabulate import tabulate
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


######################################### LIST ALL FILTERS ############################################
def get_filters():
	"""
	1. only for free courses.
	2. scrapes options from catalog.
	"""

	html = requests.get("https://in.udacity.com/courses/all/").text
	obj = BeautifulSoup(html, "html.parser")

	levels = obj.find_all("input", {"data-filter":"level"})
	course_level = [x['name'] for x in levels]

	by = obj.find_all("input", {"data-filter": "affiliate"})
	built_by = [y['name'] for y in by]

	tech = obj.find_all("input", {"data-filter": "technology"})
	technology = [x['name'] for x in tech]

	filter_dict = {
		"Course_level": course_level,
		"Built_by": built_by,
		"Technology": technology,
	} 

	return(filter_dict)

def show_filters(filters):
	"""
	1. Tabulates for better readability.
	"""
	print(tabulate(filters, headers='keys', tablefmt='fancy_grid', showindex="always"))


def list_filters():
	"""
	1. Binds the above two functions and prints the table.
	"""
	print("Enlisting all filters:\n")
	filters = get_filters()
	show_filters(filters)

#########################################################################################################



################################# FIND RELEVANT COURSES #################################################

class FindCourses(object):
	"""
	This class is responsible for automatically selected the entered choices,
	on the catalog page and scraping urls of the final relevant courses.
	"""
	def init_driver(self):
		"""
		intitializes the driver
		"""
		driver = webdriver.Firefox()
		driver.wait = WebDriverWait(driver, 50000)
		return driver

	def select_fields(self, driver, choices):
		"""
		1. selects the chosen fields.
		2. Scrapes the urls and returns as a list.
		"""
		driver.get("https://in.udacity.com/courses/all/")
		
		course_type = driver.wait.until(EC.presence_of_element_located(
										(By.NAME, "Free Course")))
		course_type.click()

		if choices['built_by'] != ['']:
			for org in choices['built_by']:
				built_by = driver.wait.until(EC.presence_of_element_located(
									(By.NAME, org)))
				built_by.click()

		if choices['course_level'] != ['']:
			for level in choices['course_level']:
				course_level = driver.wait.until(EC.presence_of_element_located(
										(By.NAME, level)))
				course_level.click()

		if choices['technology'] != ['']:
			for tech in choices['technology']:
				technology = driver.wait.until(EC.presence_of_element_located(
										(By.NAME, tech)))
				technology.click()

		html = driver.page_source
		obj = BeautifulSoup(html, "html.parser")
		all_matches = obj.find_all("div", {"data-filter-state": "show"})
		matched_courses = []
		for item in all_matches:
			matched_courses.append("https://www.udacity.com" + item.find("a")['href'])

		return matched_courses

	# the above function gives us a list of all urls that match our provided parameters
	# Now simply run the data.py for this list and find scrap the data on each course.
	def binder(self, filters):
		"""
		The binder function.
		"""
		driver = self.init_driver()
		recomm_courses = self.select_fields(driver, filters)
		driver.close()
		return recomm_courses


#########################################################################################################


################################# SCRAPE DATA FOR EACH COURSE ###########################################

def get_data(link):
	"""
	Scrapes the course details for a given url.
	"""

	html = requests.get(link)
	html = html.text
	obj = BeautifulSoup(html, 'html.parser')
	try:
		title = obj.find("h1", class_="hero__course--title").string
		Type = obj.find("h6", class_="hero__course--type").string
		info = obj.find("div", class_="information__summary").find("p").string
		skill_level = obj.find("div", class_="information__details").find("div", class_="icon-middle")['class'][1]
		try:
			time = obj.find("div", class_="information__details").find_all("div", class_="section--top")[0]
			timeline = time.find_all("h5")[1].string

		except Exception as e:
			timeline = "No expected time of completion."

		try:
			teachers = []
			instructors = obj.findAll("h5", class_="instructor--name")
			for i in instructors:
				teachers.append(i.string)

		except Exception as e:
			print("{}: Looks like there are no instructors.".format(e))
			teachers=None
			pass

		lesson_list = []
		lessons = obj.findAll("a", class_="card--lesson")
		try:
			for lesson in lessons:
				lnum = lesson.find("h6", class_="mb-half").string
				ltitle = lesson.find("h4", class_="mb-0").string
				l_details = lesson.findAll("li")
				ldetails = []
				for i in l_details:
					ldetails.append(i.string)
				less_dict = {"lesson_number":lnum, "lesson_title": ltitle, "ldetails": ldetails}
				lesson_list.append(less_dict)
		except TypeError as e:
			print("{}: Go check the DOM again, and test in shell too.".format(e))
		req = obj.findAll("div", class_="course-reqs--summary")

		link_data = {"title": title,
					 "type": Type,
					 "course_desc": info,
					 "skill": skill_level,
					 "timeline": timeline,
					 "instructors": teachers,
					 "lessons": lesson_list,
					 "req": req}
		return(link_data)
	
	except Exception as e:
		print("{}: Oops! Something went wrong....".format(e))


def whatisthis(s):
    """
    For python2.x:
    	Finds if something is unicode or not.
    """
    if isinstance(s, str):
        return False
    elif isinstance(s, unicode):
        return True

def print_info(links):
	"""
	Prints the course details on the terminal.
	"""

	for link in links:
		print("\n+++++++++" + link + "++++++++++\n")
		data = get_data(link)
		print("Title:\t\t{}\n".format(data['title'].upper()))
		print("Type:\t\t{}\n".format(data['type']))
		print("Description:\t\t{}\n".format(data['course_desc']))
		print("Skill level:\t\t{}\n".format(data['skill']))
		print("Timeline:\t\t{}\n".format(data['timeline']))
		if len(data['instructors'])>=1:
			count = 1
			print("Instructors:\n")
			for teacher in data['instructors']:
				print("\t{}. {}".format(count, teacher))
				count += 1
		else:
			print("\t--> No instructors")
		print("\n")
		print("### DETAILS: ###")
		for lesson in data['lessons']:
			print("{}: {}\n".format(lesson['lesson_number'], lesson['lesson_title']))
			count = 1
			for l in lesson['ldetails']:				
				print("{}. {}".format(count, l))
				count += 1
			print("\n")
		# For requirements: Find a way to scrape out only technology names and any links corressponding to them.
		print("\n############################################################################################################################\n")

#########################################################################################################


############################# CLEAN INPUT BEACUSE USERS ARE IDIOTS ######################################

def users_are_idiots(string):
	"""
	splits the input strings and removes any preceeding or trailing whitespaces.
	"""

	s = string.split(",")
	s = [i.strip() for i in s]
	return s


def filter_dict(course_level, built_by, technology):
	"""
	creates the final dict that has all the data
	"""

	d = {
		"built_by": users_are_idiots(built_by),
		"course_level": users_are_idiots(course_level),
		"technology": users_are_idiots(technology),
	}

	return d

def main():

	list_filters()
	print("Enter your filters:")
	
	version = sys.version_info

	if version.major==3 and version.minor>=4:

		built_by = input("Search by affiliated to(seperate using commas): ")

		course_level = input("Search by course level(seperate using commas): ")

		technology = input("Search by technologies(seperate using commas): ")

	elif version.major==2 and version.minor>=6:

		built_by = raw_input("Search by affiliated to(seperate using commas): ")

		course_level = raw_input("Search by course level(seperate using commas): ")

		technology = raw_input("Search by technologies(seperate using commas): ")

	filters = filter_dict(course_level, built_by, technology)

	match_class = FindCourses()
	matches = match_class.binder(filters)

	print_info(matches)

#########################################################################################################


if __name__ =="__main__":

	main()


