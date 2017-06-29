"""
This script is written to scrape all the data from udacity's website about
the selected few courses whose links I have stored in a 'txt' file.

Later the script must be developed into a full scale CLI project with multiple check features and checks
to find all the 'free courses' for given categories from Udacity's catalog'.

Development Directions:

Version 1:
==========
1. Make sure the script work for given links.
2. Allow users multiple choices for finding courses, scrape these choices from catalog.
3. Once the choices are selected, use selenium to make the browser select the specific choices and obtain all courses urls.
4. Now apply the 'get_data' function to get details of every single course and present to user neatly.
5. Finally allow users to input the courses which to would like to select enroll in:
	- Ask for username, password or the social auth account details.
	- Now using selenium automatically open the selected courses page and click on the 'Start course now' button to enroll.

Version 1.1:
============
+Add feature: If user wishes to download all the youtube videos for the course,
			  then download the videos playing list from youtube(write a script to download playlists from youtube).

+Add feature: Allow users to queue their choices, while searching over and over in the same session.
			  The choices must be retained.(Use 'queue' library of python, or find a better alternative.)

Version 1.2:
============
+Add feature: Find the corresponding github projects for enrolled courses and allows users to see as well clone them locally.

+Add feature: Allow sharing of videos among users so that only one would need to download the project while the rest can simply,
			  take from her/him.

Version 1.3:
============
+Add feature: For nanodegree students, they can see how much time has passed and since they began the course,
			  Helpful as this way students can make sure they haven't crossed the 50% refund period.

Version 2.0:
============
NEW: If it feels right, go GUI!
"""


import requests
import pprint
from bs4 import BeautifulSoup

def init():
	requests.get("")

def get_data(link):
	html = requests.get(link)
	html = html.text
	obj = BeautifulSoup(html, 'html.parser')
	try:
		title = obj.find("h1", class_="hero__course--title").string
		Type = obj.find("h6", class_="hero__course--type").string
		info = obj.find("div", class_="information__summary").find("p").string
		skill_level = obj.find("div", class_="information__details").find("div", class_="icon-middle")['class'][1]
		try:
			teachers = []
			instructors = obj.findAll("h5", class_="instructor--name")
			for i in instructors:
				teachers.append(i.string)
		except Exception as e:
			print("{}: Looks like there are no instructors.".format(e))
			instructors=None
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
					 "instructors": teachers,
					 "lessons": lesson_list,
					 "req": req}
		return(link_data)
	
	except Exception as e:
		print("{}: Oops! Something went wrong....".format(e))


def print_info(links):

	for link in links:
		print("+++++++++" + link + "++++++++++")
		data = get_data(link)
		print("Title:\t\t{}\n".format(data['title'].upper()))
		print("Type:\t\t{}\n".format(data['type']))
		print("Description:\t\t{}\n".format(data['course_desc']))
		print("Skill level:\t\t{}\n".format(data['skill']))
		if len(data['instructors'])>1:
			count = 1
			print("Instructors:\n")
			for teacher in data['instructors']:
				print("\t{}. {}".format(count, teacher))
				count += 1
		else:
			print("\t--> {}".format(teacher))
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
if __name__=="__main__":

	# file = open("./js_courses.txt", "r+")
	# links = file.read()
	# links = links.split(',')
	with open("./js_courses.txt", "r") as file:
		links = file.read().split(',')
		print_info(links)




