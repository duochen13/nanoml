# Skills

Optional skills that enhance or modify the framework behavior.

## Available Skills

### demo-fill
**Purpose:** Fills skeleton example code with working implementations.

**Usage:**
```bash
make demo           # Activate demo mode
make run            # See actual results
make demo-restore   # Restore skeleton
```

See [demo-fill/README.md](demo-fill/README.md) for details.

## Creating Your Own Skills

Skills are self-contained Python scripts that can:
- Modify code dynamically
- Add optional features
- Enhance developer experience
- Provide debugging tools

### Skill Structure
```
skills/
├── your-skill/
│   ├── README.md     # Documentation
│   ├── activate.py   # Main activation script
│   └── ...           # Supporting files
```

### Integration with Makefile

Add your skill to the Makefile:
```makefile
your-skill:
	@python3 skills/your-skill/activate.py
```

## Philosophy

Skills should be:
- **Optional** - Framework works without them
- **Self-contained** - Don't depend on each other
- **Reversible** - Can be deactivated/restored
- **Safe** - Create backups, ask for confirmation
- **Documented** - Clear README explaining purpose and usage
