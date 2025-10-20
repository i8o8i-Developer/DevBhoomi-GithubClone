# 🚀 DevBhoomi - Git Repository Hosting Platform

```
██████╗ ███████╗██╗   ██╗██████╗ ██╗  ██╗ ██████╗  ██████╗ ███╗   ███╗██╗
██╔══██╗██╔════╝██║   ██║██╔══██╗██║  ██║██╔═══██╗██╔═══██╗████╗ ████║██║
██║  ██║█████╗  ██║   ██║██████╔╝███████║██║   ██║██║   ██║██╔████╔██║██║
██║  ██║██╔══╝  ╚██╗ ██╔╝██╔══██╗██╔══██║██║   ██║██║   ██║██║╚██╔╝██║██║
██████╔╝███████╗ ╚████╔╝ ██████╔╝██║  ██║╚██████╔╝╚██████╔╝██║ ╚═╝ ██║██║
╚═════╝ ╚══════╝  ╚═══╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝
```

> **A Modern, Self-Hosted Git Repository Management Platform Inspired By GitHub**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-lightgrey.svg)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-green.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [🔧 Usage](#-usage)
- [📚 API Documentation](#-api-documentation)
- [🎨 UI/UX](#-uiux)
- [🛠️ Development](#️-development)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [🙏 Acknowledgments](#-acknowledgments)

---

## ✨ Features

### 🔐 Authentication & User Management
- **Secure User Registration** - Create Accounts With Email Verification
- **Password Hashing** - Bcrypt Encryption For Secure Password Storage
- **Session Management** - Flask-Session For Persistent User Sessions
- **User Profiles** - Manage Personal Information And Repositories

### 📁 Repository Management
- **Create Repositories** - Public And Private Repository Support
- **Repository Settings** - Configure Repository Visibility And Permissions
- **File Operations** - Upload, Edit, And Delete Files Through Web Interface
- **Directory Structure** - Organized File System With Git Integration

### 🌿 Branch & Version Control
- **Branch Creation** - Create And Manage Multiple Branches
- **Branch Protection** - Configure Protection Rules For Critical Branches
- **Commit History** - Track All Changes With Detailed Commit Information
- **Merge Operations** - Handle Branch Merges And Conflicts

### 🔍 Search & Discovery
- **Repository Search** - Find Repositories By Name Or Description
- **User Search** - Discover Other Users And Their Projects
- **Code Search** - Search Within Repository Files And Content

### 🎨 Modern UI/UX
- **Dark Theme** - GitHub-Inspired Dark Interface
- **Responsive Design** - Works On Desktop And Mobile Devices
- **Intuitive Navigation** - Clean, Modern User Interface
- **Real-time Updates** - Dynamic Content Loading

### 🛡️ Security & Access Control
- **Access Permissions** - Read, Write, And Admin Permissions
- **Repository Privacy** - Private Repositories With Access Control
- **Git Hooks** - Automated Git Operations And Validations
- **Input Validation** - Secure Form Handling And Data Validation

---

## 🏗️ Architecture

```
DevBhoomi/
├── BackEnd/                    # Flask Application Core
│   ├── App.py                 # Main Flask Application
│   ├── Config.py              # Application Configuration
│   ├── Models.py              # SQLAlchemy Data Models
│   ├── Setup_DB.py            # Database Initialization
│   ├── UserLoginManager.py    # Authentication Manager
│   ├── RepoManager.py         # Repository Operations
│   ├── GitHooks.py            # Git Hook Management
│   ├── DBSchema.sql           # Database Schema
│   └── ApiRoutes/             # API Blueprints
│       ├── AuthRoutes.py      # Authentication Endpoints
│       ├── RepoRoutes.py      # Repository Management
│       ├── BranchRoutes.py    # Branch Operations
│       └── SearchRoutes.py    # Search Functionality
├── FrontEnd/                  # Web Interface
│   ├── Templates/             # Jinja2 HTML Templates
│   └── Static/                # CSS, JS, Assets
│       ├── Css/
│       └── Js/
├── Instance/                  # SQLite Database
├── Repositories/              # Git Repository Storage
├── Uploads/                   # File Upload Storage
└── Flask_Session/             # Session Data
```

### 🗄️ Database Schema

```sql
Users (Id, Username, PasswordHash, Email, CreatedAt)
Repositories (Id, Name, Description, OwnerId, IsPrivate, CreatedAt, UpdatedAt)
Branches (Id, Name, RepositoryId, IsProtected, CreatedAt)
Commits (Id, Hash, Message, AuthorId, RepositoryId, BranchId, ParentHashes, CreatedAt)
BranchProtectionRules (Id, BranchId, RuleType, Value, CreatedAt)
RepositoryAccess (Id, RepositoryId, UserId, PermissionLevel, GrantedAt)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 Or Higher
- Pip Package Manager
- Git (For Repository Operations)

### One-Command Setup

```bash
# Clone The Repository
git clone https://github.com/i8o8i-Developer/DevBhoomi-GithubClone.git
cd DevBhoomi-GithubClone

# Install Dependencies
pip install -r Requirements.txt

# Setup Database And Directories
python BackEnd/Setup_DB.py

# Run The Application
python BackEnd/App.py
```

Visit `http://localhost:5000` In Your Browser!

---

## 📦 Installation

### 1. Clone The Repository
```bash
git clone https://github.com/i8o8i-Developer/DevBhoomi-GithubClone.git
cd DevBhoomi-GithubClone
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r Requirements.txt
```

### 4. Setup Database
```bash
python BackEnd/Setup_DB.py
```

### 5. Configure Environment (Optional)
Create A `.env` File In The Root Directory:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///BackEnd/Instance/devbhoomi.db
```

### 6. Run The Application
```bash
python BackEnd/App.py
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `DevBhoomiSecretKey2025` | Flask Secret Key For Sessions |
| `DATABASE_URL` | `sqlite:///BackEnd/Instance/devbhoomi.db` | Database Connection String |
| `DEBUG` | `False` | Enable Debug Mode |

### Directory Structure
- `BackEnd/Instance/` - SQLite Database Files
- `BackEnd/Repositories/` - Git Repository Storage
- `BackEnd/Uploads/` - File Upload Storage
- `BackEnd/Flask_Session/` - Session Data

---

## 🔧 Usage

### Creating Your First Repository

1. **Register/Login** - Create An Account Or Log In
2. **Dashboard** - Access Your Personal Dashboard
3. **Create Repository** - Click "New Repository" Button
4. **Configure** - Set Name, Description, And Visibility
5. **Initialize** - Repository Is Created With Default `main` Branch

### Managing Files

- **Upload Files** - Use The Upload Interface For New Files
- **Edit Files** - Click On Files To View/Edit Content
- **Create Files** - Add New Files Through The Web Interface
- **Directory Navigation** - Browse Repository Structure

### Branch Management

- **Create Branches** - Add New Branches From Existing Ones
- **Switch Branches** - Change Active Branch In Repository View
- **Protect Branches** - Configure Protection Rules For Critical Branches

---

## 📚 API Documentation

### Authentication Endpoints

```
POST /api/login
GET  /login
POST /register
GET  /logout
```

### Repository Endpoints

```
GET    /                          # Dashboard
POST   /repo/create               # Create Repository
GET    /repo/<name>               # View Repository
GET    /repo/<name>/tree/<branch> # View Branch
POST   /repo/<name>/upload        # Upload Files
POST   /repo/<name>/create-file   # Create New File
```

### Branch Endpoints

```
GET    /repo/<name>/branches      # List Branches
POST   /repo/<name>/branches      # Create Branch
GET    /repo/<name>/branch/<branch>/settings  # Branch Settings
```

### Search Endpoints

```
GET    /search                    # Search Interface
GET    /api/search/repositories   # Search Repositories
GET    /api/search/users          # Search Users
```

---

## 🎨 UI/UX

### Design Philosophy
- **GitHub-Inspired** - Familiar Interface For Developers
- **Dark Theme** - Easy On The Eyes With Modern Aesthetics
- **Responsive** - Works Seamlessly Across Devices
- **Accessible** - WCAG Compliant Color Contrasts And Navigation

### Key Components
- **Navigation Bar** - Quick Access To Main Features
- **Repository Cards** - Visual Repository Representation
- **Code Viewer** - Syntax-Highlighted File Viewing
- **Dashboard** - Centralized Repository Management

### Technologies
- **HTML5** - Semantic Markup
- **CSS3** - Modern Styling With Custom Properties
- **JavaScript** - Interactive Functionality
- **Jinja2** - Server-Side Templating

---

## 🛠️ Development

### Project Structure
```
DevBhoomi-GithubClone/
├── BackEnd/           # Python Flask Backend
├── FrontEnd/          # HTML/CSS/JS Frontend
├── Requirements.txt   # Python Dependencies
└── README.md         # This File
```

### Development Setup
```bash
# Install Development Dependencies
pip install -r Requirements.txt

# Run In Development Mode
export FLASK_ENV=development
python BackEnd/App.py
```

### Testing
```bash
# Run Unit Tests
python -m pytest

# Run With Coverage
python -m pytest --cov=BackEnd
```

### Code Style
- **PEP 8** - Python Code Style Guidelines
- **Black** - Code Formatting
- **Flake8** - Linting

---

## 🤝 Contributing

We Welcome Contributions! Please See Our [Contributing Guide](CONTRIBUTING.md) For Details.

### Development Workflow
1. Fork The Repository
2. Create A Feature Branch
3. Make Your Changes
4. Add Tests If Applicable
5. Submit A Pull Request

### Code Of Conduct
Please Read Our [Code Of Conduct](CODE_OF_CONDUCT.md) Before Contributing.

---

## 📄 License

This Project Is Licensed Under The MIT License - See The [LICENSE](LICENSE) File For Details.

```
MIT License

Copyright (c) 2025 DevBhoomi

Permission Is Hereby Granted, Free Of Charge, To Any Person Obtaining A Copy
Of This Software And Associated Documentation Files (The "Software"), To Deal
In The Software Without Restriction, Including Without Limitation The Rights
To Use, Copy, Modify, Merge, Publish, Distribute, Sublicense, And/Or Sell
Copies Of The Software, And To Permit Persons To Whom The Software Is
Furnished To Do So, Subject To The Following Conditions:

The Above Copyright Notice And This Permission Notice Shall Be Included In All
Copies Or Substantial Portions Of The Software.

The Software Is Provided "As Is", Without Warranty Of Any Kind, Express Or
Implied, Including But Not Limited To The Warranties Of Merchantability,
Fitness For A Particular Purpose And Noninfringement. In No Event Shall The
Authors Or Copyright Holders Be Liable For Any Claim, Damages Or Other
Liability, Whether In An Action Of Contract, Tort Or Otherwise, Arising From,
Out Of Or In Connection With The Software Or The Use Or Other Dealings In The
Software.
```

---

## 🙏 Acknowledgments

- **Flask** - The Web Framework That Makes This Possible
- **GitPython** - For Seamless Git Operations
- **SQLAlchemy** - Powerful Database Abstraction
- **GitHub** - Inspiration For The User Interface
- **Open Source Community** - For The Amazing Tools And Libraries

---

## 📞 Support

- **Issues** - [GitHub Issues](https://github.com/i8o8i-Developer/DevBhoomi-GithubClone/issues)
- **Discussions** - [GitHub Discussions](https://github.com/i8o8i-Developer/DevBhoomi-GithubClone/discussions)
- **Documentation** - [Wiki](https://github.com/i8o8i-Developer/DevBhoomi-GithubClone/wiki)

---

```
    ████████╗██╗  ██╗ █████╗ ███╗   ██╗██╗  ██╗███████╗    ██╗   ██╗ ██████╗ ██╗   ██╗
    ╚══██╔══╝██║  ██║██╔══██╗████╗  ██║██║ ██╔╝██╔════╝    ██║   ██║██╔═══██╗██║   ██║
       ██║   ███████║███████║██╔██╗ ██║█████╔╝ ███████╗    ██║   ██║██║   ██║██║   ██║
       ██║   ██╔══██║██╔══██║██║╚██╗██║██╔═██╗ ╚════██║    ╚██╗ ██╔╝██║   ██║██║   ██║
       ██║   ██║  ██║██║  ██║██║ ╚████║██║  ██╗███████║     ╚████╔╝ ╚██████╔╝╚██████╔╝
       ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝      ╚═══╝   ╚═════╝  ╚═════╝
```

**Built With ❤️ By i8o8i WorkStation**</content>