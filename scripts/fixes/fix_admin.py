with open("core/services/admin_api.py", "r") as f:
    content = f.read()

content = content.replace(
    'self.server = ReusableHTTPServer("127.0.0.1", self.port), AdminAPIHandler)',
    'self.server = ReusableHTTPServer(("127.0.0.1", self.port), AdminAPIHandler)',
)

with open("core/services/admin_api.py", "w") as f:
    f.write(content)
