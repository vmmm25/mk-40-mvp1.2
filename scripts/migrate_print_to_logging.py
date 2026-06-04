import os
import re

def migrate_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Determine if we need to add a logger import
    needs_logger = False
    
    # Patterns to replace
    # print(f"[JARVIS] 🔧 {name}  {args}") -> logger.info(f"Tool called: {name} args={args}")
    # We will do some generic replacements:
    # print("[JARVIS] 🔧 " + ...) -> logger.info(...)
    # print("[JARVIS] ⚠️ " + ...) -> logger.warning(...)
    # print("[JARVIS] ❌ " + ...) -> logger.error(...)
    # print("[JARVIS] 🔴 " + ...) -> logger.critical(...)
    # print("[JARVIS] 🐛 " + ...) -> logger.debug(...)
    
    # Let's use regex to replace common prints.
    # We'll match `print(f"[JARVIS] <icon> <message>")`
    
    # Mapping icons to log levels
    icon_to_level = {
        '🔧': 'info',
        '⚠️': 'warning',
        '❌': 'error',
        '🔴': 'critical',
        '🐛': 'debug'
    }

    # Match print(f"[JARVIS] 🔧 message") or print("[JARVIS] 🔧 message")
    # Captures: 1: f or empty, 2: icon, 3: message
    pattern = r'print\(\s*(f?)["\']\[JARVIS\]\s*(🔧|⚠️|❌|🔴|🐛)\s*(.*?)["\']\s*\)'

    def replacer(match):
        nonlocal needs_logger
        needs_logger = True
        is_fstring = match.group(1)
        icon = match.group(2)
        message = match.group(3)
        
        level = icon_to_level.get(icon, 'info')
        return f'logger.{level}({is_fstring}"{message}")'

    new_content, count = re.subn(pattern, replacer, content)
    
    # Also replace traceback.print_exc() with logger.exception("Exception occurred")
    new_content, tb_count = re.subn(r'traceback\.print_exc\(\)', r'logger.exception("Exception occurred")', new_content)
    
    if tb_count > 0:
        needs_logger = True

    if needs_logger and "import logging" not in new_content:
        # insert logger definition after imports
        imports = "import logging\n\nlogger = logging.getLogger(__name__)\n"
        # naive insertion at top
        new_content = imports + new_content
    elif needs_logger and "logger = logging.getLogger" not in new_content:
        new_content = new_content.replace("import logging", "import logging\n\nlogger = logging.getLogger(__name__)", 1)
        
    if count > 0 or tb_count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Migrated {filepath}: {count + tb_count} replacements")

def main():
    for root, dirs, files in os.walk('.'):
        if '.venv' in root or '.git' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py') and file != 'migrate_print_to_logging.py':
                filepath = os.path.join(root, file)
                migrate_file(filepath)

if __name__ == '__main__':
    main()
