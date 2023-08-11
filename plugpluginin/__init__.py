import pathlib
from urllib.parse import urlparse

from extism import Function, host_fn, ValType, Plugin, set_log_file

REGISTRY = dict()
PLUGIN_ID = 0

#set_log_file("stderr", "trace")

@host_fn
def register_plugin(plugin, input_, output, _user_data):
    global REGISTRY
    global PLUGIN_ID
    wasm_path = str(plugin.input_string(input_[0]))
    pieces = urlparse(wasm_path)
    manifest = {"memory": {"max": 5}}
    if pieces.scheme.lower() in ('http', 'https'):
        manifest["wasm"] = [{ "url": wasm_path }]
    else:
        manifest["wasm"] = [{ "path": wasm_path }]
    plugin = Plugin(manifest)
    REGISTRY[PLUGIN_ID] = plugin
    output[0].value = PLUGIN_ID
    PLUGIN_ID += 1

@host_fn
def call_plugin(plugin, input_, output, _user_data):
    global REGISTRY
    plugin_id = input_[0].value
    func_name = plugin.input_string(input_[1])
    input = plugin.input_bytes(input_[2])
    result = REGISTRY[plugin_id].call(func_name, input)
    plugin.return_bytes(output[0], result)

def main():
    functions = [
        Function(
            "register_plugin",
            [ValType.I64],
            [ValType.I64],
            register_plugin,
            None,
        ),
        Function(
            "call_plugin",
            [ValType.I64, ValType.I64, ValType.I64],
            [ValType.I64],
            call_plugin,
            None,
        )
    ]
    wasm_file_path = pathlib.Path(__file__).parent.parent / "plugins" / "host.wasm"
    config = { "wasm": [{"path": str(wasm_file_path)}], "memory": {"max": 5} }
    host_plugin = Plugin(config, functions=functions)
    result = host_plugin.call("run", "")
    print(str(result))
