# CI/CD Setup for Pygetpapers

## Overview

This document describes the Continuous Integration and Continuous Deployment (CI/CD) setup for the pygetpapers project, including the new Streamlit UI components.

## CI/CD Architecture

### GitHub Actions Workflows

The project uses GitHub Actions for CI/CD with the following workflows:

1. **`ci.yml`** - Main CI pipeline for all branches
2. **`release.yml`** - Automated releases to PyPI
3. **`streamlit-dev.yml`** - Streamlit UI specific testing

### Workflow Triggers

- **Push to main/v20/develop branches** - Runs full CI pipeline
- **Pull requests to main/v20/develop** - Runs CI checks
- **Release creation** - Triggers PyPI deployment
- **v20 branch updates** - Runs Streamlit-specific tests

## CI Pipeline Jobs

### 1. Test CLI Functionality (`test-cli`)

**Purpose**: Test the core pygetpapers CLI functionality

**Matrix Strategy**: Tests against Python 3.8, 3.9, 3.10, 3.11

**Steps**:
- **Code checkout** - Clone repository
- **Python setup** - Install specified Python version
- **Dependency caching** - Cache pip dependencies for speed
- **Install dependencies** - Install requirements and dev tools
- **Linting** - Run flake8, black, isort checks
- **Testing** - Run pytest with coverage
- **Coverage upload** - Upload to Codecov

**Tools Used**:
- `pytest` - Test runner
- `pytest-cov` - Coverage reporting
- `flake8` - Code linting
- `black` - Code formatting
- `isort` - Import sorting

### 2. Test Streamlit UI (`test-streamlit`)

**Purpose**: Test the Streamlit UI components

**Steps**:
- **Code checkout** - Clone repository
- **Python setup** - Install Python 3.9
- **Dependency caching** - Cache Streamlit-specific dependencies
- **Install dependencies** - Install requirements and Playwright
- **Browser setup** - Install Playwright browsers
- **Import testing** - Test Streamlit app imports
- **Script testing** - Test run script functionality
- **CLI integration** - Test pygetpapers CLI availability

**Tools Used**:
- `pytest-playwright` - Browser testing
- `streamlit` - Web framework
- `plotly` - Data visualization

### 3. Build Package (`build-package`)

**Purpose**: Build Python package for distribution

**Dependencies**: Requires `test-cli` and `test-streamlit` to pass

**Steps**:
- **Code checkout** - Clone repository
- **Python setup** - Install Python 3.9
- **Build tools** - Install build and twine
- **Package build** - Build wheel and source distribution
- **Artifact upload** - Upload build artifacts

**Output**: Python package files in `dist/` directory

### 4. Deploy Documentation (`deploy-docs`)

**Purpose**: Deploy documentation to GitHub Pages

**Dependencies**: Requires `test-cli` and `test-streamlit` to pass
**Trigger**: Only on main branch

**Steps**:
- **Code checkout** - Clone repository
- **Python setup** - Install Python 3.9
- **Dependencies** - Install requirements and Sphinx
- **Documentation build** - Build HTML documentation
- **GitHub Pages deploy** - Deploy to GitHub Pages

**Output**: Documentation available at `https://petermr.github.io/pygetpapers/`

### 5. Security Scan (`security-scan`)

**Purpose**: Security analysis of the codebase

**Steps**:
- **Code checkout** - Clone repository
- **Python setup** - Install Python 3.9
- **Security tools** - Install bandit and safety
- **Bandit scan** - Static security analysis
- **Safety check** - Dependency vulnerability scan
- **Report upload** - Upload security reports

**Tools Used**:
- `bandit` - Static security analysis
- `safety` - Dependency vulnerability scanning

## Streamlit Development Workflow

### Streamlit UI Testing (`test-streamlit-ui`)

**Purpose**: Comprehensive testing of Streamlit UI components

**Steps**:
- **Structure testing** - Verify app structure and imports
- **Integration testing** - Test pygetpapers CLI integration
- **Documentation validation** - Check documentation completeness
- **Port configuration** - Verify port 8502 configuration
- **Code linting** - Basic syntax and style checks

### Streamlit Documentation Build (`build-streamlit-docs`)

**Purpose**: Build Streamlit-specific documentation

**Trigger**: Only on v20 branch

**Steps**:
- **Documentation creation** - Build HTML documentation site
- **Artifact upload** - Upload documentation artifacts

## Release Workflow

### Automated PyPI Deployment (`deploy`)

**Purpose**: Automatically deploy to PyPI when releases are created

**Trigger**: Release publication

**Steps**:
- **Code checkout** - Clone repository
- **Python setup** - Install Python 3.9
- **Build tools** - Install build and twine
- **Package build** - Build distribution files
- **PyPI upload** - Upload to PyPI using API token

**Secrets Required**:
- `PYPI_API_TOKEN` - PyPI API token for authentication

## Configuration Files

### pyproject.toml

The `pyproject.toml` file contains comprehensive configuration for all development tools:

- **Build system** - setuptools configuration
- **Project metadata** - Package information and dependencies
- **Development dependencies** - Testing and development tools
- **Tool configurations** - Black, isort, flake8, pytest, coverage, bandit, mypy

### Test Configuration

- **pytest.ini_options** - Test discovery and execution settings
- **Coverage configuration** - Code coverage reporting
- **Test markers** - Slow, integration, and Streamlit test markers

## Local Development

### Running Tests Locally

```bash
# Install development dependencies
pip install -e ".[dev,test,streamlit]"

# Run all tests
pytest

# Run only Streamlit tests
pytest tests/test_streamlit_ui.py

# Run with coverage
pytest --cov=pygetpapers --cov-report=html

# Run linting
flake8
black --check .
isort --check-only .
```

### Code Quality Tools

```bash
# Format code
black .
isort .

# Security scan
bandit -r pygetpapers/
safety check

# Type checking
mypy pygetpapers/
```

### Streamlit Development

```bash
# Run Streamlit app locally
python run_streamlit.py

# Or directly with streamlit
streamlit run streamlit_app.py --server.port 8502
```

## CI/CD Best Practices

### Branch Strategy

- **main** - Production-ready code
- **v20** - Streamlit UI development branch
- **develop** - Development branch for features
- **feature branches** - Individual feature development

### Commit Standards

- Use conventional commit messages
- Include issue numbers in commit messages
- Keep commits focused and atomic
- Test locally before pushing

### Pull Request Process

1. Create feature branch from appropriate base
2. Make changes and test locally
3. Push branch and create pull request
4. CI checks run automatically
5. Address any CI failures
6. Request review from maintainers
7. Merge after approval

### Release Process

1. Create release branch from main
2. Update version in pyproject.toml
3. Update CHANGELOG.md
4. Create pull request
5. After merge, create GitHub release
6. CI automatically deploys to PyPI

## Monitoring and Maintenance

### CI/CD Metrics

- **Build success rate** - Track CI pipeline success
- **Test coverage** - Monitor code coverage trends
- **Security vulnerabilities** - Regular security scans
- **Deployment frequency** - Track release frequency

### Maintenance Tasks

- **Dependency updates** - Regular security updates
- **Tool updates** - Keep CI tools current
- **Configuration review** - Periodic configuration audits
- **Performance optimization** - Monitor CI execution times

## Troubleshooting

### Common CI Issues

**Build Failures**:
- Check dependency conflicts
- Verify Python version compatibility
- Review test failures

**Test Failures**:
- Run tests locally to reproduce
- Check for environment-specific issues
- Review test data and mocks

**Deployment Issues**:
- Verify PyPI API token
- Check package metadata
- Review build artifacts

### Local Development Issues

**Streamlit Issues**:
- Check port availability (8502)
- Verify dependency installation
- Review browser compatibility

**Test Issues**:
- Clear pytest cache: `pytest --cache-clear`
- Check test markers: `pytest --markers`
- Verify test data

## Future Enhancements

### Planned CI/CD Improvements

1. **Automated dependency updates** - Dependabot integration
2. **Performance testing** - Load testing for Streamlit UI
3. **Browser testing** - Automated UI testing with Playwright
4. **Security scanning** - Enhanced security analysis
5. **Documentation automation** - Auto-generated API docs

### Monitoring Enhancements

1. **CI/CD dashboards** - Visual monitoring of pipeline health
2. **Alert integration** - Slack/email notifications for failures
3. **Performance tracking** - CI execution time monitoring
4. **Quality gates** - Automated quality checks

This CI/CD setup ensures that pygetpapers maintains high quality standards while enabling rapid development and deployment of new features, including the Streamlit UI enhancement. 