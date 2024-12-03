![Image of stock portfolio](/static/finance.jpg)

# Finance
Finance is a web project created as an assignment for week 9 of Harvard CS50 by Rohan Muppa on the week of July 3rd 2021 (7/3/21) to July 15th 2021 (7/15/21). The application was made using Python, HTML (w/ Jinja), CSS, and Javascript using the Flask web framework. It uses the IEX API to get the stock prices in real time and a SQL database to store user and transaction information.

Once you register and log yourself in there will be 5 main sections:

* **Portfolio** is the default route that is opened up once you log in. Portfolio will present to you all the stocks you own along with some details about it. Portfolio also provides you with your current cash balance, and your combined net worth.
* **Quote** allows you to enter a stock ticker then fetches you the current price of it using the IEX API.
* **Buy** allows you to purchase your desired stocks. Enter the stock ticker and the amount of shares you want to buy then the transaction will proceed and your information will be updated to the SQL database. An error will occur if you cannot afford that many shares or if you enter an invalid stock ticker.
* **Sell** allows you to sell shares of any stock you own. Select the stock then enter the number of shares you would like to sell. An error will occur if you choose to sell more shares than you currently own.
* **History** will present all the previous transactions you've made. The ticker symbol; number of shares; purchase price; total amount, in US dollars, spent during that
transaction; and the time of transaction in UTC (Coordinated Universal Time) will all be displayed to you on the screen.
# Extras
* **Log out** clears all your cookies effectively logging you out, prompting you to log in (or register) again.
* **Information** opens a page giving you more information about the website and it's functionality.
* **Leaderboard** displays to you the top 10 users, emphasizing the top 3, in terms of total earnings.
* **Admins** is a page open to admins, which you can register as using a valid admin code, that gives the admin options to alter and test user accounts, as you can log in as an admin and member at the same time using separate accounts.
# Usage
Finance can be accessed and ran either **locally**, on your own computer, or **online**, hosted by a web server.
### Online
1. To access the application online open `https://rohan-finance.herokuapp.com` in a new browser tab.
    * Sometimes the heroku app has glitches and bugs, so if that happens message me and I'll open up a Flask server. (If you want, you can do it yourself via the instructions below)
### Locally
1. First, running the application locally requires you to change directory or `cd` into your desired directory using the terminal then clone this repository with `git clone https://github.com/RohanMuppa/Finance.git` to download the repository locally.
1. After that install Python using the [Python documentation](https://docs.python.org/3/using/index.html) as an installation guide.
1. Finally, read the [Flask documentation](https://flask.palletsprojects.com/en/2.0.x/installation/#) to install and run Flask, optionally, learning how it works.

## Video Demo
Video Demo: https://youtu.be/lauKRc3qlD4
