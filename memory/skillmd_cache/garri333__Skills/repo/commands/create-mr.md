# Create Branch and Merge Request

Create a branch, commit changes, and open a merge request or pull request for new PrivaLex content.

## Instructions

### Step 1: Check Prerequisites

```bash
# Check current git status
git status
git branch --show-current

# Check if gh CLI is available (GitHub)
which gh || echo "gh not found"

# Check if glab CLI is available (GitLab)
which glab || echo "glab not found"
```

### Step 2: Handle Changes

Based on git status:

1. **If on main with uncommitted changes**: Create a new branch
2. **If already on a feature branch**: Continue with existing branch
3. **If there are conflicts**: Help resolve them before proceeding

### Step 3: Create Branch (if needed)

Generate a branch name from the content type and topic:

```bash
# Naming convention: content/<type>/<topic-slug>
# Examples:
# content/blog/iso-27001-certification-guide
# content/linkedin/nis2-training-requirements
# content/newsletter/february-2026-update

git checkout -b content/<type>/<topic-slug>
```

### Step 4: Stage and Commit

Stage changes and create a commit:

```bash
git add <files>
git commit -m "<type>: <description>

Content: <brief description of what was created/modified>
Framework: <ISO 27001 / NIS2 / RGPD / etc. if applicable>
Language: <es / en>

Co-Authored-By: AI Assistant <noreply@assistant.com>"
```

Generate the commit message from:
- The content type (blog, linkedin, newsletter)
- The topic and framework covered
- The language of the content
- Or ask the user for a summary

### Step 5: Sync with Main (if needed)

If the branch is behind main:

```bash
git fetch origin main
git rebase origin/main
```

If conflicts occur, help the user resolve them:

```bash
git status  # Show conflicting files
# Edit files to resolve conflicts
git add <resolved-files>
git rebase --continue
```

### Step 6: Push and Create MR/PR

**If gh (GitHub) is available:**

```bash
git push -u origin <branch-name>
gh pr create --fill --base main
```

**If glab (GitLab) is available:**

```bash
git push -u origin <branch-name>
glab mr create --fill --target-branch main
```

**If neither is available:**

```bash
git push -u origin <branch-name>
echo "Branch pushed. Please create the MR/PR manually in your repository UI."
```

### Step 7: Report Result

Share the MR/PR URL with the user, or provide instructions for manual creation.

---

## User Input

$ARGUMENTS
