from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'Users'
    Id = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(255), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    Repositories = db.relationship('Repository', backref='Owner', lazy=True)
    Commits = db.relationship('Commit', backref='Author', lazy=True)
    RepositoryAccess = db.relationship('RepositoryAccess', backref='User', lazy=True)

class Repository(db.Model):
    __tablename__ = 'Repositories'
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    Description = db.Column(db.Text)
    OwnerId = db.Column(db.Integer, db.ForeignKey('Users.Id'), nullable=False)
    IsPrivate = db.Column(db.Boolean, default=True)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)
    UpdatedAt = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    Branches = db.relationship('Branch', backref='Repository', lazy=True)
    Commits = db.relationship('Commit', backref='Repository', lazy=True)
    RepositoryAccess = db.relationship('RepositoryAccess', backref='Repository', lazy=True)

    __table_args__ = (db.UniqueConstraint('OwnerId', 'Name', name='unique_owner_repo'),)

class Branch(db.Model):
    __tablename__ = 'Branches'
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(255), nullable=False)
    RepositoryId = db.Column(db.Integer, db.ForeignKey('Repositories.Id'), nullable=False)
    IsProtected = db.Column(db.Boolean, default=False)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    Commits = db.relationship('Commit', backref='Branch', lazy=True)
    ProtectionRules = db.relationship('BranchProtectionRule', backref='Branch', lazy=True)

    __table_args__ = (db.UniqueConstraint('RepositoryId', 'Name', name='unique_repo_branch'),)

class Commit(db.Model):
    __tablename__ = 'Commits'
    Id = db.Column(db.Integer, primary_key=True)
    Hash = db.Column(db.String(40), unique=True, nullable=False)
    Message = db.Column(db.Text)
    AuthorId = db.Column(db.Integer, db.ForeignKey('Users.Id'))
    RepositoryId = db.Column(db.Integer, db.ForeignKey('Repositories.Id'), nullable=False)
    BranchId = db.Column(db.Integer, db.ForeignKey('Branches.Id'), nullable=False)
    ParentHashes = db.Column(db.Text)  # Comma-Separated Parent Commit Hashes
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

class BranchProtectionRule(db.Model):
    __tablename__ = 'BranchProtectionRules'
    Id = db.Column(db.Integer, primary_key=True)
    BranchId = db.Column(db.Integer, db.ForeignKey('Branches.Id'), nullable=False)
    RuleType = db.Column(db.String(50), nullable=False)  # 'no_force_push', 'review_required', 'require_up_to_date'
    Value = db.Column(db.Boolean, default=True)
    CreatedAt = db.Column(db.DateTime, default=datetime.utcnow)

class RepositoryAccess(db.Model):
    __tablename__ = 'RepositoryAccess'
    Id = db.Column(db.Integer, primary_key=True)
    RepositoryId = db.Column(db.Integer, db.ForeignKey('Repositories.Id'), nullable=False)
    UserId = db.Column(db.Integer, db.ForeignKey('Users.Id'), nullable=False)
    PermissionLevel = db.Column(db.String(20), default='read')  # 'read', 'write', 'admin'
    GrantedAt = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('RepositoryId', 'UserId', name='unique_repo_user_access'),)
