from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "supersecretkey"  # For admin authentication

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolios.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --------------------
# Database Model
# --------------------
class UserPortfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100))
    skills = db.Column(db.String(500))  # Comma-separated skills
    experience = db.Column(db.Integer)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(50))

    def __repr__(self):
        return f'<Portfolio {self.name}>'

# --------------------
# Routes
# --------------------

# Home / Portfolio Form
@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        company = request.form.get("company")
        skills = request.form.get("skills")
        experience = request.form.get("experience")
        email = request.form.get("email")
        phone = request.form.get("phone")

        # Save portfolio to database
        portfolio = UserPortfolio(
            name=name,
            company=company,
            skills=skills,
            experience=int(experience),
            email=email,
            phone=phone
        )
        db.session.add(portfolio)
        db.session.commit()

        # Redirect to the generated portfolio
        return redirect(url_for('portfolio', portfolio_id=portfolio.id))
    return render_template("form.html")

# Display Portfolio
@app.route("/portfolio/<int:portfolio_id>")
def portfolio(portfolio_id):
    user = UserPortfolio.query.get_or_404(portfolio_id)
    skills = [s.strip() for s in user.skills.split(",")]
    return render_template("portfolio.html", user=user, skills=skills)

# Admin Login
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "admin" and password == "admin123":
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template("admin_login.html", error="Invalid credentials")
    return render_template("admin_login.html")

# Admin Dashboard
@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    portfolios = UserPortfolio.query.all()
    return render_template("admin_dashboard.html", portfolios=portfolios)

# Admin Logout
@app.route("/admin/logout")
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

# --------------------
# Run App
# --------------------
if __name__ == "__main__":
    # Create database tables inside app context
    with app.app_context():
        db.create_all()
    app.run(debug=True)
