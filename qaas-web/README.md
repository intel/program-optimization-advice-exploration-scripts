GUI and Database
================

Installation
-------------------------
1. Follow [topmost installation instruction](../README.md)
   - The topmost setup.sh script will run setup.sh script of Webfront and database to do the following automatically
     - Build web code
     - Build database
2. Install web certificate [optional and manual]
   - Use can install the web certificate to the web server folder and the volume feature of docker will keep the certificate persistent.    

Using the GUI and Database
--------------------------

### Run QaaS Web Front
- For security measures,
  - need to enable HTTPS connection.
  - debug feature is disabled by default.  Developer needs to enable it by updating source code to set debug parameters for various components.
  - to limit the HTTP request body size, can use the maxAllowedContentLength to limit size, or other commands depending on the type of the webservers.
  - User should follow security tips when deploying current webapp to production web servers.
- Also should enable TLS for further safety in data transfer.
- To limit message size, set maxContentLength variable (e.g. to 10000) on React async() call to receive request.
