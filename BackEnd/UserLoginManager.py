import bcrypt
import functools
from flask import session
from Models import db, User

class UserLoginManager:
    @staticmethod
    def HashPassword(Password):
        # HashPassword: Hash A Password Using Bcrypt
        return bcrypt.hashpw(Password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def VerifyPassword(Password, HashedPassword):
        # VerifyPassword: Verify A Password Against Its Hash
        return bcrypt.checkpw(Password.encode('utf-8'), HashedPassword.encode('utf-8'))

    @staticmethod
    def CreateUser(Username, Password, Email):
        # CreateUser: Create A New User Account
        if User.query.filter_by(Username=Username).first() or User.query.filter_by(Email=Email).first():
            return None  # User Already Exists

        HashedPassword = UserLoginManager.HashPassword(Password)
        NewUser = User(Username=Username, PasswordHash=HashedPassword, Email=Email)
        db.session.add(NewUser)
        db.session.commit()
        return NewUser

    @staticmethod
    def AuthenticateUser(Username, Password):
        # AuthenticateUser: Authenticate A User With Username And Password
        UserObj = User.query.filter_by(Username=Username).first()
        if UserObj and UserLoginManager.VerifyPassword(Password, UserObj.PasswordHash):
            return UserObj
        return None

    @staticmethod
    def LoginUser(UserObj):
        # LoginUser: Log In A User By Setting Session
        session['UserId'] = UserObj.Id
        session['Username'] = UserObj.Username

    @staticmethod
    def LogoutUser():
        # LogoutUser: Log Out A User By Clearing Session
        session.pop('UserId', None)
        session.pop('Username', None)

    @staticmethod
    def GetCurrentUser():
        # GetCurrentUser: Get The Currently Logged In User
        UserId = session.get('UserId')
        if UserId:
            return User.query.get(UserId)
        return None

    @staticmethod
    def IsLoggedIn():
        # IsLoggedIn: Check If A User Is Currently Logged In
        return 'UserId' in session

    @staticmethod
    def RequireLogin():
        # RequireLogin: Decorator To Require Login For Routes
        def Decorator(Func):
            @functools.wraps(Func)
            def Wrapper(*args, **kwargs):
                if not UserLoginManager.IsLoggedIn() or not UserLoginManager.GetCurrentUser():
                    from flask import redirect, url_for
                    return redirect(url_for('AuthRoutes.Login'))
                return Func(*args, **kwargs)
            return Wrapper
        return Decorator
