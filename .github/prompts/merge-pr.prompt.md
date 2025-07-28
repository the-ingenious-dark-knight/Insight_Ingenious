---
mode: agent
tools: ['runCommands', 'changes', 'codebase', 'editFiles']
model: Claude Sonnet 4
---
# Prompt: Merge Pull Request with Conflict Resolution and Testing

## Instructions

1. **List available pull requests and ask user to select one**
    ```sh
    gh pr list --state open
    ```
    
    After showing the available PRs, **pause and ask the user which PR number they want to merge for this session.**
    
    Wait for the user's response before proceeding with any merge operations.

2. **View details of the selected pull request**
    ```sh
    gh pr view <pr-number>
    ```

3. **Checkout the pull request branch locally**
    ```sh
    gh pr checkout <pr-number>
    ```

4. **Merge the PR into your current branch**
    Choose one of the following merge strategies:

    **Option A: Create merge commit (preserves PR history)**
    ```sh
    git merge --no-ff <pr-branch-name>
    ```

    **Option B: Squash and merge (cleaner history)**
    ```sh
    git merge --squash <pr-branch-name>
    git commit -m "Merge PR #<pr-number>: <pr-title>"
    ```

    **Option C: Rebase and merge (linear history)**
    ```sh
    git rebase <pr-branch-name>
    ```

5. **If merge conflicts occur:**
    - Identify conflicted files: `git status`
    - View conflicts in detail: `git diff`
    - Open each conflicted file and resolve conflicts manually
    - Look for conflict markers: `<<<<<<<`, `=======`, `>>>>>>>`
    - Edit files to resolve conflicts, keeping the desired changes
    - Stage resolved files: `git add <resolved-file>`
    - Continue the merge process:
        - For merge: `git commit` (if not already committed)
        - For rebase: `git rebase --continue`
        - For squash: Complete with `git commit`

6. **Verify the merge was successful**
    ```sh
    git status
    git log --oneline -10
    ```

7. **Run comprehensive tests**
    ```sh
    uv run pytest
    uv run pre-commit run --all-files
    ```

8. **If tests pass, push the updated branch**
    ```sh
    git push origin <current-branch-name>
    ```

9. **Clean up (optional)**
    ```sh
    # Delete the local PR branch if no longer needed
    git branch -d <pr-branch-name>
    
    # If the PR was merged successfully, you can close it on GitHub
    gh pr close <pr-number>
    ```

## Conflict Resolution Tips

- **Understanding conflict markers:**
    - `<<<<<<< HEAD` - Your current branch changes
    - `=======` - Separator between conflicting changes
    - `>>>>>>> <pr-branch>` - Pull request branch changes

- **Common resolution strategies:**
    - **Accept both changes**: Combine the changes logically
    - **Accept current branch**: Keep your current implementation
    - **Accept PR changes**: Adopt the pull request's implementation
    - **Create hybrid solution**: Write new code that incorporates the best of both

- **Useful commands for conflict resolution:**
    - `git diff` - See current conflicts
    - `git diff --ours` - See your changes only
    - `git diff --theirs` - See PR changes only
    - `git checkout --ours <file>` - Accept your version of a file
    - `git checkout --theirs <file>` - Accept PR version of a file

## GitHub CLI Advanced Options

- **List PRs with more details:**
    ```sh
    gh pr list --json number,title,author,headRefName
    ```

- **View PR diff:**
    ```sh
    gh pr diff <pr-number>
    ```

- **Check PR status:**
    ```sh
    gh pr checks <pr-number>
    ```

- **Merge PR directly via GitHub CLI (alternative to manual merge):**
    ```sh
    # Merge with merge commit
    gh pr merge <pr-number> --merge
    
    # Squash and merge
    gh pr merge <pr-number> --squash
    
    # Rebase and merge
    gh pr merge <pr-number> --rebase
    ```

## Example Workflow

```sh
# List available PRs
gh pr list --state open

# View PR details (replace 123 with actual PR number)
gh pr view 123

# Checkout the PR locally
gh pr checkout 123

# Merge with merge commit strategy
git merge --no-ff pr-branch-name

# If conflicts occur, resolve them manually then:
git add .
git commit -m "Resolve merge conflicts for PR #123"

# Run tests
uv run pytest
uv run pre-commit run --all-files

# If tests pass, push the changes
git push origin current-branch-name

# Clean up
git branch -d pr-branch-name
```

## Troubleshooting

- **If you need to abort a merge:**
    ```sh
    git merge --abort
    ```

- **If you need to abort a rebase:**
    ```sh
    git rebase --abort
    ```

- **If tests fail after merge:**
    - Fix the failing tests
    - Run tests again: `uv run pytest`
    - Commit fixes: `git add . && git commit -m "Fix tests after merge"`
    - Push: `git push origin <current-branch-name>`

- **If pre-commit hooks fail:**
    - Fix formatting/linting issues
    - Run: `uv run pre-commit run --all-files`
    - Commit fixes: `git add . && git commit -m "Fix linting after merge"`
    - Push: `git push origin <current-branch-name>`