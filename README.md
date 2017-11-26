# Docker based Website
### Ubuntu - Apache2 - mod_wsgi for Python3.6 - Flask 

This repo is my slow attempt at learning several technologies, including Dockers, web debelopment, and Cassandra. Over time this site will grow and move away from being just a Bitcoin Dashboard to eventually being a blog for the various things I learn. 

I have attempted to seperate the Python code for doing data collection and data analysis from the actual Flask site code. All things related to data analysis will be in the data analysis folder, to include code for getting data from the Cassandra backend. The data collection directory is where the web scrappers are located and any other functions related to getting data into the database. Finally the website folder is where the Flask app is located and it houses all the code related to making the website work. 

As stated before I am also using this repo as an attempt to learn more about Docker and have included the Dockerfile that I am using to house the website. With little editing it will run on either a normal x86 based computer or an ARM based mirco-computer (Rock64 in my case currently). The Docker has some additional bloat to include M$ ODBC drivers and Kerberos for Linux because I am using dervations elsewhere and wanted to keep track of it. The optional things are commented in the Dockerfile. 



The command to run the `Dockerfile` is:

`docker run -d -p 80:80 --name <name> mattcamp.org`

or with a volume:

`docker run -d -p 80:80 -v /path/to/BitCoinDashboard:/var/www/apache-flask/ --name <name> mattcamp.org`


 * Clone the repo and CD into the root directory
 * build the image: `docker build -t mattcamp.org .`


#### The docker file runs through the following steps:  

 - get Ubuntu 16.04
 - apt-get and system utilities
 - install Microsoft ODBC drivers for SQL Server (Optional)
 - copy over Kerberos config files (Optional)
 - install Apache2, Python 3.6, mod_wsgi
 - copy over the `requirements.txt` file and run `pip install` on it. 
    - This is put near the end of the Dockerfile to allow it to be changed and no impact the build much.   
 - expose port 80  
 - point the container to the application directory  
 - the run command. 