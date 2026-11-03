"""AST Scanner Unit Test: Enforces strict READ-ONLY Kubernetes API calls across the codebase."""
import ast
from pathlib import Path

FORBIDDEN_VERB_PREFIXES = (
    "create_",
    "delete_",
    "patch_",
    "replace_",
    "connect_get_namespaced_pod_exec",
    "connect_post_namespaced_pod_exec",
    "connect_get_namespaced_pod_portforward",
    "connect_post_namespaced_pod_portforward",
)


def test_ast_scans_and_forbids_non_read_verbs():
    """Verify that NO write, mutate, exec, or port-forward Kubernetes calls exist in app/."""
    app_dir = Path(__file__).parent.parent / "app"
    py_files = list(app_dir.rglob("*.py"))
    assert len(py_files) > 0, "No python files found in app/"

    violations = []

    for py_file in py_files:
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                elif isinstance(node.func, ast.Name):
                    func_name = node.func.id

                for forbidden in FORBIDDEN_VERB_PREFIXES:
                    if func_name.startswith(forbidden):
                        violations.append(f"{py_file.name}:{node.lineno} calls forbidden API verb '{func_name}'")

    assert not violations, f"STRICT READ-ONLY SAFETY VIOLATIONS DETECTED:\n" + "\n".join(violations)

