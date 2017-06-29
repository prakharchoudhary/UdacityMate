"""
This script will enlist a set of filter options and then render all relevant courses.
"""

import requests
from bs4 import BeautifulSoup
import pprint
from tabulate import tabulate
import pandas as pd

def get_filters():
	"""
	only for free courses
	"""

	html = requests.get("https://in.udacity.com/courses/all/").text
	obj = BeautifulSoup(html, "html.parser")
	
	raw_categories = obj.find_all("p", class_="form-control-static")
	categories = []
	for category in raw_categories:
		categories.append(category.find("a").string)

	levels = obj.find_all("input", {"data-filter":"level"})
	course_level = [x['name'] for x in levels]

	by = obj.find_all("input", {"data-filter": "affiliate"})
	built_by = [y['name'] for y in by]

	tech = obj.find_all("input", {"data-filter": "technology"})
	technology = [x['name'] for x in tech]

	filter_dict = {
		"Categories": categories,
		"Course_level": course_level,
		"Built_by": built_by,
		"Technology": technology,
	} 

	return(filter_dict)

def show_filters(filters):

	print(tabulate(filters, headers='keys', tablefmt='fancy_grid', showindex="always"))


if __name__=="__main__":

	print("Enlisting all filters:\n")
	filters = get_filters()
	show_filters(filters)