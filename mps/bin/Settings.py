
import os

#PROJECT CONSTANTS
use_email = False
email_user = 'circlecycle@gmail.com'
email_password = 'xxx'
path_to_storage = "/usr/local/apache2/mps_instance/storage/"
path_to_sessions = "/usr/local/apache2/mps_instance/sessions/"
db_extension = ""

#CHECK CONSTANTS and err if they aren't set
if use_email and not (email_user.count('@') and len(email_password)):
    raise "Double check the email values in the __init__.py module of mps"
    
if not path_to_storage:
    raise "Please set the path to where the storage lives"
    
if not path_to_storage:
    raise "Please set the path to where the sessions live"

#a simple template for exceptions encountered
exceptionHTML = """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"> 
    <html lang="en-US" xml:lang="en-US" xmlns="http://www.w3.org/1999/xhtml"> 
        <body>
            <div align="center">An error occured. The URL %s not valid.</div>
            <div align="center">The error is:</div>
            <pre align="center">%s</pre>
        </body>
    </html> 
"""

#a lookup of extensions->common http metadata types
metatypes = {
    'jpg':  "image/jpeg",
    'gif':  "image/gif",
    'png':  "image/png",
    'js':   "text/javascript",
    'html': "text/html",
    'htm':  "text/html",
    'xul':  "text/xul",
    'css':  "text/css",
    'pdf':  "text/pdf",
    'swf':  "application/x-shockwave-flash",
    'mp3':  "audio/mpeg",
  }