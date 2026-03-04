import os
import textwrap


class BugGenerator:
    def __init__(self, target_dir: str = "/tmp/aether_bugs"):
        self.target_dir = target_dir
        os.makedirs(self.target_dir, exist_ok=True)

    def generate_syntax_error(self) -> str:
        code = textwrap.dedent("""
            def faulty_function():
                print("Missing parenthesis"
            
            faulty_function()
        """)
        path = os.path.join(self.target_dir, "syntax_bug.py")
        with open(path, "w") as f:
            f.write(code)
        return path

    def generate_import_error(self) -> str:
        code = textwrap.dedent("""
            import non_existent_package_aether_123
            
            def test():
                return True
            
            test()
        """)
        path = os.path.join(self.target_dir, "import_bug.py")
        with open(path, "w") as f:
            f.write(code)
        return path

    def generate_key_error(self) -> str:
        code = textwrap.dedent("""
            def leak():
                data = {"a": 1}
                return data["non_existent"]
            
            leak()
        """)
        path = os.path.join(self.target_dir, "key_bug.py")
        with open(path, "w") as f:
            f.write(code)
        return path

    def cleanup(self):
        import shutil

        if os.path.exists(self.target_dir):
            shutil.rmtree(self.target_dir)
