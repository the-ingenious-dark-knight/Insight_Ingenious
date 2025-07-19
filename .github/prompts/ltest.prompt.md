---
mode: agent
tools: ['changes', 'codebase', 'editFiles', 'extensions', 'fetch', 'findTestFiles', 'githubRepo', 'new', 'openSimpleBrowser', 'problems', 'runCommands', 'runNotebooks', 'runTasks', 'runTests', 'search', 'searchResults', 'terminalLastCommand', 'terminalSelection', 'testFailure', 'usages', 'vscodeAPI', 'websearch']
model: Claude Sonnet 4
---
Run `uv run pytest` and `uv run pre-commit run --all-files` and debug iteratively until there are no more test, formatting, or linting errors. Do not implement any slow tests or remove slow tests if you encounter them.
