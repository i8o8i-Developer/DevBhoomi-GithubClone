from flask import Blueprint, request, jsonify, redirect, url_for, render_template, flash, current_app
from UserLoginManager import UserLoginManager
from RepoManager import DevBhoomiRepoManager
from Models import Branch
from GitHooks import GitHooks

RepoRoutes = Blueprint('RepoRoutes', __name__)

@RepoRoutes.route('/')
def Dashboard():
    # Dashboard: Show User's Repositories Or Redirect To Login
    CurrentUser = UserLoginManager.GetCurrentUser()
    if not CurrentUser:
        return redirect(url_for('AuthRoutes.Login'))
    Repositories = DevBhoomiRepoManager.ListUserRepositories(CurrentUser.Id)
    return render_template('Dashboard.html', Repositories=Repositories)

@RepoRoutes.route('/repo/create', methods=['GET', 'POST'])
@UserLoginManager.RequireLogin()
def CreateRepository():
    # CreateRepository: Create A New Repository
    if request.method == 'POST':
        Name = request.form.get('Name')
        Description = request.form.get('Description')
        IsPrivate = request.form.get('IsPrivate') == 'on'

        CurrentUser = UserLoginManager.GetCurrentUser()
        if not CurrentUser:
            return redirect(url_for('AuthRoutes.Login'))
        NewRepo = DevBhoomiRepoManager.CreateRepository(Name, Description, CurrentUser.Id, IsPrivate)
        if NewRepo:
            GitHooks.SetupHooks(NewRepo.Id)  # Setup Git Hooks
            flash('Repository Created Successfully', 'success')
            return redirect(url_for('RepoRoutes.ViewRepository', RepoName=NewRepo.Name))
        else:
            flash('Repository Name Already Exists', 'error')

    return render_template('CreateRepository.html')

@RepoRoutes.route('/repo/<RepoName>')
@RepoRoutes.route('/repo/<RepoName>/tree/<BranchName>')
@UserLoginManager.RequireLogin()
def ViewRepository(RepoName, BranchName=None):
    # ViewRepository: View Repository Details
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj:
        flash('Repository Not Found Or Access Denied', 'error')
        return redirect(url_for('RepoRoutes.Dashboard'))

    # Default To Main Branch If No Branch Specified
    if not BranchName:
        MainBranch = Branch.query.filter_by(RepositoryId=RepoObj.Id, Name='main').first()
        BranchName = MainBranch.Name if MainBranch else 'main'

    Branches = DevBhoomiRepoManager.GetBranches(RepoObj.Id)
    Commits = DevBhoomiRepoManager.GetCommitHistory(RepoObj.Id, BranchName, Limit=20)
    Readme = DevBhoomiRepoManager.GetReadmeContent(RepoObj.Id, BranchName)
    License = DevBhoomiRepoManager.GetLicenseContent(RepoObj.Id, BranchName)
    Stats = DevBhoomiRepoManager.GetRepositoryStats(RepoObj.Id, BranchName)
    return render_template('RepoView.html', Repository=RepoObj, Branches=Branches, Commits=Commits, Readme=Readme, License=License, Stats=Stats, CurrentBranch=BranchName)

@RepoRoutes.route('/repo/<RepoName>/branches')
@UserLoginManager.RequireLogin()
def ViewBranches(RepoName):
    # ViewBranches: View All Branches For A Repository
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj:
        flash('Repository Not Found Or Access Denied', 'error')
        return redirect(url_for('RepoRoutes.Dashboard'))

    Branches = DevBhoomiRepoManager.GetBranches(RepoObj.Id)
    return render_template('Branches.html', Repository=RepoObj, Branches=Branches)

@RepoRoutes.route('/repo/<RepoName>/commits')
@RepoRoutes.route('/repo/<RepoName>/commits/<BranchName>')
@UserLoginManager.RequireLogin()
def ViewCommits(RepoName, BranchName=None):
    # ViewCommits: View Commit History For A Repository
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj:
        flash('Repository Not Found Or Access Denied', 'error')
        return redirect(url_for('RepoRoutes.Dashboard'))

    # Use URL Parameter First, Then Query Parameter
    if not BranchName:
        BranchName = request.args.get('branch')

    # Default To Main Branch If No Branch Specified
    if not BranchName:
        MainBranch = Branch.query.filter_by(RepositoryId=RepoObj.Id, Name='main').first()
        BranchName = MainBranch.Name if MainBranch else 'main'

    Commits = DevBhoomiRepoManager.GetCommitHistory(RepoObj.Id, BranchName)
    return render_template('CommitHistoryViewer.html', Repository=RepoObj, Commits=Commits, Branch=BranchName)

@RepoRoutes.route('/repo/<RepoName>/settings', methods=['GET', 'POST'])
@UserLoginManager.RequireLogin()
def RepositorySettings(RepoName):
    # RepositorySettings: Manage Repository Settings
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj or RepoObj.OwnerId != CurrentUser.Id:
        flash('Repository Not Found Or Access Denied', 'error')
        return redirect(url_for('RepoRoutes.Dashboard'))

    if request.method == 'POST':
        Name = request.form.get('Name')
        Description = request.form.get('Description')
        IsPrivate = request.form.get('IsPrivate') == 'on'

        # Check If This Is A Delete Request
        if request.form.get('action') == 'delete':
            confirm_name = request.form.get('confirm_name')
            if confirm_name == RepoObj.Name:
                if DevBhoomiRepoManager.DeleteRepository(RepoObj.Id, CurrentUser.Id):
                    flash('Repository Deleted Successfully', 'success')
                    return redirect(url_for('RepoRoutes.Dashboard'))
                else:
                    flash('Failed To Delete Repository', 'error')
            else:
                flash('Repository Name Confirmation Does Not Match', 'error')
        else:
            DevBhoomiRepoManager.UpdateRepository(RepoObj.Id, CurrentUser.Id, Name, Description, IsPrivate)
            flash('Repository Updated Successfully', 'success')
            return redirect(url_for('RepoRoutes.RepositorySettings', RepoName=RepoObj.Name))

    return render_template('RepositorySettings.html', Repository=RepoObj)

@RepoRoutes.route('/repo/<RepoName>/blob/<path:FilePath>')
@UserLoginManager.RequireLogin()
def ViewFile(RepoName, FilePath):
    # ViewFile: View The Content Of A Specific File
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj:
        flash('Repository Not Found Or Access Denied', 'error')
        return redirect(url_for('RepoRoutes.Dashboard'))

    FileContent = DevBhoomiRepoManager.GetFileContent(RepoObj.Id, FilePath)
    if FileContent is None:
        flash('File Not Found', 'error')
        return redirect(url_for('RepoRoutes.ViewCode', RepoName=RepoName))

    # Create Breadcrumb Navigation
    Breadcrumbs = [{'name': RepoName, 'path': ''}]
    path_parts = FilePath.split('/')
    current_path = ''
    for part in path_parts[:-1]:  # Exclude The Filename
        if part:
            current_path += part + '/'
            Breadcrumbs.append({'name': part, 'path': current_path})

    Breadcrumbs.append({'name': path_parts[-1], 'path': FilePath})

    return render_template('FileView.html',
                         Repository=RepoObj,
                         FilePath=FilePath,
                         FileName=path_parts[-1],
                         FileContent=FileContent,
                         Breadcrumbs=Breadcrumbs)

@RepoRoutes.route('/repo/<RepoName>/edit/<path:FilePath>', methods=['GET', 'POST'])
@UserLoginManager.RequireLogin()
def EditFile(RepoName, FilePath):
    # EditFile: Edit A File In The Repository
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj:
        flash('Repository Not Found Or Access Denied', 'error')
        return redirect(url_for('RepoRoutes.Dashboard'))

    if RepoObj.OwnerId != CurrentUser.Id:
        flash('You Do Not Have Permission To Edit Files In This Repository', 'error')
        return redirect(url_for('RepoRoutes.ViewFile', RepoName=RepoName, FilePath=FilePath))

    if request.method == 'POST':
        content = request.form.get('content', '')
        commit_message = request.form.get('commit_message', f'Update {FilePath}')

        success = DevBhoomiRepoManager.UpdateFileInRepository(RepoObj.Id, FilePath, content, commit_message, CurrentUser.Id)
        if success:
            flash(f'File "{FilePath}" Updated Successfully', 'success')
            return redirect(url_for('RepoRoutes.ViewFile', RepoName=RepoName, FilePath=FilePath))
        else:
            flash('Failed To Update File', 'error')

    FileContent = DevBhoomiRepoManager.GetFileContent(RepoObj.Id, FilePath)
    if FileContent is None:
        flash('File Not Found', 'error')
        return redirect(url_for('RepoRoutes.ViewCode', RepoName=RepoName))

    # Create Breadcrumb Navigation
    Breadcrumbs = [{'name': RepoName, 'path': ''}]
    path_parts = FilePath.split('/')
    current_path = ''
    for part in path_parts[:-1]:  # Exclude The Filename
        if part:
            current_path += part + '/'
            Breadcrumbs.append({'name': part, 'path': current_path})

    Breadcrumbs.append({'name': path_parts[-1], 'path': FilePath})

    return render_template('EditFile.html',
                         Repository=RepoObj,
                         FilePath=FilePath,
                         FileName=path_parts[-1],
                         FileContent=FileContent,
                         Breadcrumbs=Breadcrumbs)

@RepoRoutes.route('/repo/<RepoName>/code')
@RepoRoutes.route('/repo/<RepoName>/tree/<BranchName>')
@UserLoginManager.RequireLogin()
def ViewCode(RepoName, BranchName=None):
    # ViewCode: View Repository Code/Files Structure
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj:
        flash('Repository Not Found Or Access Denied', 'error')
        return redirect(url_for('RepoRoutes.Dashboard'))

    # Default To Main Branch If No Branch Specified
    if not BranchName:
        MainBranch = Branch.query.filter_by(RepositoryId=RepoObj.Id, Name='main').first()
        BranchName = MainBranch.Name if MainBranch else 'main'

    Path = request.args.get('path', '')
    Files = DevBhoomiRepoManager.GetRepositoryFiles(RepoObj.Id, Path, BranchName)
    Breadcrumbs = []
    if Path:
        parts = Path.split('/')
        current_path = ''
        for part in parts:
            if part:
                current_path += part + '/'
                Breadcrumbs.append({
                    'name': part,
                    'path': current_path.rstrip('/')
                })

    return render_template('CodeView.html', Repository=RepoObj, Files=Files, CurrentPath=Path, Breadcrumbs=Breadcrumbs, CurrentBranch=BranchName)

@RepoRoutes.route('/repo/<RepoName>/upload', methods=['GET', 'POST'])
@UserLoginManager.RequireLogin()
def UploadFile(RepoName):
    # UploadFile: Upload Files To Repository
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj:
        flash('Repository Not Found Or Access Denied', 'error')
        return redirect(url_for('RepoRoutes.Dashboard'))

    if request.method == 'POST':
        if 'files' not in request.files:
            flash('No File Selected', 'error')
            return redirect(request.url)

        files = request.files.getlist('files')
        commit_message = request.form.get('commit_message', 'Upload Files')

        uploaded_files = []
        for i, file in enumerate(files):
            if file.filename == '':
                continue
            if file:
                # Save File Temporarily
                import os
                import uuid
                # Get Relative Path From Form Data, Fallback To Filename
                relative_path = request.form.get(f'relative_path_{i}', file.filename)
                temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(uuid.uuid4()) + '_' + os.path.basename(file.filename))
                file.save(temp_path)
                uploaded_files.append((relative_path, temp_path))

        if uploaded_files:
            # Add Files To Repository
            success = DevBhoomiRepoManager.AddFilesToRepository(RepoObj.Id, uploaded_files, commit_message, CurrentUser.Id)
            if success:
                flash(f'Successfully Uploaded {len(uploaded_files)} File(s)', 'success')
            else:
                flash('Failed To Upload Files', 'error')
        else:
            flash('No Valid Files Selected', 'error')

        return redirect(url_for('RepoRoutes.ViewRepository', RepoName=RepoName))

    return render_template('UploadFile.html', Repository=RepoObj)

@RepoRoutes.route('/repo/<RepoName>/new-file', methods=['GET', 'POST'])
@UserLoginManager.RequireLogin()
def CreateFile(RepoName):
    # CreateFile: Create A New File In Repository
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj:
        flash('Repository Not Found Or Access Denied', 'error')
        return redirect(url_for('RepoRoutes.Dashboard'))

    if request.method == 'POST':
        filename = request.form.get('filename')
        content = request.form.get('content', '')
        commit_message = request.form.get('commit_message', f'Create {filename}')

        if not filename:
            flash('Filename Is Required', 'error')
            return redirect(request.url)

        # Create File In Repository
        success = DevBhoomiRepoManager.CreateFileInRepository(RepoObj.Id, filename, content, commit_message, CurrentUser.Id)
        if success:
            flash(f'File "{filename}" Created Successfully', 'success')
            return redirect(url_for('RepoRoutes.ViewRepository', RepoName=RepoName))
        else:
            flash('Failed To Create File', 'error')

    return render_template('CreateFile.html', Repository=RepoObj)

# API Endpoints

@RepoRoutes.route('/api/repos', methods=['GET'])
@UserLoginManager.RequireLogin()
def ApiListRepositories():
    # ApiListRepositories: API To List User's Repositories
    CurrentUser = UserLoginManager.GetCurrentUser()
    Repositories = DevBhoomiRepoManager.ListUserRepositories(CurrentUser.Id)
    return jsonify([{
        'id': repo.Id,
        'name': repo.Name,
        'description': repo.Description,
        'isPrivate': repo.IsPrivate,
        'createdAt': repo.CreatedAt.isoformat()
    } for repo in Repositories])

@RepoRoutes.route('/api/repo/<RepoName>/branches', methods=['GET'])
@UserLoginManager.RequireLogin()
def ApiListBranches(RepoName):
    # ApiListBranches: API To List Branches For A Repository
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj:
        return jsonify({'error': 'Repository Not Found'}), 404

    Branches = DevBhoomiRepoManager.GetBranches(RepoObj.Id)
    return jsonify([{
        'id': branch.Id,
        'name': branch.Name,
        'isProtected': branch.IsProtected
    } for branch in Branches])

@RepoRoutes.route('/api/repo/<RepoName>/commits', methods=['GET'])
@UserLoginManager.RequireLogin()
def ApiListCommits(RepoName):
    # ApiListCommits: API To List Commits For A Repository
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj:
        return jsonify({'error': 'Repository Not Found'}), 404

    BranchName = request.args.get('branch')
    Commits = DevBhoomiRepoManager.GetCommitHistory(RepoObj.Id, BranchName, Limit=100)
    return jsonify([{
        'hash': commit.Hash,
        'message': commit.Message,
        'author': commit.Author.Username if commit.Author else 'Unknown',
        'createdAt': commit.CreatedAt.isoformat()
    } for commit in Commits])

@RepoRoutes.route('/api/repo/<RepoName>/contents', methods=['GET'])
@UserLoginManager.RequireLogin()
def ApiGetRepositoryContents(RepoName):
    # ApiGetRepositoryContents: API To Get Repository File Contents By Repo Name
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj:
        return jsonify({'error': 'Repository Not Found'}), 404

    # Get Optional Branch And Path Parameters
    BranchName = request.args.get('branch', 'main')
    Path = request.args.get('path', '')

    # Get Files In The Repository
    Files = DevBhoomiRepoManager.GetRepositoryFiles(RepoObj.Id, Path, BranchName)
    
    return jsonify({
        'repository': RepoObj.Name,
        'branch': BranchName,
        'path': Path,
        'files': [{
            'name': file.get('name'),
            'type': file.get('type'),  # 'File' or 'Directory'
            'path': file.get('path'),
            'size': file.get('size', 0),
            'lastModified': file.get('lastModified')
        } for file in Files] if Files else []
    })

@RepoRoutes.route('/links')
def Links():
    # Links: Show All Footer Links
    return render_template('Links.html')
