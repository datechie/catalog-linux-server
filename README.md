# Udacity FSND Project - Linux Server Configuration

# Amazon Lighsail Instance Details
* Instance setup as per the Get Started on Lightsail section of the Udacity Linux Server Configuration project
* The Public IP is 54.202.167.86
* SSH port has been changed to 2200
* The IP address was converted to a host name using [Host2IP](http://www.hcidata.info/host2ip.cgi).
* Application URL is [http://ec2-54-202-167-86.us-west-2.compute.amazonaws.com/](http://ec2-54-202-167-86.us-west-2.compute.amazonaws.com/)

# Software Updates/Installs on the system
* Check for system updates and upgrade
  - `sudo apt-get update`
  - `sudo apt-get upgrade`
* Install other required software:
  - Apache2 - `sudo apt-get install apache2`
  - wsgi - `sudo apt-get install libapache2-mod-wsgi`
  - Postgresql - `sudo apt-get install postgresql`
  - Python - `sudo apt install python2.7 python-pip`
  - Pip upgrade - `sudo pip install --upgrade pip`
  - Flask - `sudo pip install flask`
  - Requests - `sudo pip install requests`
  - oauth2client - `sudo pip install oauth2client`
  - sqlaclhemy - `sudo pip install sqlalchemy`
  - git - `sudo apt-get install git`
  - psycopg2 - `sudo pip install psycopg2`
  - psycopg2-binary - `sudo pip install pyscopg2-binary`

# Firewall configuration to allow ssh (port 2200), http (port 80) and ntp (port 123)
  - `sudo ufw allow ssh`
  - `sudo ufw allow 2200/tcp`
  - `sudo ufw allow www`
  - `sudo ufw allow ntp`
  - `sudo ufw enable`

# grader account access using ssh key and sudo access
* grader account key included with the submissions.
* sudo access granted via creating an entry for grader under /etc/sudoers.d

# Disable remote login of the root user
* /etc/ssh/sshd_config has this entry to disable remote login for the root user
  `PermitRootLogin No`

# Enforce key-based ssh authentication
* /etc/ssh/sshd_config has password authentication disabled
  `PasswordAuthentication no`

# Is there a web server running on Port 80
* The default Apache service running on port 80 has been disabled and the catalog project is configured to use Port 80

# Configure the catalog app as a WSGI script
* Original catalog project repository cloned as `git clone https://github.com/datechie/catalog.git`
* The modified content to make the project work has been added to this new repository - https://github.com/datechie/catalog-linux-server
* The config file being used at /etc/apache2/sites-enabled/catalog.conf has been added to the new catalog-linux-server repository
* The content modified in project.py is also available in this repository with the changes. The changes are include updating the paths of the client_secrets.json and fb_client_secrets.json and also the DB information.
* The wsgi file - catalog.wsgi (located at /var/www/catalog on the server) file is also available in this repository

# Database configuration
* At the psql prompt, ran the following:
  - `CREATE USER catalog;`
  - `ALTER USER catalog WITH PASSWORD 'catalog';`
  - `CREATE DATABASE catalog WITH OWNER catalog; `
  - `\c catalog`
  - `REVOKE ALL ON SCHEMA public FROM public;`
  - `GRANT ALL ON SCHEMA public TO catalog;`
* In the python code, changed the create_engine references to use `engine = create_engine('postgresql://catalog:catalog@localhost/catalog')`

# OAuth
* Updated the Google authentication to replace `http://localhost:5000` with `http://ec2-54-202-167-86.us-west-2.compute.amazonaws.com`
* For FB, changed the Site URL to `http://ec2-54-202-167-86.us-west-2.compute.amazonaws.com/`

# Final steps
*  Disable the default Apache site - `sudo a2dissite 000-default`
*  Enable our new site - `sudo a2ensite catalog`
*  Reload Apache2 - `sudo service apache2 reload`

# References
* [Flask config](http://flask.pocoo.org/docs/0.12/config/)
* [Flask mod_wsgi](http://flask.pocoo.org/docs/0.12/deploying/mod_wsgi/)
* [Host2IP](http://www.hcidata.info/host2ip.cgi)
* [Abigail Mathews](https://github.com/AbigailMathews/FSND-P5)
* [Harushimo](https://github.com/harushimo/linux-server-configuration)
* [Ghoshabhi](https://github.com/ghoshabhi/P5-Linux-Config)
* [Steve Wooding](https://github.com/SteveWooding/fullstack-nanodegree-linux-server-config)
* [Stueken](https://github.com/stueken/FSND-P5_Linux-Server-Configuration)

