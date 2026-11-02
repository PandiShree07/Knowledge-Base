from pathlib import Path


def test_seed_script_has_demo_database_safety_guard():
    source = (Path(__file__).resolve().parents[1] / "scripts" / "seed_demo_data.py").read_text(encoding="utf-8")
    assert 'db_name.lower() != "uka_demo"' in source
    assert "never deletes rows" in source
    assert "DELETE FROM" not in source.upper()
    assert "TRUNCATE" not in source.upper()


def test_documents_have_okf_frontmatter():
    root = Path(__file__).resolve().parents[1] / "knowledge" / "documents"
    files = list(root.rglob("*.md"))
    assert len(files) >= 35
    assert all(path.read_text(encoding="utf-8").startswith("---") for path in files)
