from rmer_ai_coffee.hal.registry import PluginRegistry, PluginMeta


def test_registry_register_get_list():
    r = PluginRegistry()
    meta = PluginMeta(name="p1", version="1.2.3", entrypoint="p1:main", description="alpha")
    r.register(meta)
    assert r.get("p1") is not None
    assert r.get("p1").version == "1.2.3"
    listed = r.list()
    assert any(m.name == "p1" for m in listed)
    d = r.as_dict()
    assert "p1" in d
    r.unregister("p1")
    assert r.get("p1") is None
