import os
import shutil
from git import Repo, GitCommandError, Actor
from Models import db, Repository, Branch, Commit, BranchProtectionRule, RepositoryAccess

class DevBhoomiRepoManager:
    @staticmethod
    def GetRepoPath(RepoId):
        # GetRepoPath: Get The File System Path For A Repository
        from Config import Config
        # Get Repository With Owner Information
        repo = Repository.query.filter_by(Id=RepoId).first()
        if not repo:
            return None
        # New Structure: Repositories/<Username>/<RepoName>/Files
        return os.path.join(Config.REPOSITORIES_PATH, repo.Owner.Username, repo.Name, 'Files')

    @staticmethod
    def CreateRepository(Name, Description, OwnerId, IsPrivate=True):
        # CreateRepository: Create A New Repository
        if Repository.query.filter_by(OwnerId=OwnerId, Name=Name).first():
            return None  # Repository Already Exists

        NewRepo = Repository(Name=Name, Description=Description, OwnerId=OwnerId, IsPrivate=IsPrivate)
        db.session.add(NewRepo)
        db.session.commit()

        # Create The Repository Directory Structure And Initialize Git
        RepoPath = DevBhoomiRepoManager.GetRepoPath(NewRepo.Id)
        os.makedirs(RepoPath, exist_ok=True)
        Repo.init(RepoPath)  # Create Non-Bare Repository For File Operations

        # Create Default Main Branch
        DevBhoomiRepoManager.CreateBranch(NewRepo.Id, 'main')

        return NewRepo

    @staticmethod
    def MigrateRepositoryStructure():
        # MigrateRepositoryStructure: Migrate Existing Repositories To New Structure
        from Config import Config

        # Get All Repositories
        repositories = Repository.query.all()

        for repo in repositories:
            # Old Path: Repositories/RepoId
            old_path = os.path.join(Config.REPOSITORIES_PATH, str(repo.Id))

            # New Path: Repositories/Username/RepoName/Files
            new_path = DevBhoomiRepoManager.GetRepoPath(repo.Id)

            if os.path.exists(old_path) and old_path != new_path:
                # Create New Directory Structure
                os.makedirs(os.path.dirname(new_path), exist_ok=True)

                # Move The Repository
                if os.path.exists(new_path):
                    # If New Path Already Exists, Remove It First
                    shutil.rmtree(new_path)

                shutil.move(old_path, new_path)
                print(f"Migrated Repository {repo.Id} From {old_path} To {new_path}")

        print("Repository Migration Completed!")

    @staticmethod
    def GetRepository(RepoId, UserId=None):
        # GetRepository: Get Repository Details
        RepoObj = Repository.query.get(RepoId)
        if not RepoObj:
            return None

        # Check Access (For Now, Only Owner Can Access Private Repos)
        if RepoObj.IsPrivate and RepoObj.OwnerId != UserId:
            return None

        return RepoObj

    @staticmethod
    def GetRepositoryByName(RepoName, UserId=None):
        # GetRepositoryByName: Get Repository Details By Name
        RepoObj = Repository.query.filter_by(Name=RepoName).first()
        if not RepoObj:
            return None

        # Check Access (For Now, Only Owner Can Access Private Repos)
        if RepoObj.IsPrivate and RepoObj.OwnerId != UserId:
            return None

        return RepoObj

    @staticmethod
    def UpdateRepository(RepoId, OwnerId, Name=None, Description=None, IsPrivate=None):
        # UpdateRepository: Update Repository Details
        RepoObj = Repository.query.filter_by(Id=RepoId, OwnerId=OwnerId).first()
        if not RepoObj:
            return None

        if Name is not None:
            RepoObj.Name = Name
        if Description is not None:
            RepoObj.Description = Description
        if IsPrivate is not None:
            RepoObj.IsPrivate = IsPrivate

        db.session.commit()
        return RepoObj

    @staticmethod
    def ListUserRepositories(UserId):
        # ListUserRepositories: List All Repositories For A User
        return Repository.query.filter_by(OwnerId=UserId).all()

    @staticmethod
    def CreateBranch(RepoId, BranchName):
        # CreateBranch: Create A New Branch
        if Branch.query.filter_by(RepositoryId=RepoId, Name=BranchName).first():
            return None  # Branch Already Exists

        NewBranch = Branch(Name=BranchName, RepositoryId=RepoId)
        db.session.add(NewBranch)
        db.session.commit()
        return NewBranch

    @staticmethod
    def DeleteBranch(RepoId, BranchName):
        # DeleteBranch: Delete A Branch
        BranchObj = Branch.query.filter_by(RepositoryId=RepoId, Name=BranchName).first()
        if not BranchObj or BranchObj.IsProtected:
            return False

        db.session.delete(BranchObj)
        db.session.commit()
        return True

    @staticmethod
    def GetBranches(RepoId):
        # GetBranches: Get All Branches For A Repository
        return Branch.query.filter_by(RepositoryId=RepoId).all()

    @staticmethod
    def SetBranchProtection(BranchId, RuleType, Value=True):
        # SetBranchProtection: Set Protection Rule For A Branch
        ExistingRule = BranchProtectionRule.query.filter_by(BranchId=BranchId, RuleType=RuleType).first()
        if ExistingRule:
            ExistingRule.Value = Value
        else:
            NewRule = BranchProtectionRule(BranchId=BranchId, RuleType=RuleType, Value=Value)
            db.session.add(NewRule)
        db.session.commit()

    @staticmethod
    def GetBranchProtectionRules(BranchId):
        # GetBranchProtectionRules: Get Protection Rules For A Branch
        return BranchProtectionRule.query.filter_by(BranchId=BranchId).all()

    @staticmethod
    def CloneRepository(RepoId, ClonePath):
        # CloneRepository: Clone A Repository To A Local Path
        RepoPath = DevBhoomiRepoManager.GetRepoPath(RepoId)
        try:
            Repo.clone_from(RepoPath, ClonePath)
            return True
        except GitCommandError:
            return False

    @staticmethod
    def GetCommitHistory(RepoId, BranchName=None, Limit=50):
        # GetCommitHistory: Get Commit History For A Repository
        Query = Commit.query.filter_by(RepositoryId=RepoId)
        if BranchName:
            BranchObj = Branch.query.filter_by(RepositoryId=RepoId, Name=BranchName).first()
            if BranchObj:
                Query = Query.filter_by(BranchId=BranchObj.Id)
        return Query.order_by(Commit.CreatedAt.desc()).limit(Limit).all()

    @staticmethod
    def EnsureNonBareRepository(RepoId):
        # EnsureNonBareRepository: Convert Bare Repository To Non-Bare If Needed
        RepoPath = DevBhoomiRepoManager.GetRepoPath(RepoId)
        RepoObj = Repo(RepoPath)

        if RepoObj.bare:
            # Convert Bare Repository To Non-Bare
            import tempfile

            # Create Temporary Non-Bare Repository
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_repo_path = os.path.join(temp_dir, 'repo')
                temp_repo = Repo.clone_from(RepoPath, temp_repo_path, bare=False)

                # Replace Bare Repository With Non-Bare
                shutil.rmtree(RepoPath)
                shutil.move(temp_repo_path, RepoPath)

        return True

    @staticmethod
    def AddFilesToRepository(RepoId, Files, CommitMessage, UserId):
        # AddFilesToRepository: Add Uploaded Files To Repository
        try:
            # Ensure Repository Is Non-Bare
            DevBhoomiRepoManager.EnsureNonBareRepository(RepoId)

            RepoPath = DevBhoomiRepoManager.GetRepoPath(RepoId)
            RepoObj = Repo(RepoPath)

            # Add Files To Git
            for filename, temp_path in Files:
                dest_path = os.path.join(RepoPath, filename)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.move(temp_path, dest_path)
                RepoObj.index.add([filename])

            # Create Commit
            commit_obj = RepoObj.index.commit(CommitMessage, author=DevBhoomiRepoManager.GetGitAuthor(UserId))

            # Record Commit In Database
            DevBhoomiRepoManager.RecordCommitInDatabase(RepoId, commit_obj, UserId)

            # Clean Up Temp Files
            for _, temp_path in Files:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

            return True
        except Exception as e:
            print(f"Error Adding Files To Repository: {e}")
            return False

    @staticmethod
    def CreateFileInRepository(RepoId, Filename, Content, CommitMessage, UserId):
        # CreateFileInRepository: Create A New File In Repository
        try:
            # Ensure Repository Is Non-Bare
            DevBhoomiRepoManager.EnsureNonBareRepository(RepoId)

            RepoPath = DevBhoomiRepoManager.GetRepoPath(RepoId)
            RepoObj = Repo(RepoPath)

            # Create File
            file_path = os.path.join(RepoPath, Filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(Content)

            # Add To Git And Commit
            RepoObj.index.add([Filename])
            commit_obj = RepoObj.index.commit(CommitMessage, author=DevBhoomiRepoManager.GetGitAuthor(UserId))

            # Record Commit In Database
            DevBhoomiRepoManager.RecordCommitInDatabase(RepoId, commit_obj, UserId)

            return True
        except Exception as e:
            print(f"Error Creating File In Repository : {e}")
            return False

    @staticmethod
    def GetGitAuthor(UserId):
        # GetGitAuthor: Get Git Author For Commits
        from Models import User
        UserObj = User.query.get(UserId)
        if UserObj:
            return Actor(UserObj.Username, f"{UserObj.Username}@devbhoomi.local")
        return Actor("Unknown", "unknown@devbhoomi.local")

    @staticmethod
    def GetReadmeContent(RepoId, BranchName=None):
        # GetReadmeContent: Get README File Content From Repository

        RepoPath = DevBhoomiRepoManager.GetRepoPath(RepoId)
        if not os.path.exists(RepoPath):
            return None

        try:
            GitRepo = Repo(RepoPath)
            if GitRepo.bare:
                return None

            # Use Specified Branch Or Default To Current Branch
            if BranchName:
                try:
                    branch_ref = GitRepo.heads[BranchName]
                    tree = branch_ref.commit.tree
                except:
                    # Branch Doesn't Exist, Fall Back To Current
                    tree = GitRepo.head.commit.tree
            else:
                tree = GitRepo.head.commit.tree

            # Look For README Files In Order Of Preference
            readme_files = ['README.md', 'README.txt', 'README.rst', 'README', 'readme.md', 'readme.txt']

            for readme_file in readme_files:
                try:
                    blob = tree[readme_file]
                    content = blob.data_stream.read().decode('utf-8')
                    return {
                        'filename': readme_file,
                        'content': content,
                        'is_markdown': readme_file.lower().endswith('.md')
                    }
                except:
                    continue

        except:
            # Fall Back To File System Reading If Git Operations Fail
            readme_files = ['README.md', 'README.txt', 'README.rst', 'README', 'readme.md', 'readme.txt']
            root_files = os.listdir(RepoPath)

            for readme_file in readme_files:
                if readme_file in root_files:
                    try:
                        with open(os.path.join(RepoPath, readme_file), 'r', encoding='utf-8') as f:
                            content = f.read()
                            return {
                                'filename': readme_file,
                                'content': content,
                                'is_markdown': readme_file.lower().endswith('.md')
                            }
                    except:
                        continue

        return None

    @staticmethod
    def GetLicenseContent(RepoId, BranchName=None):
        # GetLicenseContent: Get LICENSE File Content From Repository

        RepoPath = DevBhoomiRepoManager.GetRepoPath(RepoId)
        if not os.path.exists(RepoPath):
            return None

        try:
            GitRepo = Repo(RepoPath)
            if GitRepo.bare:
                return None

            # Use Specified Branch Or Default To Current Branch
            if BranchName:
                try:
                    branch_ref = GitRepo.heads[BranchName]
                    tree = branch_ref.commit.tree
                except:
                    # Branch Doesn't Exist, Fall Back To Current
                    tree = GitRepo.head.commit.tree
            else:
                tree = GitRepo.head.commit.tree

            # Look For LICENSE Files
            license_files = ['LICENSE', 'LICENSE.md', 'LICENSE.txt', 'COPYING', 'license', 'license.md', 'license.txt']

            for license_file in license_files:
                try:
                    blob = tree[license_file]
                    content = blob.data_stream.read().decode('utf-8')
                    return {
                        'filename': license_file,
                        'content': content,
                        'is_markdown': license_file.lower().endswith('.md')
                    }
                except:
                    continue

        except:
            # Fall Back To File System Reading If Git Operations Fail
            license_files = ['LICENSE', 'LICENSE.md', 'LICENSE.txt', 'COPYING', 'license', 'license.md', 'license.txt']
            root_files = os.listdir(RepoPath)

            for license_file in license_files:
                if license_file in root_files:
                    try:
                        with open(os.path.join(RepoPath, license_file), 'r', encoding='utf-8') as f:
                            content = f.read()
                            return {
                                'filename': license_file,
                                'content': content,
                                'is_markdown': license_file.lower().endswith('.md')
                            }
                    except:
                        continue

        return None

    @staticmethod
    def GetRepositoryStats(RepoId, BranchName=None):
        # GetRepositoryStats: Get Repository Statistics

        RepoPath = DevBhoomiRepoManager.GetRepoPath(RepoId)

        stats = {
            'commits': 0,
            'branches': 0,
            'files': 0,
            'size': 0
        }

        # Count Commits
        try:
            GitRepo = Repo(RepoPath)
            if BranchName:
                try:
                    branch_ref = GitRepo.heads[BranchName]
                    stats['commits'] = len(list(GitRepo.iter_commits(branch_ref)))
                except:
                    # Branch Doesn't Exist, Count All Commits
                    stats['commits'] = len(list(GitRepo.iter_commits()))
            else:
                stats['commits'] = len(list(GitRepo.iter_commits()))
        except:
            stats['commits'] = 0

        # Count Branches
        stats['branches'] = len(DevBhoomiRepoManager.GetBranches(RepoId))

        # Count Files And Calculate Size From Committed Files Only
        try:
            # Ensure Repository Is Non-Bare
            DevBhoomiRepoManager.EnsureNonBareRepository(RepoId)

            GitRepo = Repo(RepoPath)
            if GitRepo.git_dir and not GitRepo.bare and GitRepo.heads:
                # Use Specified Branch Or Default To Current Branch
                if BranchName:
                    try:
                        branch_ref = GitRepo.heads[BranchName]
                        tree = branch_ref.commit.tree
                    except:
                        # Branch Doesn't Exist, Fall Back To Current
                        tree = GitRepo.head.commit.tree
                else:
                    tree = GitRepo.head.commit.tree

                # Count Files From Branch Commit
                total_files = len(list(tree.traverse()))
                total_size = sum(item.size for item in tree.traverse() if hasattr(item, 'size'))
                stats['files'] = total_files
                stats['size'] = total_size
            else:
                # Empty Repository
                stats['files'] = 0
                stats['size'] = 0
        except:
            # Repository Not Initialized Or Empty
            stats['files'] = 0
            stats['size'] = 0

        return stats

    @staticmethod
    def GetRepositoryFiles(RepoId, Path='', BranchName=None):
        # GetRepositoryFiles: Get Repository File Structure Like GitHub's Code View

        # Ensure Repository Is Non-Bare For File Operations
        DevBhoomiRepoManager.EnsureNonBareRepository(RepoId)

        RepoPath = DevBhoomiRepoManager.GetRepoPath(RepoId)
        FullPath = os.path.join(RepoPath, Path) if Path else RepoPath

        if not os.path.exists(FullPath):
            return []

        files = []
        try:
            # Try To Get Files From Git Index If Repository Has Commits
            GitRepo = Repo(RepoPath)
            if GitRepo.git_dir and not GitRepo.bare:
                try:
                    # Use Specified Branch Or Default To Current Branch
                    if BranchName:
                        try:
                            branch_ref = GitRepo.heads[BranchName]
                            tree = branch_ref.commit.tree
                        except:
                            # Branch Doesn't Exist, Fall Back To Current
                            tree = GitRepo.head.commit.tree
                    else:
                        tree = GitRepo.head.commit.tree

                    if Path:
                        # Navigate To Subdirectory
                        for item in Path.split('/'):
                            if item:
                                tree = tree[item]

                    for item in tree.blobs + tree.trees:
                        item_path = os.path.join(Path, item.name) if Path else item.name
                        # Normalize Path To Use Forward Slashes
                        item_path = item_path.replace('\\', '/')
                        files.append({
                            'name': item.name,
                            'path': item_path,
                            'type': 'tree' if hasattr(item, 'trees') else 'blob',
                            'size': item.size if hasattr(item, 'size') else 0
                        })
                except:
                    # Repository Might Be Empty, Fall Back To Filesystem
                    pass
        except:
            # Repository Not Initialized Yet
            pass

        # If No Files From Git, Get From Filesystem (For Uncommitted Files)
        if not files:
            try:
                for item in os.listdir(FullPath):
                    if item.startswith('.git'):
                        continue

                    item_path = os.path.join(FullPath, item)
                    is_dir = os.path.isdir(item_path)

                    item_rel_path = os.path.join(Path, item) if Path else item
                    # Normalize Path To Use Forward Slashes
                    item_rel_path = item_rel_path.replace('\\', '/')
                    files.append({
                        'name': item,
                        'path': item_rel_path,
                        'type': 'tree' if is_dir else 'blob',
                        'size': 0 if is_dir else os.path.getsize(item_path)
                    })
            except:
                pass

        # Sort: Directories First, Then Files Alphabetically
        files.sort(key=lambda x: (x['type'] != 'tree', x['name'].lower()))
        return files

    @staticmethod
    def RecordCommitInDatabase(RepoId, GitCommit, UserId):
        # RecordCommitInDatabase: Record A Git Commit In The Database
        try:
            # Check If Commit Already Exists
            if not Commit.query.filter_by(Hash=GitCommit.hexsha).first():
                # Get Branch (Assume Main For Now)
                BranchObj = Branch.query.filter_by(RepositoryId=RepoId, Name='main').first()
                if not BranchObj:
                    BranchObj = DevBhoomiRepoManager.CreateBranch(RepoId, 'main')

                NewCommit = Commit(
                    Hash=GitCommit.hexsha,
                    Message=GitCommit.message,
                    AuthorId=UserId,
                    RepositoryId=RepoId,
                    BranchId=BranchObj.Id,
                    ParentHashes=','.join([p.hexsha for p in GitCommit.parents]) if GitCommit.parents else '',
                    CreatedAt=GitCommit.authored_datetime
                )
                db.session.add(NewCommit)
                db.session.commit()
        except Exception as e:
            print(f"Error Recording Commit In Database: {e}")
            db.session.rollback()

    @staticmethod
    def GetFileContent(RepoId, FilePath):
        # GetFileContent: Get The Content Of A Specific File

        # Normalize The File Path
        FilePath = FilePath.replace('\\', '/').strip('/')

        # Ensure Repository Is Non-Bare
        DevBhoomiRepoManager.EnsureNonBareRepository(RepoId)

        RepoPath = DevBhoomiRepoManager.GetRepoPath(RepoId)
        FullFilePath = os.path.join(RepoPath, FilePath)

        try:
            # Try Filesystem First (For Most Reliable Access)
            if os.path.exists(FullFilePath) and os.path.isfile(FullFilePath):
                with open(FullFilePath, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()

            # Try To Get File Content From Git (For Committed Files)
            GitRepo = Repo(RepoPath)
            if GitRepo.heads:
                try:
                    # Navigate The Tree Step By Step
                    tree = GitRepo.head.commit.tree
                    if FilePath:
                        path_parts = FilePath.split('/')
                        for part in path_parts:
                            if part:  # Skip Empty Parts
                                tree = tree[part]
                    
                    # Now Tree Should Be The File Blob
                    if hasattr(tree, 'data_stream'):
                        return tree.data_stream.read().decode('utf-8', errors='replace')
                except Exception as e:
                    print(f"Error Accessing Git Tree For {FilePath}: {e}")
                    pass

        except Exception as e:
            print(f"Error Reading File {FilePath}: {e}")

        return None

    @staticmethod
    def UpdateFileInRepository(RepoId, FilePath, Content, CommitMessage, UserId):
        # UpdateFileInRepository: Update An Existing File In Repository
        try:
            # Ensure Repository Is Non-Bare
            DevBhoomiRepoManager.EnsureNonBareRepository(RepoId)

            RepoPath = DevBhoomiRepoManager.GetRepoPath(RepoId)
            RepoObj = Repo(RepoPath)

            # Update File
            file_path = os.path.join(RepoPath, FilePath)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(Content)

            # Add To Git And Commit
            RepoObj.index.add([FilePath])
            commit_obj = RepoObj.index.commit(CommitMessage, author=DevBhoomiRepoManager.GetGitAuthor(UserId))

            # Record Commit In Database
            DevBhoomiRepoManager.RecordCommitInDatabase(RepoId, commit_obj, UserId)

            return True
        except Exception as e:
            print(f"Error Updating File In Repository: {e}")
            return False

    @staticmethod
    def DeleteRepository(RepoId, OwnerId):
        # DeleteRepository: Delete A Repository And All Its Data

        RepoObj = Repository.query.filter_by(Id=RepoId, OwnerId=OwnerId).first()
        if not RepoObj:
            return False

        # Get Repository Path Before Deleting Database Record
        RepoPath = DevBhoomiRepoManager.GetRepoPath(RepoId)
        if not RepoPath:
            return False

        # Delete All Related Data First
        try:
            # Delete Repository Access Records
            RepositoryAccess.query.filter_by(RepositoryId=RepoId).delete()

            # Delete Commits
            Commit.query.filter_by(RepositoryId=RepoId).delete()

            # Delete Branches And Their Protection Rules
            branches = Branch.query.filter_by(RepositoryId=RepoId).all()
            for branch in branches:
                BranchProtectionRule.query.filter_by(BranchId=branch.Id).delete()
            Branch.query.filter_by(RepositoryId=RepoId).delete()

            # Delete Repository Record
            db.session.delete(RepoObj)
            db.session.commit()

            # Delete Repository Files
            if os.path.exists(RepoPath):
                try:
                    shutil.rmtree(RepoPath)
                    print(f"Successfully Deleted Repository Files At : {RepoPath}")
                except Exception as file_error:
                    print(f"Warning: Failed To Delete Repository Files At : {RepoPath}: {file_error}")
                    # Don't Fail The Entire Operation For File Deletion Issues
                    # The Repository Is Successfully Removed From Database

            return True
        except Exception as e:
            print(f"Error Deleting Repository: {e}")
            db.session.rollback()
            return False
