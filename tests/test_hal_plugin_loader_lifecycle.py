from rmer_ai_coffee.hal.plugin_loader import PluginLoader


def test_load_unload_from_file(tmp_path):
    p = tmp_path / "plugins"
    p.mkdir()
    plugin_file = p / "alpha_plugin.py"
    plugin_file.write_text("""
PLUGIN_NAME = 'alpha'

def ping():
    return 'pong'
""")
    pl = PluginLoader()
    found = pl.discover([str(p)])
    assert 'alpha_plugin' in found
    mod = pl.load('alpha_plugin', paths=[str(p)])
    assert hasattr(mod, 'ping')
    assert mod.ping() == 'pong'
    loaded = pl.get_loaded()
    assert 'alpha_plugin' in loaded
    pl.unload('alpha_plugin')
    assert 'alpha_plugin' not in pl.get_loaded()


def test_load_package_plugin(tmp_path):
    p = tmp_path / "plugins"
    p.mkdir()
    pkg = p / "betapkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("""
PLUGIN_NAME = 'beta'

def hello():
    return 'hi'
""")
    pl = PluginLoader()
    found = pl.discover([str(p)])
    assert 'betapkg' in found
    mod = pl.load('betapkg', paths=[str(p)])
    assert hasattr(mod, 'hello')
    assert mod.hello() == 'hi'
    pl.unload('betapkg')
