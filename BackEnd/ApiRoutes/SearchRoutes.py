from flask import Blueprint, request, render_template
from Models import User, Repository, RepositoryAccess, db
from UserLoginManager import UserLoginManager

SearchRoutes = Blueprint('SearchRoutes', __name__)

@SearchRoutes.route('/search')
def Search():
    # Search: Search For Users And Repositories
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')  # 'all', 'users', 'repos'

    users = []
    repos = []

    if query:
        if search_type in ['all', 'users']:
            # Search Users By Username Or Email
            users = User.query.filter(
                db.or_(
                    User.Username.ilike(f'%{query}%'),
                    User.Email.ilike(f'%{query}%')
                )
            ).all()

        if search_type in ['all', 'repos']:
            # Search Repositories By Name Or Description
            repos_query = Repository.query.filter(
                db.or_(
                    Repository.Name.ilike(f'%{query}%'),
                    Repository.Description.ilike(f'%{query}%')
                )
            )

            # Only Show Public Repos Or Repos Owned By/Accessed By Current User
            current_user = UserLoginManager.GetCurrentUser()
            if current_user:
                repos_query = repos_query.filter(
                    db.or_(
                        Repository.IsPrivate == False,
                        Repository.OwnerId == current_user.Id,
                        Repository.Id.in_(
                            db.session.query(RepositoryAccess.RepositoryId).filter(
                                RepositoryAccess.UserId == current_user.Id
                            )
                        )
                    )
                )
            else:
                repos_query = repos_query.filter(Repository.IsPrivate == False)

            repos = repos_query.all()

    return render_template('Search.html',
                         query=query,
                         search_type=search_type,
                         users=users,
                         repos=repos)

@SearchRoutes.route('/users')
def BrowseUsers():
    # BrowseUsers: Show All Users
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page

    users = User.query.order_by(User.CreatedAt.desc()).offset(offset).limit(per_page).all()
    total_users = User.query.count()

    return render_template('Users.html',
                         users=users,
                         page=page,
                         per_page=per_page,
                         total_users=total_users)