from flask import Flask
from flask_session import Session
from Config import Config
from Models import db
from ApiRoutes.AuthRoutes import AuthRoutes
from ApiRoutes.RepoRoutes import RepoRoutes
from ApiRoutes.BranchRoutes import BranchRoutes
from ApiRoutes.SearchRoutes import SearchRoutes
import os

def CreateApp(ConfigClass=Config):
    # CreateApp: Create And Configure The Flask Application
    # Get The Absolute Path To The Project Root
    ProjectRoot = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TemplateDir = os.path.join(ProjectRoot, 'FrontEnd', 'Templates')
    StaticDir = os.path.join(ProjectRoot, 'FrontEnd', 'Static')

    App = Flask(__name__,
                template_folder=TemplateDir,
                static_folder=StaticDir,
                static_url_path='/Static')
    App.config.from_object(ConfigClass)

    # Initialize Database
    db.init_app(App)

    # Initialize Session
    Session(App)

    # Register Blueprints
    App.register_blueprint(AuthRoutes)
    App.register_blueprint(RepoRoutes)
    App.register_blueprint(BranchRoutes)
    App.register_blueprint(SearchRoutes)

    # Create Necessary Directories
    os.makedirs(App.config['REPOSITORIES_PATH'], exist_ok=True)
    os.makedirs(App.config['UPLOAD_FOLDER'], exist_ok=True)

    # Context Processor For Templates
    @App.context_processor
    def InjectUser():
        from UserLoginManager import UserLoginManager
        return {'CurrentUser': UserLoginManager.GetCurrentUser()}

    return App

if __name__ == '__main__':
    App = CreateApp()
    with App.app_context():
        # Create Database Tables
        try:
            db.create_all()
            print("✓ Database Tables Created Successfully")
        except Exception as e:
            print(f"⚠ Database Setup Warning: {e}")
            print("Note: Using SQLite Database. Run Setup_DB.py If You Encounter Issues.")

    print("Starting DevBhoomi Server...")
    print("Access at: http://localhost:5000")
    App.run(debug=True, host='0.0.0.0', port=5000)
