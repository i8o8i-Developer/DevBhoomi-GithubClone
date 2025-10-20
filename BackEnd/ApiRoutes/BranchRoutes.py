from flask import Blueprint, request, jsonify, redirect, url_for, flash
from UserLoginManager import UserLoginManager
from RepoManager import DevBhoomiRepoManager

BranchRoutes = Blueprint('BranchRoutes', __name__)

@BranchRoutes.route('/repo/<RepoName>/branch/create', methods=['POST'])
@UserLoginManager.RequireLogin()
def CreateBranch(RepoName):
    # CreateBranch: Create A New Branch
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj:
        flash('Repository Not Found Or Access Denied', 'error')
        return redirect(url_for('RepoRoutes.Dashboard'))

    BranchName = request.form.get('BranchName')
    if not BranchName:
        flash('Branch Name Is Required', 'error')
        return redirect(url_for('RepoRoutes.ViewBranches', RepoName=RepoName))

    NewBranch = DevBhoomiRepoManager.CreateBranch(RepoObj.Id, BranchName)
    if NewBranch:
        flash(f'Branch "{BranchName}" Created Successfully', 'success')
    else:
        flash(f'Branch "{BranchName}" Already Exists', 'error')

    return redirect(url_for('RepoRoutes.ViewBranches', RepoName=RepoName))

@BranchRoutes.route('/repo/<RepoName>/branch/<BranchName>/delete', methods=['POST'])
@UserLoginManager.RequireLogin()
def DeleteBranch(RepoName, BranchName):
    # DeleteBranch: Delete A Branch
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj or RepoObj.OwnerId != CurrentUser.Id:
        flash('Repository Not Found Or Access Denied', 'error')
        return redirect(url_for('RepoRoutes.Dashboard'))

    if DevBhoomiRepoManager.DeleteBranch(RepoObj.Id, BranchName):
        flash(f'Branch "{BranchName}" Deleted Successfully', 'success')
    else:
        flash(f'Cannot Delete Branch "{BranchName}" (May Be Protected)', 'error')

    return redirect(url_for('RepoRoutes.ViewBranches', RepoName=RepoName))

@BranchRoutes.route('/repo/<RepoName>/branch/<int:BranchId>/protect', methods=['POST'])
@UserLoginManager.RequireLogin()
def SetBranchProtection(RepoName, BranchId):
    # SetBranchProtection: Set Protection Rules For A Branch
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj or RepoObj.OwnerId != CurrentUser.Id:
        return jsonify({'error': 'Access Denied'}), 403

    RuleType = request.form.get('RuleType')
    Value = request.form.get('Value') == 'true'

    DevBhoomiRepoManager.SetBranchProtection(BranchId, RuleType, Value)
    return jsonify({'success': True})

# API Endpoints

@BranchRoutes.route('/api/repo/<RepoName>/branch', methods=['POST'])
@UserLoginManager.RequireLogin()
def ApiCreateBranch(RepoName):
    # ApiCreateBranch: API To Create A Branch
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj:
        return jsonify({'error': 'Repository Not Found'}), 404

    data = request.get_json()
    BranchName = data.get('name')
    if not BranchName:
        return jsonify({'error': 'Branch Name Is Required'}), 400

    NewBranch = DevBhoomiRepoManager.CreateBranch(RepoObj.Id, BranchName)
    if NewBranch:
        return jsonify({
            'id': NewBranch.Id,
            'name': NewBranch.Name,
            'isProtected': NewBranch.IsProtected
        })
    else:
        return jsonify({'error': 'Branch Already Exists'}), 409

@BranchRoutes.route('/api/repo/<RepoName>/branch/<BranchName>', methods=['DELETE'])
@UserLoginManager.RequireLogin()
def ApiDeleteBranch(RepoName, BranchName):
    # ApiDeleteBranch: API To Delete A Branch
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj or RepoObj.OwnerId != CurrentUser.Id:
        return jsonify({'error': 'Access Denied'}), 403

    if DevBhoomiRepoManager.DeleteBranch(RepoObj.Id, BranchName):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Cannot Delete Branch'}), 400

@BranchRoutes.route('/api/repo/<RepoName>/branch/<int:BranchId>/protection', methods=['GET', 'POST'])
@UserLoginManager.RequireLogin()
def ApiBranchProtection(RepoName, BranchId):
    # ApiBranchProtection: API To Get/Set Branch Protection Rules
    CurrentUser = UserLoginManager.GetCurrentUser()
    RepoObj = DevBhoomiRepoManager.GetRepositoryByName(RepoName, CurrentUser.Id)
    if not RepoObj or RepoObj.OwnerId != CurrentUser.Id:
        return jsonify({'error': 'Access Denied'}), 403

    if request.method == 'GET':
        Rules = DevBhoomiRepoManager.GetBranchProtectionRules(BranchId)
        return jsonify([{
            'type': rule.RuleType,
            'value': rule.Value
        } for rule in Rules])
    else:  # POST
        data = request.get_json()
        if isinstance(data, list):
            # Handle Multiple Rules
            for rule in data:
                RuleType = rule.get('type')
                Value = rule.get('value', True)
                DevBhoomiRepoManager.SetBranchProtection(BranchId, RuleType, Value)
        else:
            # Handle Single Rule (Backward Compatibility)
            RuleType = data.get('type')
            Value = data.get('value', True)
            DevBhoomiRepoManager.SetBranchProtection(BranchId, RuleType, Value)
        return jsonify({'success': True})
