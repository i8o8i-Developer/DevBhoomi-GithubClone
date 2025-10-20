import os
from git import Repo
from Models import db, Commit, Branch, Repository
from RepoManager import DevBhoomiRepoManager

class GitHooks:
    @staticmethod
    def PostReceiveHook(RepoId, OldRev, NewRev, RefName):
        # PostReceiveHook: Handle Post-Receive Git Hook
        BranchName = RefName.split('/')[-1] if '/' in RefName else RefName

        # Get Or Create Branch In Database
        BranchObj = Branch.query.filter_by(RepositoryId=RepoId, Name=BranchName).first()
        if not BranchObj:
            BranchObj = DevBhoomiRepoManager.CreateBranch(RepoId, BranchName)

        # Get Repository And Check Protection Rules
        RepoObj = Repository.query.get(RepoId)
        if not RepoObj:
            return False

        # Check Branch Protection Rules
        if BranchObj.IsProtected:
            ProtectionRules = DevBhoomiRepoManager.GetBranchProtectionRules(BranchObj.Id)
            for Rule in ProtectionRules:
                if Rule.RuleType == 'no_force_push' and Rule.Value:
                    if OldRev != '0000000000000000000000000000000000000000':
                        # Check If This Is A Force Push (Non-Fast-Forward)
                        RepoPath = DevBhoomiRepoManager.GetRepoPath(RepoId)
                        GitRepo = Repo(RepoPath)
                        try:
                            # Check If Old_Rev Is Ancestor Of New_Rev
                            GitRepo.git.merge_base('--is-ancestor', OldRev, NewRev)
                        except:
                            return False  # Force Push Not Allowed

        # Record Commits In Database
        GitHooks.RecordCommits(RepoId, BranchObj.Id, OldRev, NewRev)

        return True

    @staticmethod
    def RecordCommits(RepoId, BranchId, OldRev, NewRev):
        # RecordCommits: Record New Commits In The Database
        RepoPath = DevBhoomiRepoManager.GetRepoPath(RepoId)
        GitRepo = Repo(RepoPath)

        # Get Commits Between Old_Rev And New_Rev
        try:
            Commits = list(GitRepo.iter_commits(f'{OldRev}..{NewRev}'))
        except:
            # For New Branch Or Initial Commit
            Commits = list(GitRepo.iter_commits(NewRev, max_count=50))

        for GitCommit in Commits:
            # Check If Commit Already Exists
            if not Commit.query.filter_by(Hash=GitCommit.hexsha).first():
                # Find Author (For Now, Assume Single User)
                Author = None  # TODO: Map Git Author To User

                NewCommit = Commit(
                    Hash=GitCommit.hexsha,
                    Message=GitCommit.message,
                    AuthorId=Author.Id if Author else None,
                    RepositoryId=RepoId,
                    BranchId=BranchId,
                    ParentHashes=','.join([p.hexsha for p in GitCommit.parents])
                )
                db.session.add(NewCommit)

        db.session.commit()

    @staticmethod
    def PreReceiveHook(RepoId, OldRev, NewRev, RefName):
        # PreReceiveHook: Handle Pre-Receive Git Hook For Validation
        BranchName = RefName.split('/')[-1] if '/' in RefName else RefName

        BranchObj = Branch.query.filter_by(RepositoryId=RepoId, Name=BranchName).first()
        if BranchObj and BranchObj.IsProtected:
            ProtectionRules = DevBhoomiRepoManager.GetBranchProtectionRules(BranchObj.Id)
            for Rule in ProtectionRules:
                if Rule.RuleType == 'review_required' and Rule.Value:
                    # TODO: Implement Review Requirement Check
                    pass
                elif Rule.RuleType == 'require_status_checks' and Rule.Value:
                    # TODO: Implement Status Checks Requirement
                    pass
                elif Rule.RuleType == 'require_up_to_date' and Rule.Value:
                    # TODO: Implement Up-To-Date Branch Requirement
                    pass
                elif Rule.RuleType == 'restrict_pushes' and Rule.Value:
                    # TODO: Implement Push Restrictions
                    pass
                elif Rule.RuleType == 'linear_history' and Rule.Value:
                    # TODO: Implement Linear History Enforcement
                    pass

        return True

    @staticmethod
    def SetupHooks(RepoId):
        # SetupHooks: Set Up Git Hooks For A Repository
        RepoPath = DevBhoomiRepoManager.GetRepoPath(RepoId)
        HooksDir = os.path.join(RepoPath, '.git', 'hooks')

        # Ensure Hooks Directory Exists
        os.makedirs(HooksDir, exist_ok=True)

        # Get Absolute Path To BackEnd Directory
        BackendPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

        # Create Post-Receive Hook (Python Script For Windows Compatibility)
        PostReceivePath = os.path.join(HooksDir, 'post-receive')
        with open(PostReceivePath, 'w') as f:
            f.write(f'''#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, r"{BackendPath}")
from GitHooks import GitHooks

# Read git hook input
for line in sys.stdin:
    oldrev, newrev, refname = line.strip().split()
    GitHooks.PostReceiveHook({RepoId}, oldrev, newrev, refname)
''')

        # Make Executable (Works On Both Windows And Unix)
        try:
            os.chmod(PostReceivePath, 0o755)
        except:
            # On Windows, chmod Might Not Work, But That's Okay
            pass

        # Create Pre-Receive Hook (Python Script For Windows Compatibility)
        PreReceivePath = os.path.join(HooksDir, 'pre-receive')
        with open(PreReceivePath, 'w') as f:
            f.write(f'''#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, r"{BackendPath}")
from GitHooks import GitHooks

# Read git hook input
for line in sys.stdin:
    oldrev, newrev, refname = line.strip().split()
    result = GitHooks.PreReceiveHook({RepoId}, oldrev, newrev, refname)
    if not result:
        sys.exit(1)
''')

        # Make Executable (Works On Both Windows And Unix)
        try:
            os.chmod(PreReceivePath, 0o755)
        except:
            # On Windows, chmod Might Not Work, But That's Okay
            pass
