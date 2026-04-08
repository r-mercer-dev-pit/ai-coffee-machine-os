from rmer_ai_coffee.hal.plugin_loader import PluginLoader

def test_discover_plugins(tmp_path):
    p = tmp_path / "plugins"
    p.mkdir()
    (p / "foo_plugin.py").write_text("# plugin")
    d = p / bar
    d.mkdir()
    (d / "__init__.py").write_text("# pkg")
    pl = PluginLoader()
    found = pl.discover([str(p)])
    assert "foo_plugin" in found
    assert "bar" in found
