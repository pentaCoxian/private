# ISC344

For Topics in Web Engineering Final.
This repo is for server side script and files for serving to client.
The enviroment used was
- ubuntu 22.04 LTS
- Apache/2.4.52
- Python 3.10.4

## INSTALL

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

To load the module to apache, `sudo nano /etc/apache2/mods-available/wsgi.load` and inside, write `LoadModule wsgi_module /usr/lib/apache2/modules/mod_wsgi-py310.cpython-310-x86_64-linux-gnu.so`. Now a2enmod should recognise mod_wsgi, so `sudo a2enmod wsgi`. Then restart apache2 by `sudo systemctl restart apache2`.

Next, setup apache config file to run wsgi. apache config files has changed names but at the time of writing, it was `/etc/apache2/apache2.conf`.
