from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy_utils import database_exists, create_database
import colorama
from colorama import Fore, Style, Back

colorama.init(autoreset=True)
db = SQLAlchemy()
DB_NAME = "rfid.db"

def create_app(host, port, secret_key, mysql_user, mysql_password, mysql_host, mysql_port, mysql_db_name):
    print("Server IP: " + Fore.MAGENTA + host)
    print("Server Port: " + Fore.MAGENTA + port)
    print("Secret Key: " + Fore.MAGENTA + secret_key)
    print("MySQL User: " + Fore.MAGENTA + mysql_user)
    print("MySQL Password: " + Fore.MAGENTA + mysql_password)
    print("MySQL Host: " + Fore.MAGENTA + mysql_host)
    print("MySQL Port: " + Fore.MAGENTA + mysql_port)
    print("MySQL Database Name: " + Fore.MAGENTA + mysql_db_name)
    print(" ")

    app = Flask(__name__)
    app.secret_key = secret_key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' + mysql_user + ':' + mysql_password + '@' + mysql_host + ':' + mysql_port + '/' + mysql_db_name
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, urlprefix='/')
    app.register_blueprint(auth, urlprefix='/')


    from .models import Credentials, Bookings, Notifications, Rooms

    print("Connecting to Database... [" + Fore.YELLOW + "?" + Fore.RESET + "]")
        #db.session.query("1").from_statement("SELECT 1").all()
    try:
        database_exists(app.config['SQLALCHEMY_DATABASE_URI'])
        print("Connected [" + Fore.GREEN + "OK" + Fore.RESET + "]")
        print("Checking Database..." + Fore.YELLOW + "[?]")
        if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
            print("Database Does NOT Exists!" + Fore.RED + "[ERROR]")
            print("Creating New Database (" + Fore.CYAN + "RFID" + Fore.RESET + ") ...")
            create_database(app.config['SQLALCHEMY_DATABASE_URI'])
            print("Created Database (" + Fore.CYAN + "RFID" + Fore.RESET + ") " + Fore.GREEN + "[OK]")
        else:
            print("Database (" + Fore.CYAN + "RFID" + Fore.RESET + ") " + Fore.GREEN + "[OK]")

        print("Checking Tables..." + Fore.YELLOW + "[?]")
        with app.app_context():
            print("Making Sure all Tables are existing...")
            print("Done")
            print(" ")
            db.create_all()

            print("Checking User Admin Account...")
            from .auth import generate_password_hash
            user_admin_exists = Credentials.query.filter_by(username="admin").first()
            if not user_admin_exists:
                new_user_admin = Credentials(username='admin', name='admin', email='admin@admin.com', priv='admin',
                                      password=generate_password_hash('admin', method='SHA256'))
                db.session.add(new_user_admin)
                db.session.commit()
                print("Creating Default Admin Account...")
                print("username: " + Fore.MAGENTA + "admin")
                print("password: " + Fore.MAGENTA + "admin")
                print(Fore.YELLOW + "Make sure you change the admin password for security reasons.")
            else:
                print("User Admin Account " + Fore.GREEN + "[OK]")
            print(" ")
            print("Starting Server...")
            print(" ")
    except:
        print("Unable to connect, is the MysQL server running? [" + Fore.RED + "ERROR" + Fore.RESET + "]")
        print(Fore.YELLOW + "Make sure your configurations are correct.")
        exit()




    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Credentials.query.get(id)

    return app

