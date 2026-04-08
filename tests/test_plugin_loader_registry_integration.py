import pytest
from rmer_ai_coffee.hal.plugin_loader import PluginLoader, PluginLoadError


def test_register_on_load_and_unregister_on_unload(tmp_path):
    p = tmp_path / 'plugins'
    p.mkdir()
    # module exposing PLUGIN_META dict
    f = p / 'reg_plugin.py'
    f.write_text("""
PLUGIN_META = {'name': 'reg', 'version': '0.1', 'entrypoint': 'reg:main', 'description': 'reg plugin'}

def ping():
    return 'pong'
""")
    pl = PluginLoader()
    mod = pl.load('reg_plugin', paths=[str(p)])
    # registry should have registered under name 'reg'
    assert pl.registry.get('reg') is not None
    assert pl.registry.get('reg').version == '0.1'
    pl.unload('reg_plugin')
    assert pl.registry.get('reg') is None


def test_missing_name_in_plugin_meta_raises(tmp_path):
    p = tmp_path / 'plugins'
    p.mkdir()
    f = p / 'bad_plugin.py'
    f.write_text("""
PLUGIN_META = {'version': '0.2'}
""")
    pl = PluginLoader()
    with pytest.raises(PluginLoadError):
        pl.load('bad_plugin', paths=[str(p)])
