from flask import Blueprint, request, jsonify, redirect, url_for, render_template, flash
from UserLoginManager import UserLoginManager
from Models import User, Repository, db

AuthRoutes = Blueprint('AuthRoutes', __name__)

@AuthRoutes.route('/login', methods=['GET', 'POST'])
def Login():
    # Login: Handle User Login
    if request.method == 'POST':
        Username = request.form.get('Username')
        Password = request.form.get('Password')

        UserObj = UserLoginManager.AuthenticateUser(Username, Password)
        if UserObj:
            UserLoginManager.LoginUser(UserObj)
            return redirect(url_for('RepoRoutes.Dashboard'))
        else:
            flash('Invalid Username or Password', 'error')

    return render_template('Login.html')

@AuthRoutes.route('/logout')
def Logout():
    # Logout: Handle User Logout
    UserLoginManager.LogoutUser()
    return redirect(url_for('AuthRoutes.Login'))

@AuthRoutes.route('/register', methods=['GET', 'POST'])
def Register():
    # Register: Handle User Registration
    if request.method == 'POST':
        Username = request.form.get('Username')
        Password = request.form.get('Password')
        Email = request.form.get('Email')

        if UserLoginManager.CreateUser(Username, Password, Email):
            flash('Account Created Successfully. Please Log In.', 'success')
            return redirect(url_for('AuthRoutes.Login'))
        else:
            flash('Username Or Email Already Exists', 'error')

    return render_template('Register.html')

@AuthRoutes.route('/api/login', methods=['POST'])
def ApiLogin():
    # ApiLogin: API Endpoint For Login
    data = request.get_json()
    Username = data.get('Username')
    Password = data.get('Password')

    UserObj = UserLoginManager.AuthenticateUser(Username, Password)
    if UserObj:
        UserLoginManager.LoginUser(UserObj)
        return jsonify({'success': True, 'user': {'id': UserObj.Id, 'username': UserObj.Username}})
    else:
        return jsonify({'success': False, 'message': 'Invalid Credentials'}), 401

@AuthRoutes.route('/api/logout', methods=['POST'])
def ApiLogout():
    # ApiLogout: API Endpoint For Logout
    UserLoginManager.LogoutUser()
    return jsonify({'success': True})

@AuthRoutes.route('/api/current-user')
def ApiCurrentUser():
    # ApiCurrentUser: Get Current User Info
    UserObj = UserLoginManager.GetCurrentUser()
    if UserObj:
        return jsonify({'id': UserObj.Id, 'username': UserObj.Username, 'email': UserObj.Email})
    else:
        return jsonify({'error': 'Not Logged In'}), 401

@AuthRoutes.route('/user/<username>')
def UserProfile(username):
    # UserProfile: View User Profile And Their Public Repositories
    user = User.query.filter_by(Username=username).first()
    if not user:
        flash('User Not Found', 'error')
        return redirect(url_for('RepoRoutes.Dashboard'))

    # Get Public Repositories Or Repositories Accessible By Current User
    current_user = UserLoginManager.GetCurrentUser()
    if current_user and current_user.Id == user.Id:
        # User Viewing Their Own Profile - Show All Repos
        repos = Repository.query.filter_by(OwnerId=user.Id).all()
    else:
        # Other User Viewing Profile - Show Only Public Repos
        repos = Repository.query.filter_by(OwnerId=user.Id, IsPrivate=False).all()

    return render_template('Profile.html', profile_user=user, repositories=repos)

@AuthRoutes.route('/user/<username>/update', methods=['POST'])
@UserLoginManager.RequireLogin()
def UpdateProfile(username):
    # UpdateProfile: Update User Profile Information
    current_user = UserLoginManager.GetCurrentUser()
    if not current_user or current_user.Username != username:
        flash('Unauthorized', 'error')
        return redirect(url_for('RepoRoutes.Dashboard'))

    email = request.form.get('email')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    # Verify Current Password
    if not UserLoginManager.AuthenticateUser(current_user.Username, current_password):
        flash('Current Password Is Incorrect', 'error')
        return redirect(url_for('AuthRoutes.UserProfile', username=username))

    # Update Email If Changed
    if email != current_user.Email:
        # Check If Email Is Already Taken
        existing_user = User.query.filter_by(Email=email).first()
        if existing_user and existing_user.Id != current_user.Id:
            flash('Email Is Already In Use', 'error')
            return redirect(url_for('AuthRoutes.UserProfile', username=username))
        current_user.Email = email

    # Update Password If Provided
    if new_password:
        current_user.PasswordHash = UserLoginManager.HashPassword(new_password)

    # Save Changes
    db.session.commit()

    flash('Profile Updated Successfully', 'success')
    return redirect(url_for('AuthRoutes.UserProfile', username=username))
