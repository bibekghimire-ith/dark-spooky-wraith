---
title: One data file, one site
date: 2026-10-30
summary: Why this portfolio is generated from a single content file, and what that buys.
---
This site has no database and no admin screen. Everything on it comes from one
file, `content.yaml`.

## What that buys

- **Edits are small.** A new project is a few lines of YAML, not a template change.
- **Mistakes are loud.** The app checks the file at startup and names the field that is wrong.
- **Hosting is cheap.** There is nothing to back up except the repository.

## The check

```python
def validate(data):
    errors = []
    if not data.get("owner", {}).get("name"):
        errors.append("owner.name is required")
    return errors
```

Raw HTML in a post is shown as text, and links may only use `http`, `https` or `mailto`.
