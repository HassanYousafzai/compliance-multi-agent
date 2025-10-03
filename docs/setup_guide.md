# Setup and Installation Guide

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

## Installation Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd compliance-multi-agent
2. Create Virtual Environment (Recommended)
bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
3. Install Dependencies
bash
pip install -r requirements.txt
4. Verify Installation
bash
python run_system.py --help
Running the System
Basic Usage
bash
# Run with example queries
python run_system.py examples

# Run interactive mode
python run_system.py interactive

# Run comprehensive demo
python run_system.py demo
Programmatic Usage
python
from src.main import EnhancedComplianceAwareAgentSystem

# Initialize system
system = EnhancedComplianceAwareAgentSystem()

# Process a query
result = system.process_query("What's the weather in London?")

# Get system analytics
analytics = system.get_system_analytics()
Testing
Run All Tests
bash
python -m pytest tests/ -v
Run Specific Test Suite
bash
python tests/test_enhanced_system.py
python tests/test_integration.py
Configuration
Database Configuration
The system uses SQLite by default. Database file is created automatically at:

Default: agent_memory.db

Can be specified: EnhancedComplianceAwareAgentSystem("custom_path.db")

Compliance Regulations
Default regulations: HIPAA, GDPR

python
# Custom regulations
result = system.process_query(query, regulations=['hipaa', 'gdpr', 'data_retention'])
File Structure
text
compliance-multi-agent/
├── src/                 # Source code
├── tests/              # Test suites
├── examples/           # Demonstration scripts
├── docs/              # Documentation
├── requirements.txt   # Dependencies
└── run_system.py     # Main entry point
text

### **Create Git Configuration**

Open `.gitignore`:

```gitignore
# .gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Database
*.db
*.sqlite
*.sqlite3

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Testing
.coverage
htmlcov/
.pytest_cache/