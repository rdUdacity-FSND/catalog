

# Item Catalog App Project - Udacity Full Stack Nanodegree

## Author - Ron Duran

## Project Description

### This application was created to fulfill the requirements of Udacity's Full Stack Nanodegree.  

### The goal of the project is to create a web application that presents category and item data from a database.  

### Items can be added to the database only by users who are logged into the application.  Additionally, items can be edited and deleted only by the user who originally added the item.  The application also provides a JSON API endpoint for obtaining catalog data. 

### The full description and example screenshots for this project are located at:
 https://docs.google.com/document/d/1jFjlq_f-hJoAZP8dYuo5H3xY62kGyziQmiv9EPIA7tM/pub?embedded=true


## Project Environment and Prerequisites
 
### Although it is not required, a Vagrant VM was used for development and the Vagrant file is included in the project.  The VM OS is Ubuntu 16.04.2 LTS (GNU/Linux 4.4.0-75-generic i686)

### If you wish to use this envionment for the application, you will need both Vagrant and VirtualBox on your system.  Instructions for working with Vagrant VM's can be found here:

https://www.vagrantup.com/intro/getting-started/

### The application uses Google's OAuth2.0 to allow the user to log in using a Google account.  You will need to create and configure the OAuth credentials for the application:

Set up Google OAuth credentials by following the instructions at:  https://support.google.com/cloud/answer/6158849 

You will need to use the following information when setting up the account:

Name: Catalog App

JavaScript Origin: http://localhost:8000
  
Redirect URI: http://localhost:8000/gconnect


After you create the Google OAuth credentials for the application, you will be able to download OAuth JSON credentials file.  The filename that is downloaded will start with "client_secrets" and end with ".json".  Rename this file to "g_auth.json" and place it in the same directory as your application.py file.

The application reads the credentials from this file so no changes need to be made to any of the .py or .html files.

## The project was created using:

    Python 2
    Flask
    Google OAuth2
    Google+ JavaScript API
    SQLite
    SQLAlchemy
    Bootstrap
    HTML/CSS/JavaScript
    JQuery
    
#
# Running the application

## You should have the following directory structure and files:

        YOUR PROJECT DIRECTORY
        |
        README.md
        requirements.txt
        application.py
        cat_app_data.db  (build this as described in this readme)
        models.py
        init_database.py
        g_auth.json  (created by follwing the OAuth instructions in this readme)
        |
        static
             |
             styles.css
        templates
             |
             addItem.html
             base.html
             categories.html
             category_panel.html
             content_panel.html
             deleteItem.html
             editItem.html
             header.html
             itemDescription.html
             login.html
             main.html

## Navigate to the directory where the application.py file is located.

## Make sure you have the necessary modules installed.  You can view the included requirements.txt file.  If you do not have all the modules/libraries installed, they can be installed in one step by running the following command:

        pip install -r requirements.txt


    
## The application uses an SQLite3 database file named "cat_app_data.db" you can build the database by running the following commands:

        python models.py
        python init_database.py

## Make sure you place the cat_app_data.db in the same directory as the application.py file - See the file structure in this readme.

 - Ron Duran - Udacity Full Stack Nanodegree - Catalog App Project June 2017    
#

