# BurnBook Examples

This directory contains sample code files that demonstrate the types of issues
BurnBook can detect. Use these to test the tool:

```bash
# Roast the bad examples
cd examples
burnbook roast . --severity nuclear

# Roast a specific file
burnbook roast bad_python.py --offline
```
