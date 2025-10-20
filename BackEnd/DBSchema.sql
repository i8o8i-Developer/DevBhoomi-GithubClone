-- DevBhoomi Database Schema
-- SQLite Database

-- Users Table
CREATE TABLE Users (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT UNIQUE NOT NULL,
    PasswordHash TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Repositories Table
CREATE TABLE Repositories (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Description TEXT,
    OwnerId INTEGER NOT NULL,
    IsPrivate BOOLEAN DEFAULT 1,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (OwnerId) REFERENCES Users(Id) ON DELETE CASCADE,
    UNIQUE(OwnerId, Name)
);

-- Branches Table
CREATE TABLE Branches (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    RepositoryId INTEGER NOT NULL,
    IsProtected BOOLEAN DEFAULT 0,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (RepositoryId) REFERENCES Repositories(Id) ON DELETE CASCADE,
    UNIQUE(RepositoryId, Name)
);

-- Commits Table (Metadata for commits)
CREATE TABLE Commits (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Hash TEXT UNIQUE NOT NULL,
    Message TEXT,
    AuthorId INTEGER,
    RepositoryId INTEGER NOT NULL,
    BranchId INTEGER NOT NULL,
    ParentHashes TEXT, -- Comma-separated parent commit hashes
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (AuthorId) REFERENCES Users(Id),
    FOREIGN KEY (RepositoryId) REFERENCES Repositories(Id) ON DELETE CASCADE,
    FOREIGN KEY (BranchId) REFERENCES Branches(Id) ON DELETE CASCADE
);

-- BranchProtectionRules Table
CREATE TABLE BranchProtectionRules (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    BranchId INTEGER NOT NULL,
    RuleType TEXT NOT NULL, -- 'no_force_push', 'review_required', 'require_up_to_date'
    Value BOOLEAN DEFAULT 1,
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (BranchId) REFERENCES Branches(Id) ON DELETE CASCADE
);

-- RepositoryAccess Table (For future multi-user support)
CREATE TABLE RepositoryAccess (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    RepositoryId INTEGER NOT NULL,
    UserId INTEGER NOT NULL,
    PermissionLevel TEXT DEFAULT 'read', -- 'read', 'write', 'admin'
    GrantedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (RepositoryId) REFERENCES Repositories(Id) ON DELETE CASCADE,
    FOREIGN KEY (UserId) REFERENCES Users(Id) ON DELETE CASCADE,
    UNIQUE(RepositoryId, UserId)
);

-- Indexes For Performance
CREATE INDEX idx_repositories_owner ON Repositories(OwnerId);
CREATE INDEX idx_branches_repository ON Branches(RepositoryId);
CREATE INDEX idx_commits_repository ON Commits(RepositoryId);
CREATE INDEX idx_commits_branch ON Commits(BranchId);
CREATE INDEX idx_commits_hash ON Commits(Hash);
