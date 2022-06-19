# ISC344

For Topics in Web Engineering Final.
This repo is for server side script and files for serving to client.

## Result
The final product can be seen here: https://icu-syllabus.com
This is hosted in my home server and is proxyed through cloudflare.

## Files
The `devpython.py` file is for searching the course offerings, and the `devpython-sub.py` is used for searching the syllabus. For each of the scripts, when accessed by a browser, it will return a json object containing the results, along with basic html(was a bit short in time so had to hardcode it in in python). The index.js file will send a GET request to that url and upon reciving the json, will display the objects as html elements.

## INSTALL

The enviroment used was
- ubuntu 22.04 LTS
- Apache/2.4.52
- Python 3.10.4

copy this repo to /var/www/html

Install Apache2 along with Apache2-dev(needed for mod_wsgi) and enable/start apache.
```
    sudo apt-get install apache2 apache2-dev
    sudo systemctl enable apache2
    sudo systemctl start apache2
```

Next, install and setup mod_wsgi to run python scripts on apache.
In the official mod_wsgi docs, building from source is recommended but that results in using python2.7 so use pip3 instead.
```
    sudo pip3 install mod_wsgi
```

We'd like to install it on to apache by a2enmod but the package can't be seen from a2enmod yet.

Find where pip3 installed the package and inside that mod_wsgi folder, under server folder, there will be `mod_wsgi-py~~.so`. Move that file to `/usr/lib/apache2/modules/`.

To load the module to apache, `sudo nano /etc/apache2/mods-available/wsgi.load` and inside, write 
```
    LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi-py310.cpython-310-x86_64-linux-gnu.so
```
Now a2enmod should recognise mod_wsgi, so `sudo a2enmod wsgi`. Then restart apache2 by `sudo systemctl restart apache2`.


Next, setup apache config file to run wsgi. apache config files has changed names but at the time of writing, it was `/etc/apache2/apache2.conf`. 

As we are in the config file we might as well find the section marked below and delete the text Indexes(for security reasons?)
```
<Directory /var/www/>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted
</Directory>
```

After that, we'll add the pass of the wsgi script that will be executed when the url is accessed. Inside the config file, add the following:
```
    WSGIScriptAlias /wsgi /var/www/html/wsgi-test.py
```
This is `WSGIScriptAlias` followed by the url path and then the path to the corresponding wsgi script file. 
For testing the setup we'll write a simple hello world script from the official docs. 
`sudo touch /var/www/html/wsgi-test.py` and then copy in the following
```
def application(environ, start_response):
    status = '200 OK'
    output = 'Hello World!\n'
    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]
```
Save the file and then restart apache2. After restarting, run `curl localhost/wsgi` and it should output `Hello World!`.
As for the setup for mod_wsgi, this should be all!

## Setup for running devpython.py and devpython-sub.py

As we want to run the script `devpython.py` and `devpython-sub.py` so we will need to add some more configs.

In `apache.conf`, add the following
```
    WSGIScriptAlias /devpython /var/www/html/devpython.py
    WSGIScriptAlias /devpython-sub /var/www/html/devpython-sub.py
```
This will enable running of the two scripts but likely accessing the url at this point will resut in a `500 internal server config error`. This is because of the missing python packages needed to run this script.

The packeges needed for serverside are:
- dns-python
- pymongo
- certifi
make shure that these are installed and can be accessed from the script.

You will need to modify soma parts of the script such as the cors headders and mongo db access strings and such.
For Cross Origin Resource Shareing, change the `originSite` to the hostname of the server sending the files / or allow all by setting `'*'` for testing.
```
    originSite = 'example.com' # or '*'
    headers = [('Content-Type', 'application/json; charset=utf-8'),('Access-Control-Allow-Origin',originSite)]
```
**Also, the mongodb access token has been left in but as the access will be limited by ip addresses, you might need to setup your own mongodb atlas instance and make the database using the syllabusscrape scripts.**

These packeges should be all but as there is no db access yet, this still will probablly result in 500 error status, see `/var/log/apache2/error.log` for details.
