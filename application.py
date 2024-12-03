import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set (public key)
API_KEY = os.environ['API_KEY']

# 0 if admin logged in 1 otherwise
admin_logged = False
@app.route("/admins/login",methods=["GET", "POST"])
def admins_login():
    """Admin page that gives control to admins to alter the app"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        query = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Admin not found
        if len(query) != 1 or not check_password_hash(query[0]["hash"], request.form.get("password")) or query[0]["admin"] != 1:
            return apology("invalid username and/or password", 403)

        # Admin is logged in
        global admin_logged
        admin_logged = True
        return redirect("/admins")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("admin_login.html")

@app.route("/admins",methods=["GET", "POST"])
def admins():
    if admin_logged == False:
        return redirect("/admins/login")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("users")
        cash = db.execute("SELECT cash FROM users WHERE username = ?",username)[0]["cash"] + int(request.form.get("amount"))

        # Admin selects adjust balance
        if request.form.get("action") == "adjust_balance":
            db.execute("UPDATE users SET cash = ? WHERE username = ?;",cash,username)

    users = db.execute("SELECT username FROM users;")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("admins.html",users=users)

@app.route("/information")
@login_required
def information():
    """Send user information about the website and how to use it"""
    return render_template("info.html")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Queries database for purchase history
    holdings = db.execute("SELECT symbol,SUM(shares) FROM transactions GROUP by id,symbol HAVING id = :id;",
                          id=session["user_id"])

    # Queries database for user cash balance
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

    # Adds cash and stock to come to come to grand_total
    grand_total = cash

    # Iterate over the holdings
    for stock in holdings:
        symbol = stock["symbol"]
        shares = stock["SUM(shares)"]
        name = lookup(symbol)["name"]
        price = lookup(symbol)["price"]
        stock["name"] = name
        stock["price"] = usd(price)
        stock["total"] = price * shares
        grand_total += stock["total"]

    db.execute("UPDATE users SET grand_total = ? WHERE id = ?;",grand_total,session["user_id"])
    return render_template("index.html", holdings=holdings, cash=usd(cash), grand_total=usd(grand_total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Makes sure symbol is valid
        if lookup(symbol) == None:
            return apology("invalid symbol")

        price = lookup(symbol)["price"]
        name = lookup(symbol)["name"]

        # Queries database to check how much cash the user has
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

        total = float(price) * int(shares)

        # Makes sure user has enough cash to buy the stocks
        if total > cash:
            return apology("insufficient funds")

        # Completes transaction
        cash -= total

        # Updates database with new information
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])

        db.execute(
            "INSERT INTO transactions (id, name, symbol, shares, price, total, date) VALUES (:id, :name, :symbol, :shares, :price, :total, :date)",
            id=session["user_id"], name=name, symbol=symbol, shares=shares, price=price, total=total,
            date=datetime.now())

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    transactions = db.execute("SELECT symbol,shares,date FROM transactions WHERE id = ?;",session["user_id"])
    for transaction in transactions:
        transaction["price"] = lookup(transaction["symbol"])["price"]

    return render_template("history.html", transactions=transactions)

@app.route("/leaderboard")
@login_required
def leaderboard():
    """Shows leaderboard of top users"""
    leaderboard = db.execute("SELECT username,cash,grand_total FROM users ORDER BY grand_total DESC LIMIT 10;")
    for user in leaderboard:
        user["cash"] = user["cash"]
        user["grand_total"] = user["grand_total"]

    return render_template("leaderboard.html",leaderboard=leaderboard)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute("SELECT hash,id FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    global admin_logged

    # Forget any user_id and admin log in
    admin_logged = False
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("quote.html")

    # User reached route via POST (as by submitting a form via POST)

    # Looks up stock information
    retrieve = lookup(request.form.get("symbol"))
    if retrieve == None:
        return apology("invalid symbol")

    # Send data to HTML page to show the stock information to the user
    return render_template("quoted.html", name=retrieve["name"], symbol=retrieve["symbol"], price=retrieve["price"])


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # variables for form submisssions
        name = request.form.get("username")
        hash_pass = generate_password_hash(request.form.get("password"))
        confirmation = request.form.get("confirmation")

        # Checks if user submitted correct password both times
        if not check_password_hash(hash_pass, confirmation):
            return apology("password must match password confirmation", 403)

        # Trys to insert the new user data
        try:
            # Checks if Admin code correct
            user_type = request.form.get("user_type")
            admin = 0  # 0 = false, 1 = true
            if user_type == "admin":
                if request.form.get("admin_code") != os.environ['ADMIN_CODE']:
                    return apology('invalid admin code')
                admin = 1

            db.execute("INSERT INTO users (username, hash, admin) VALUES (:username, :hash, :admin)",
                       username=name, hash=hash_pass, admin=admin)
        # If insert fails it outputs "username has already been taken"
        except:
            return apology("username has already been taken", 403)

        # Redirect user to login page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # User reached route via GET (as by clicking a link or via redirect)
    symbols = []
    symbols_query = db.execute("SELECT DISTINCT(symbol) FROM transactions WHERE id = ?;", session["user_id"])

    # Loops through symbols to list on drop down
    for symbol in symbols_query:
        symbols.append(symbol["symbol"])

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        symbol = request.form.get("symbol")
        sell_shares = int(request.form.get("shares"))
        price = lookup(symbol)["price"]
        total = price * sell_shares
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

        # Amount of shares available to sell
        maximum = db.execute("SELECT SUM(shares) FROM transactions WHERE symbol = ? AND id = ?;",
                             symbol, session["user_id"])[0]["SUM(shares)"]

        # User doesn't have enough shares of symbol to complete the transaction
        if sell_shares > maximum:
            return apology("You do not have enough shares")

        name = lookup(symbol)["name"]

        # Update table
        db.execute(
            "INSERT INTO transactions (id,name,symbol,shares,price,total,date) VALUES (:id,:name,:symbol,:shares,:price,:total,:date);",
            id=session["user_id"], name=name, symbol=symbol, shares=sell_shares * -1, price=price, total=total * -1,
            date=datetime.now())

        # Update cash balance and add it to table
        cash += total
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, session["user_id"])

        # Redirect to index
        return redirect("/")

    # Renders sell.html template
    return render_template("sell.html", symbols=symbols)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run()
