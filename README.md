<strong>Aboout</strong>
<hr>
Hi! My name is Hennadii and this is my microblogging web application written in Python and Flask.
Currently the <a href="http://159.203.164.211/">application</a> had been deployed on Digital Ocean remote server running with Nginx as reverse proxy, Gunicorn wsgi-server and Redis.
<br>
<br>
<strong>Installation</strong>
<hr>
You need python 3.5, nginx, redis and virtual environment.<br>
<br>
1. install python and redis packages<br>
2. create your virtual environment<br>
3. install all the required modules from my requirements.txt<br>
4. as whooshalchemy extension has some compability issues with python 3 you need to uninstall it using
<code>(yourvenv) $ pip uninstall flask-whooshalchemy</code> and install this fork: 
<code>(yourvenv) $ pip install git+git://github.com/miguelgrinberg/flask-whooshalchemy.git</code>
<br>
<br>
<em>to start the app USING NGINX AND GUNICORN</em><br>
5. install nginx package<br>
6. set up environment variables: SECRET_KEY, SALT_EMAIL_KEY, SALT_RECOVERY_KEY and MAIL_USERNAME, MAIL_PASSWORD (your mail login credentials). In most cases you need to set up enironment variables in gunicorn files (there are plenty ways to do that). For security reasons i can't tell where are mine.<br>
7. configure nginx, gunicorn and redis depending on your OS or Remote(Cloud) Server.
<br>
<br>
<em>to start the app WITHOUT NGINX AND GUNICORN</em><br>
5. it's enough to set up environment variables in your <code>"yourvenv/bin/activate"</code> file.<br>
6. (in most cases there is no need to configure redis)
<br>
<br>
<strong>Running</strong>
<hr>
First create sqlite database using <code>(yourvenv) $ python db_create.py</code> command from your virtual environment.<br>
You can run the app using <code>(yourvenv) $ python wsgi.py</code> (without gunicorn and nginx).<br> 
The way to run the app with Nginx and Gunicorn depends on your system configuration.