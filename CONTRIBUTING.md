# Contributing to Cloud Deployment Dashboard

Thank you for your interest in contributing to the Cloud Deployment Dashboard! This document provides guidelines and information for contributors.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker Desktop
- Azure CLI
- Git
- Node.js (for frontend dependencies)

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd cloud-deployment-dashboard
   ```

2. **Set up Python virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

## 📋 Development Guidelines

### Code Style
- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ES6+ features, consistent indentation
- **HTML/CSS**: Use semantic HTML, BEM methodology for CSS
- **Comments**: Write clear, concise comments for complex logic

### Git Workflow
1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes with clear commits:**
   ```bash
   git commit -m "feat: add new deployment monitoring feature"
   ```

3. **Push and create a Pull Request:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention
Use conventional commits format:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_app.py

# Run with verbose output
pytest -v
```

### Writing Tests
- Write tests for all new features
- Maintain test coverage above 80%
- Use descriptive test names
- Mock external dependencies (Supabase, Azure services)

### Test Structure
```python
def test_feature_description():
    """Test that feature works as expected."""
    # Arrange
    setup_test_data()
    
    # Act
    result = perform_action()
    
    # Assert
    assert result == expected_value
```

## 🐳 Docker Development

### Building Images
```bash
# Development build
docker build -t cloud-dashboard:dev .

# Production build (Azure-optimized)
docker build -f Dockerfile.azure -t cloud-dashboard:prod .
```

### Running Containers
```bash
# Development container
docker run -p 8000:8000 --env-file .env cloud-dashboard:dev

# Production container
docker run -p 8000:8000 --env-file .env.production cloud-dashboard:prod
```

## 🔧 Azure Development

### Local Azure Testing
```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "your-subscription-id"

# Test Azure CLI commands
az webapp list --resource-group your-rg
```

### Container Registry Testing
```bash
# Build and push to ACR
az acr build --registry your-acr --image cloud-dashboard:latest .

# Test container locally
docker run -p 8000:8000 your-acr.azurecr.io/cloud-dashboard:latest
```

## 📚 Documentation

### Code Documentation
- Use docstrings for all functions and classes
- Include parameter types and return values
- Provide usage examples for complex functions

### API Documentation
- Document all endpoints with request/response examples
- Include error codes and handling
- Update OpenAPI/Swagger documentation

## 🚀 Deployment

### Staging Deployment
```bash
# Deploy to staging
./azure-container-deployment.ps1 -Environment staging

# Run smoke tests
pytest tests/integration/
```

### Production Deployment
- All changes must pass through staging first
- Require code review from at least one maintainer
- Run full test suite before deployment
- Monitor deployment metrics post-release

## 🐛 Bug Reports

### Before Submitting
1. Check existing issues for duplicates
2. Test with the latest version
3. Reproduce the issue consistently

### Bug Report Template
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g. Windows 11]
- Python version: [e.g. 3.11.5]
- Browser: [e.g. Chrome 118]
- Docker version: [e.g. 24.0.6]

**Additional context**
Add any other context about the problem here.
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Describe alternatives you've considered**
Alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request.
```

## 🏗️ Architecture Guidelines

### Project Structure
```
├── app.py                 # Main Flask application
├── static/               # Static assets (CSS, JS, images)
├── templates/            # Jinja2 templates
├── tests/               # Test suite
├── azure/               # Azure-specific configurations
├── .github/workflows/   # CI/CD pipelines
└── docs/               # Documentation
```

### Adding New Features
1. **Plan the feature** with architectural considerations
2. **Create tests** before implementation (TDD)
3. **Implement** with proper error handling
4. **Document** the feature and API changes
5. **Update** deployment scripts if needed

## 🤝 Code Review Process

### For Contributors
- Keep PRs focused and small
- Write clear PR descriptions
- Respond to feedback promptly
- Update documentation as needed

### For Reviewers
- Review within 48 hours
- Provide constructive feedback
- Test the changes locally
- Check for security implications

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Email**: [maintainer-email] for security issues

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Cloud Deployment Dashboard! 🎉