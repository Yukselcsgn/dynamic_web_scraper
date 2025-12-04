# Contributor Guide - Dynamic Web Scraper

Welcome! This guide helps new contributors get started with the Dynamic Web Scraper project.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Ways to Contribute](#ways-to-contribute)
3. [Setting Up Your Environment](#setting-up-your-environment)
4. [Making Your First Contribution](#making-your-first-contribution)
5. [Contribution Workflow](#contribution-workflow)
6. [Code Review Process](#code-review-process)
7. [Community Guidelines](#community-guidelines)
8. [Getting Help](#getting-help)

## Getting Started

### What is the Dynamic Web Scraper?

A powerful, enterprise-grade Python platform for web scraping with:
- Automatic site detection
- Anti-bot evasion
- Data analytics
- Distributed processing
- And much more!

### Why Contribute?

- 🌟 **Learn new skills** - Web scraping, Python, distributed systems
- 🤝 **Build your portfolio** - Real-world open source experience
- 🎯 **Make an impact** - Help thousands of users
- 👥 **Join the community** - Connect with developers worldwide

## Ways to Contribute

### 1. 🐛 Report Bugs

Found a bug? Help us fix it!

**Steps:**
1. Check if it's already reported in [Issues](https://github.com/Yukselcsgn/dynamic_web_scraper/issues)
2. Create a new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - System information
   - Error messages/logs

**Example**:
```
Title: Scraper fails on sites with JavaScript

Description:
When scraping https://example.com, the scraper returns no data.

Steps to reproduce:
1. Run: python scraper/main.py
2. Enter URL: https://example.com
3. See no data extracted

Expected: Data extracted successfully
Actual: Empty result

System: Windows 10, Python 3.9.7
Error: [Paste error here]
```

### 2. 💡 Suggest Features

Have an idea? We'd love to hear it!

**Good feature requests include:**
- Clear description of the feature
- Use case/problem it solves
- Proposed solution
- Alternative approaches considered

### 3. 📝 Improve Documentation

Documentation is crucial! Help by:
- Fixing typos
- Clarifying confusing sections
- Adding examples
- Writing tutorials
- Translating documentation

**Easy wins:**
- Fix broken links
- Update outdated information
- Add missing docstrings
- Improve README clarity

### 4. 🔧 Fix Bugs

Check the [Issues](https://github.com/Yukselcsgn/dynamic_web_scraper/issues) for bugs to fix.

**Look for:**
- `good first issue` label (great for beginners)
- `help wanted` label (we need help!)
- `bug` label (confirmed bugs)

### 5. ✨ Add Features

Ready to add new functionality?

**Popular feature areas:**
- New site adaptations
- Analytics enhancements
- Performance optimizations
- Export formats
- Plugin development

## Setting Up Your Environment

### 1. Fork the Repository

Click "Fork" on [GitHub](https://github.com/Yukselcsgn/dynamic_web_scraper)

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/dynamic_web_scraper.git
cd dynamic_web_scraper
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/Yukselcsgn/dynamic_web_scraper.git
```

### 4. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 5. Install Dependencies

```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### 6. Verify Setup

```bash
# Run tests
pytest

# Check code style
flake8 scraper/

# Verify everything works
python setup_and_test.py
```

## Making Your First Contribution

###  Finding an Issue

1. Browse [Issues](https://github.com/Yukselcsgn/dynamic_web_scraper/issues)
2. Filter by `good first issue`
3. Comment "I'd like to work on this"
4. Wait for maintainer approval

### Creating Your Fix

```bash
# Create feature branch
git checkout -b fix/issue-number-description

# Make your changes
# ... edit files ...

# Run tests
pytest

# Format code
black scraper/

# Commit changes
git add .
git commit -m "Fix: Description of fix (#issue-number)"

# Push to your fork
git push origin fix/issue-number-description
```

### Opening a Pull Request

1. Go to your fork on GitHub
2. Click "Pull Request"
3. Fill out the template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Other (describe)

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Updated docs if needed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] No new warnings
```

## Contribution Workflow

### Standard Workflow

```bash
# 1. Sync with upstream
git checkout main
git pull upstream main

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes
# ... edit files ...

# 4. Test changes
pytest
black scraper/
flake8 scraper/

# 5. Commit changes
git add .
git commit -m "Add: Feature description"

# 6. Push to fork
git push origin feature/my-feature

# 7. Create Pull Request
# ... on GitHub ...
```

### Keeping Your Fork Updated

```bash
# Fetch upstream changes
git fetch upstream

# Merge into main
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

## Code Review Process

### What to Expect

1. **Automated Checks** run first (tests, linting)
2. **Maintainer Review** typically within 2-3 days
3. **Feedback** - Address comments and push updates
4. **Approval** - Once approved, we'll merge!

### Responding to Feedback

```bash
# Make requested changes
# ... edit files ...

# Commit changes
git add .
git commit -m "Address review feedback"

# Push updates
git push origin feature/my-feature
```

### If Your PR Gets Stuck

- Ask for clarification in comments
- Reach out in GitHub Discussions
- Be patient - maintainers are volunteers!

## Community Guidelines

### Code of Conduct

We follow these principles:

✅ **Do:**
- Be respectful and inclusive
- Provide constructive feedback
- Help others learn
- Celebrate successes
- Ask questions

❌ **Don't:**
- Use offensive language
- Harass others
- Spam issues/PRs
- Demand immediate responses

### Communication

- **GitHub Issues** - Bug reports, feature requests
- **Pull Requests** - Code contributions
- **Discussions** - Questions, ideas, general chat
- **Email** - Private/sensitive matters

### Recognition

Contributors are recognized:
- In the README
- In CHANGELOG
- On the contributors page
- In release notes

## Getting Help

### Resources

- 📖 **Documentation** - [docs/](../docs/)
- 🏗️ **Architecture** - [architecture/overview.md](architecture/overview.md)
- 🔧 **Developer Guide** - [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- 📝 **Full Contributing Guide** - [CONTRIBUTING.md](../CONTRIBUTING.md)

### Ask Questions

- 💬 **GitHub Discussions** - General questions
- 🐛 **Issues** - Bug-related questions
- 📧 **Email** - Private matters

### Common Questions

**Q: I'm new to open source. Where do I start?**
A: Check out `good first issue` labels and don't hesitate to ask questions!

**Q: How long does review take?**
A: Usually 2-3 days, but can vary. Be patient!

**Q: My PR was rejected. What now?**
A: Don't be discouraged! Ask for feedback and try again.

**Q: Can I work on multiple issues?**
A: Start with one, then take on more as you're comfortable.

**Q: I made a mistake in my PR. Help!**
A: No problem! Just push fixes to your branch.

## Quick Reference

### Commit Messages

```bash
# Format
<Type>: <Description> (#issue)

# Types
Add:    New feature
Fix:    Bug fix
Docs:   Documentation
Style:  Formatting
Refactor: Code restructuring
Test:   Adding tests
Chore:  Maintenance

# Examples
Add: Support for new export format (#123)
Fix: Price extraction on Amazon (#456)
Docs: Update installation instructions
```

### Branch Naming

```bash
feature/description    # New features
fix/description        # Bug fixes
docs/description       # Documentation
refactor/description   # Code refactoring
```

### Running Checks

```bash
# Format code
black scraper/

# Lint code
flake8 scraper/

# Type check
mypy scraper/

# Run tests
pytest

# All checks
pre-commit run --all-files
```

## Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort! 🙏

### Next Steps

1. ⭐ Star the repository
2. 🍴 Fork the project
3. 🐛 Find a `good first issue`
4. 💻 Make your first contribution
5. 🎉 Join the community!

---

**Questions?** Open a [Discussion](https://github.com/Yukselcsgn/dynamic_web_scraper/discussions) or check [CONTRIBUTING.md](../CONTRIBUTING.md)

**Ready to contribute?** Check out the [issues](https://github.com/Yukselcsgn/dynamic_web_scraper/issues) and get started! 🚀
