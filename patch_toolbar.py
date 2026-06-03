import re

with open('ui/config_toolbar.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace _on_pull_model
old_pull = '''    def _on_pull_model(self):
        """Run ollama pull <model> in a terminal window."""
        model_id = self._model_combo.currentData()
        self._pull_status.setText(f"‘ºÁ  Pulling {model_id}...")
        self._pull_status.setStyleSheet(f"color: {C.ACC2}; background: transparent;")
        self._pull_btn.setEnabled(False)

        # Run ollama pull in a new terminal window
        try:
            cmd = f"ollama pull {model_id}"
            if _OS == "Windows":
                subprocess.Popen(
                    ["start", "cmd", "/k", cmd],
                    shell=True, cwd=str(Path.home())
                )
            elif _OS == "Darwin":
                subprocess.Popen(
                    ["osascript", "-e",
                     f'tell app "Terminal" to do script "{cmd}"'],
                    cwd=str(Path.home())
                )
            else:  # Linux
                subprocess.Popen(
                    ["x-terminal-emulator", "-e", cmd],
                    cwd=str(Path.home())
                )
        except Exception as e:'''

new_pull = '''    def _on_pull_model(self):
        """Run ollama pull <model> in a terminal window securely."""
        model_id = self._model_combo.currentData() or self._model_combo.currentText()
        
        # Security: sanitize model_id
        import re
        if not re.match(r"^[a-zA-Z0-9\-\.\:]+$", model_id):
            self._pull_status.setText("‘ÿÓ Error: Modelo inv·lido")
            self._pull_status.setStyleSheet(f"color: {C.RED}; background: transparent;")
            return
            
        self._pull_status.setText(f"‘ºÁ  Pulling {model_id}...")
        self._pull_status.setStyleSheet(f"color: {C.ACC2}; background: transparent;")
        self._pull_btn.setEnabled(False)

        try:
            if _OS == "Windows":
                subprocess.Popen(["cmd.exe", "/c", "start", "cmd.exe", "/k", "ollama", "pull", model_id], cwd=str(Path.home()))
            elif _OS == "Darwin":
                script = f'tell app "Terminal" to do script "ollama pull {model_id}"'
                subprocess.Popen(["osascript", "-e", script], cwd=str(Path.home()))
            else:  # Linux
                subprocess.Popen(["x-terminal-emulator", "-e", f"ollama pull {model_id}"], cwd=str(Path.home()))
        except Exception as e:'''

content = content.replace(old_pull, new_pull)

# Fix _on_up_server
old_up = '''    def _on_up_server(self):
        """Start ollama server in a terminal."""
        try:
            cmd = "ollama serve"
            if _OS == "Windows":
                subprocess.Popen(
                    ["start", "cmd", "/k", cmd],
                    shell=True, cwd=str(Path.home())
                )'''

new_up = '''    def _on_up_server(self):
        """Start ollama server in a terminal securely."""
        try:
            if _OS == "Windows":
                subprocess.Popen(
                    ["cmd.exe", "/c", "start", "cmd.exe", "/k", "ollama", "serve"],
                    cwd=str(Path.home())
                )'''

content = content.replace(old_up, new_up)

with open('ui/config_toolbar.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("config_toolbar patched")
