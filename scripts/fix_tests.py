from pathlib import Path
p=Path('tests')
files = {
 'test_hal_plugin_loader_impl.py': [
   ("tmp_path / plugins", "tmp_path / \"plugins\""),
   ("(p / foo_plugin.py).write_text(# plugin)", "(p / \"foo_plugin.py\").write_text(\"# plugin\")"),
   ("(d / __init__.py).write_text(# pkg)", "(d / \"__init__.py\").write_text(\"# pkg\")"),
   ("assert foo_plugin in found","assert \"foo_plugin\" in found"),
   ("assert bar in found","assert \"bar\" in found"),
 ],
 'test_hal_registry_helper.py': [
   ("PluginMeta(name=p1, version=1.2.3, entrypoint=p1:main, description=alpha)",
    "PluginMeta(name=\"p1\", version=\"1.2.3\", entrypoint=\"p1:main\", description=\"alpha\")"),
   ("r.get(p1)","r.get(\"p1\")"),
   ("r.unregister(p1)","r.unregister(\"p1\")"),
 ]
}
for name, edits in files.items():
    f = p / name
    if not f.exists():
        print('missing', name)
        continue
    s = f.read_text()
    orig=s
    for old, new in edits:
        s = s.replace(old, new)
    if s!=orig:
        f.write_text(s)
        print('patched', name)
print('done')
