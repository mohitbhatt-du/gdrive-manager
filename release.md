# PROJECT: GDRIVE MANAGER — WINDOWS PROFESSIONAL REPOSITORY & BRANDING

## ROLE

Act as a Senior Windows Desktop Software Engineer, Open-Source Maintainer, DevOps Engineer, QA Engineer, Release Engineer and Brand Designer.

I have already developed a working Python desktop application named GDrive Manager.

Your task is to transform the existing project into a professional, maintainable, well-documented Windows desktop software repository suitable for public GitHub distribution.

This is an existing application. Do not rebuild it from scratch.

Preserve existing working functionality and improve the repository, documentation, branding, testing, Windows packaging and release automation.

The application is Windows-only.

Do not spend time implementing Linux support or Linux builds.

---

# 1. INITIAL REPOSITORY AUDIT

Before modifying anything:

1. Inspect the complete repository.
2. Understand the existing application architecture.
3. Identify the application entry point.
4. Inspect dependencies.
5. Inspect GUI implementation.
6. Inspect Google Drive authentication.
7. Inspect rclone integration.
8. Inspect WinFsp integration.
9. Inspect configuration and credential storage.
10. Inspect existing tests and GitHub workflows.

Identify:

- Bugs and technical debt.
- Missing documentation.
- Missing tests.
- Unused dependencies.
- Hardcoded paths.
- Security weaknesses.
- Packaging problems.
- Missing application metadata.
- Windows compatibility issues.

Create REPOSITORY_AUDIT.md.

Do not modify the existing application until the audit is complete.

Do not assume that features are implemented merely because they are described in previous specifications.

---

# 2. BRAND IDENTITY AND VISUAL ASSETS

Create a professional visual identity for GDrive Manager.

This is an important requirement, not an optional enhancement.

The application should look like a polished commercial Windows desktop utility.

## Brand direction

Product name: GDrive Manager

Visual identity:

- Dark navy.
- Deep charcoal.
- Violet and purple accents.
- Modern geometric design.
- Clean typography.
- Minimal and recognizable iconography.
- Professional cloud-storage aesthetic.

Create an original brand identity.

Do not directly copy Google's official logo or create an icon that could be mistaken for an official Google product.

## 2.1 Application icon

Create a custom application icon.

The icon should communicate:

- Cloud storage.
- Multiple drives.
- File management.
- Connectivity.
- Organization.

Design requirements:

- Minimal geometric symbol.
- Recognizable at small sizes.
- Strong contrast.
- Modern Windows application aesthetic.
- Consistent with the dark application theme.

Create the following assets:

assets/branding/
    logo.svg
    logo.png
    icon.svg
    icon.png
    icon.ico
    icon-16.png
    icon-32.png
    icon-48.png
    icon-64.png
    icon-128.png
    icon-256.png

The Windows ICO file must contain appropriate multiple resolutions.

Use a genuine vector source where possible.

Export assets from the vector source rather than creating unrelated versions independently.

Use Pillow or another appropriate tool to generate raster sizes.

Ensure the application icon is actually used in:

- Windows executable.
- Application window.
- Taskbar.
- Installer.
- README.

Do not use an emoji as the application icon.

## 2.2 Marketing banner

Create a professional GitHub marketing banner.

Required file:

assets/branding/github-banner.png

Dimensions:

1280 × 640 pixels.

Design:

- Dark navy background.
- Purple/violet gradient accents.
- Large GDrive Manager branding.
- Original application icon.
- Elegant desktop application mockup or screenshot composition.
- Clean typography.
- Professional spacing.

Include a concise product tagline:

"Your Google Drives. One Desktop."

Include a short feature summary:

"Multi-Account • Cloud Streaming • Offline Sync"

The banner should communicate the product immediately.

Do not make the banner look like a generic AI-generated poster.

Do not overcrowd it with text.

Use actual application screenshots if available.

If actual screenshots are unavailable, create a clearly illustrative interface composition. Do not present a mockup as a real screenshot.

## 2.3 README branding

Use the banner near the top of README.md.

Add the application logo and appropriate GitHub badges.

Ensure the design looks professional in both light and dark GitHub themes.

## 2.4 GitHub social preview

Prepare a dedicated social preview image:

assets/branding/social-preview.png

Recommended dimensions: 1280 × 640 pixels.

It should remain visually readable when displayed as a small repository preview.

---

# 3. PROFESSIONAL REPOSITORY STRUCTURE

Improve the existing structure without breaking working imports.

Use a structure similar to:

gdrive-manager/
│
├── .github/
│   ├── workflows/
│   │   ├── ci.yml
│   │   ├── build-windows.yml
│   │   ├── release.yml
│   │   └── security.yml
│   │
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   └── feature_request.yml
│   │
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── dependabot.yml
│
├── app/
│   └── Existing application source
│
├── assets/
│   ├── branding/
│   ├── icons/
│   ├── images/
│   └── fonts/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── fixtures/
│   └── conftest.py
│
├── docs/
│   ├── installation.md
│   ├── architecture.md
│   ├── configuration.md
│   ├── troubleshooting.md
│   ├── development.md
│   └── security.md
│
├── scripts/
│   ├── build.py
│   ├── check_environment.py
│   └── generate_version.py
│
├── packaging/
│   └── windows/
│
├── main.py
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── LICENSE
├── .gitignore
├── .editorconfig
├── .gitattributes
├── .pre-commit-config.yaml
└── DEVELOPMENT_STATUS.md

This is a suggested structure.

Do not create unnecessary directories or empty files.

---

# 4. PROFESSIONAL README.md

Create a detailed and visually polished README.

It must include:

1. Marketing banner.
2. Project title and description.
3. GitHub badges.
4. Actual application screenshots.
5. Introduction.
6. Key features.
7. Supported Windows versions.
8. System requirements.
9. Download instructions.
10. Installation instructions.
11. Google OAuth setup.
12. Usage guide.
13. Streaming mode.
14. Offline mode.
15. Hybrid mode.
16. Synchronization.
17. Configuration.
18. Architecture diagram.
19. Development setup.
20. Running tests.
21. Building locally.
22. Troubleshooting.
23. Roadmap.
24. Contributing.
25. Security.
26. License.

Use accurate information from the actual codebase.

Do not advertise unimplemented features.

Include links to official rclone, WinFsp and Google Drive documentation.

Use a Mermaid architecture diagram.

Example:

GUI
  |
Python Application Backend
  |
Account Manager / Mount Manager / Sync Manager
  |
rclone
  |
Google Drive

Windows filesystem integration:

rclone mount
  |
WinFsp
  |
Windows File Explorer

Make the README suitable for a public open-source repository.

---

# 5. TESTING AND QUALITY ASSURANCE

Use pytest.

Create a professional test suite.

Test:

- Configuration.
- Account management.
- Duplicate account handling.
- Drive-letter validation.
- OAuth workflow abstractions.
- rclone command generation.
- Mount lifecycle.
- Process management.
- Transfer progress parsing.
- Synchronization safety.
- File path validation.
- Error handling.

Use mocks for Google API and rclone subprocess operations.

Do not require real Google accounts for unit testing.

Never perform destructive operations on real user data during automated tests.

Use pytest-cov.

Target at least 80% coverage for testable business logic as a gradual quality objective.

Do not write meaningless tests to inflate coverage.

Separate integration tests from unit tests.

---

# 6. CODE QUALITY

Configure:

- Ruff.
- Pytest.
- Pytest-cov.
- Mypy where practical.
- Pre-commit.

Use pyproject.toml as the primary project configuration.

Implement:

- Consistent formatting.
- Type hints.
- Docstrings.
- Clear naming.
- Proper exception handling.
- Modular architecture.

Avoid unnecessary abstractions.

Do not introduce lint suppressions without justification.

---

# 7. WINDOWS-ONLY CONTINUOUS INTEGRATION

Create:

.github/workflows/ci.yml

Use GitHub Actions with Windows runners.

Supported initial target:

Windows 10 and Windows 11, x86_64.

CI should run on:

- Push to main.
- Push to develop.
- Pull requests.
- Manual workflow dispatch.

Use Windows GitHub-hosted runners.

CI steps:

1. Checkout repository.
2. Install supported Python version.
3. Cache pip dependencies.
4. Install requirements.
5. Install development requirements.
6. Compile Python source.
7. Run Ruff lint.
8. Check Ruff formatting.
9. Run Mypy where configured.
10. Run pytest.
11. Generate coverage report.
12. Upload coverage artifacts.

Do not require real Google credentials.

Do not attempt privileged WinFsp mounts during ordinary CI.

Use mocked external services.

Use least-privilege GitHub Actions permissions.

---

# 8. WINDOWS BUILD AUTOMATION

Create:

.github/workflows/build-windows.yml

Use a Windows GitHub Actions runner.

Use PyInstaller unless the current application requires a different packaging strategy.

Build target:

Windows x86_64.

Prefer an onedir distribution initially.

The build must include:

- Application source.
- Required Python dependencies.
- Custom application icon.
- GUI assets.
- Fonts if required.
- Configuration templates.
- Required resource files.

Use the correct ICO file:

assets/branding/icon.ico

Generate:

dist/GDriveManager/

Contents should include:

- GDriveManager.exe
- Required runtime files.
- Assets.
- Other required resources.

Also produce:

GDriveManager-Windows-x64.zip

Requirements:

- Correct application version.
- No development dependencies.
- No unnecessary source files.
- No credentials.
- No local user data.
- No test files.

Verify that the generated executable starts successfully.

Check hidden imports and bundled resources.

Do not assume that rclone or WinFsp can be redistributed without checking their licensing and distribution requirements.

Prefer dependency detection and clear installation instructions.

---

# 9. WINDOWS INSTALLER

After the portable package works, implement a Windows installer.

Preferred technology:

Inno Setup.

Create:

packaging/windows/installer.iss

Installer requirements:

- Application installation directory.
- Start menu shortcut.
- Optional desktop shortcut.
- Application icon.
- Uninstaller.
- Version information.
- Dependency checks.
- Installation documentation.

Do not silently install external drivers or privileged dependencies.

Inform the user when WinFsp is required.

Allow users to choose the installation directory.

Generate:

GDriveManager-Setup-x64.exe

The portable ZIP and installer must both be available as separate release assets.

---

# 10. AUTOMATED GITHUB RELEASES

Create:

.github/workflows/release.yml

Use semantic versioning.

Examples:

v1.0.0
v1.0.1
v1.1.0
v2.0.0

Trigger release builds using version tags.

Workflow:

1. Checkout repository.
2. Verify version.
3. Run quality checks.
4. Run tests.
5. Build Windows distribution.
6. Verify executable.
7. Build portable ZIP.
8. Build installer.
9. Generate SHA256 checksums.
10. Generate release notes.
11. Publish GitHub Release.
12. Upload all artifacts.

Expected release assets:

GDriveManager-Windows-x64.zip

GDriveManager-Setup-x64.exe

SHA256SUMS.txt

Release notes should contain:

- Version.
- Release date.
- New features.
- Improvements.
- Bug fixes.
- Known issues.
- System requirements.
- Installation instructions.

Use GITHUB_TOKEN with minimum required permissions.

Do not publish releases from ordinary pull requests.

Do not overwrite existing releases accidentally.

---

# 11. VERSION MANAGEMENT

Use semantic versioning.

Maintain a single authoritative version source where practical.

The version must be available inside the Python application.

The executable must display the correct version.

The release workflow must validate that the Git tag and project version match.

Example:

Application version: 1.0.0

Git tag: v1.0.0

Release name: GDrive Manager v1.0.0

---

# 12. SECURITY

Create SECURITY.md.

Document:

- Vulnerability reporting.
- Credential handling.
- OAuth token security.
- Supported versions.
- Security update policy.

Add pip-audit to the security workflow.

Configure Dependabot for:

- Python dependencies.
- GitHub Actions.

Exclude:

- OAuth credentials.
- Tokens.
- Local configuration.
- Logs.
- Cache.
- Build artifacts.
- Executables.

Do not expose credentials in logs or CI artifacts.

---

# 13. OPEN-SOURCE REPOSITORY STANDARDS

Create:

CONTRIBUTING.md

CODE_OF_CONDUCT.md

CHANGELOG.md

SECURITY.md

Create GitHub issue templates:

- Bug report.
- Feature request.

Create a pull request template.

Use conventional commit examples:

feat: add offline sync

fix: resolve mount failure

docs: improve installation guide

test: add transfer manager tests

refactor: improve account manager

chore: update dependencies

Do not invent maintainer details or contact information.

Do not select a license without approval if the project has no existing license.

---

# 14. WINDOWS COMPATIBILITY AND PACKAGING

The application officially targets Windows.

Verify:

- Windows path handling.
- Drive-letter detection.
- WinFsp dependency.
- rclone executable discovery.
- Windows subprocess handling.
- Credential storage.
- Application startup.
- GUI icon.
- Resource loading.
- Executable packaging.

Test on Windows 10 and Windows 11 where practical.

Document any features requiring administrator privileges.

Do not require administrator privileges unnecessarily.

Do not claim support for a Windows version that has not been verified.

---

# 15. REQUIRED FINAL REPOSITORY DELIVERABLES

The final repository must include:

[ ] Professional README.

[ ] Custom application logo.

[ ] Multi-resolution Windows ICO.

[ ] Marketing banner.

[ ] GitHub social preview image.

[ ] Actual application screenshots or clearly identified mockups.

[ ] Repository audit.

[ ] Installation documentation.

[ ] Architecture documentation.

[ ] Troubleshooting documentation.

[ ] CONTRIBUTING.md.

[ ] CODE_OF_CONDUCT.md.

[ ] SECURITY.md.

[ ] CHANGELOG.md.

[ ] pytest test suite.

[ ] Coverage configuration.

[ ] Ruff configuration.

[ ] Mypy configuration where practical.

[ ] Pre-commit configuration.

[ ] GitHub Actions CI.

[ ] Windows build workflow.

[ ] Automated GitHub Release workflow.

[ ] SHA256 checksum generation.

[ ] Dependabot configuration.

[ ] Windows portable ZIP.

[ ] Windows installer EXE.

---

# 16. EXECUTION RULES

Follow this exact sequence:

PHASE 1: Audit the existing project.

PHASE 2: Propose repository improvements.

PHASE 3: Create brand identity and image assets.

PHASE 4: Improve repository structure.

PHASE 5: Create README and technical documentation.

PHASE 6: Improve tests and quality checks.

PHASE 7: Configure GitHub Actions CI.

PHASE 8: Implement Windows executable builds.

PHASE 9: Implement Windows installer generation.

PHASE 10: Implement automated GitHub Releases.

PHASE 11: Run final verification.

After each phase:

- Run relevant checks.
- Fix problems.
- Preserve working functionality.
- Update DEVELOPMENT_STATUS.md.
- Report completed and pending work.

Never claim an artifact or build has been verified if it has not been tested.

Never fabricate screenshots.

Never include credentials.

Never rewrite Git history.

Never force-push.

Never publish an unverified release.

Never delete existing user data.

Never change the project's license without approval.

Do not stop after creating YAML files or documentation. Validate the actual implementation.

Start with the repository audit.

The final objective is a professional, secure, attractive, maintainable and distributable Windows desktop application with a polished brand identity and automated GitHub releases.