# FleetRiskReports
Tools to pull Risk Report data from a Geotab instance and email notifications to drivers
## Installation
This app was developed for use on a Raspberry Pi.  Here's what you need to do to get started:
1. Install Raspberry Pi OS on your Pi using the Raspberry Pi Imager
2. Download the following additional packages:
   - ksh (my favorite shell!)
   - expect (needed to control alpine)
3. Download, build, and install the alpine email client.  You can find that at [https://alpineapp.email](https://alpineapp.email/).  Make sure you select a version that supports OAUTH2.
4. Download the files from this repository under ~pi (or whatever user your prefer):
```
mkdir bin etc tmp
mv *.sh *.py ~/bin
mv *.conf *.txt ~/etc
```
Configuring alpine can be a little tricky, especially for OAUTH2 email servers, but there are step-by-step instructions for doing this on the alpine site.  Also, before entering your email credentials you'll want to create a private key that alpine will use to encrypt the OAUTH tokens.  The key is stored in an X509 certificate file located in ~/.alpine-smime/.pwd.  Here's the command to generate your key files:
```
openssl req -nodes -new -x509 -keyout private.key -out private.crt
```
Also, don't forget to set the "customized-hdrs" field in .pinerc to: From:account@provider.com, where account@provider.com is the email account from which you'll be sending out reports & notifications.  Similarly, set "user-domain" to: provider.com.
## Configuration
After the software is installed on the Pi, edit risopts.conf to supply your own settings, and customize the text in risnotice.txt as desired. Lastly, create a crontab entry to schedule the execution of risfleet.sh according to your needs.
