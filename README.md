# README #

Edward Bottom 448634
Rohit Kumar 448301

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

* Quick summary
* Version
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

[This repository](https://bitbucket.org/cse330/spring2018-cp-group-448634-448301) is for the creative project for CSE 330. No link to the project is provided at the moment, because the server has to be setup on port 5000 of an aws instance inorder for the code to run properly. This can be done by creating virtual environment and then running the microblog.py file as a Flask application. 

### How do I get set up? ###

* Summary of set up
* Configuration
* Dependencies
* Database configuration
* How to run tests
* Deployment instructions

The code is laid on in an intutive and user friendly manner. If the user tries to go to the page without loggin in, then they will be taken to the login screen. From there, they will have the option to either login with their username and password, or register for a new account. Once the user has registered, the user will be able to login. 

The user will then be taken to the home page, where they will see a variety of information about whiskey and a task bar for naviagting the pages of the website. The view our collection tab takes the user to the table of all the whiskys in the collection. The user can click on a link to any of the whiskys reviews to see the user reviews for the whiskeys, like the reviews of the whiskeys, and create and edit their own reviews. The reviews are color coded based on how positive they are, with red being a bas review, yellow being average, and green being a good review. The add to our collection tab takes the user to a form that can add new whiskys to the collection. The return to home tab will take the user back to the home page and the logout button will log the user out. 

Our creative portion had a number of parts to it. The front page has a whisky of the day feature, that randomly chooses a whisky from the database every day and displays the facts about it on the front page of the website. We also added in a sort feature to the table (although the code was taken from the internet and we do not expect points for it and it was approperately cited), it is none the less a feature that was not specified on our rubric. We also gave the ability to let the user create a my whiskys group, that adds specific whiskys to their collection that they can view and edit in a more condensed version of their table. We also implemented the use of user admins to monitor the website. These admins can delete reviews and whiskys from the collection, but can only be made admins by other users. Our cite also has a data visualization feature that allows the suer to visualize the rating and look at statistics of the whiskeys in the collection usind the D3 data visulaization library. 



* Writing tests
* Code review
* Other guidelines

The functionality of this code was tested on both the server side and the client side. Most of the errors that happened with this assignment were largely due to discrpencies between the two or trouble with routes and rerouting. We did have some troubles with getting bootstrap to work, but that was largely due to learning a new technology. Setting up the database and reading in the csv
proved diffcult, but it proved to be minor syntax errors and was solved by using the PyMongo library. We ended up having to use
AJAX to update the table without reloading the page, which we didnt originally plan for, but it since we had already used AJAX for calendar that was relatively painless. 
### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact

If you have any questions or comments about the code, please contact either Edward Bottom, <edward.bottom@wustl.edu> or <rohit.kumar@wustl.edu>. 