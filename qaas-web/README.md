## Run QaaS Web Front
- For security measures,
  - need to enable HTTPS connection.
  - debug feature is disabled by default.  Developer needs to enable it by updating source code to set debug parameters for various components.
  - to limit the HTTP request body size, can use the maxAllowedContentLength to limit size, or other commands depending on the type of the webservers.
  - User should follow security tips when deploying current webapp to production web servers.
- Also should enable TLS for further safety in data transfer.
- To limit message size, set maxContentLength variable (e.g. to 10000) on React async() call to receive request.
