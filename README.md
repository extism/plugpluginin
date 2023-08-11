# Calling plug-ins from plug-ins

A common question we get asked is how to call a plug-in from another plug-in.
It is possible to run wasm in interpreted mode [inside an Extism plugin](https://github.com/rusticus-io/Extism-wasm-in-wasm) but this is very experimental and there are some downsides to this. This repo demonstrates a pattern I'm calling "inter-plugin communication" in reference [Inter-process communication](https://en.wikipedia.org/wiki/Inter-process_communication).

It works in a similar way. The host application acts as the OS and the wasm plugins act as the processes. The host facilitates communication b/w the processes.

## Running

Requires [poetry](https://python-poetry.org/):

```
make build
make run
```

## Python Host

I wrote the host in python here because it's easy to have global mutable data, but you can write this in any of the host languages that support host functions.

The host implements 2 Host Functions in python:

* register_plugin(i64) -> i64
* call_plugin(i64, i64, i64) -> i64

### register_plugin

This function allows any Extism plugin to initialize another. You can think of this as analogous to the `exec` syscall and the plugin id as analogous to a process id. There is a global dictionary `REGISTRY` which has type `dict[int, Plugin]`. The function creates a plugin, adds it to the registry, then gives the plugin back an ID as a handle to this plugin.

```python
@host_fn
def register_plugin(plugin, input_, output, _user_data):
    global REGISTRY
    global PLUGIN_ID
    name = plugin.input_string(input_[0])
    # we just look up the wasm file by name, you can make your own lookup logic here
    wasm_file_path = pathlib.Path(__file__).parent.parent / "plugins" / f"{name}.wasm"
    config = { "wasm": [{"path": str(wasm_file_path)}], "memory": {"max": 5} }
    plugin = Plugin(config)
    REGISTRY[PLUGIN_ID] = plugin
    output[0].value = PLUGIN_ID
    PLUGIN_ID += 1
```

### call_plugin

Now that we have a plugin running and an id, we can call it with call_plugin. Because all Extism plugins have a consistent interface, this should work for any Extism exports. We just need to give the host the plugin-id, the function name, and the input. It will return a pointer to the output. The implementation is simple:

```python
@host_fn
def call_plugin(plugin, input_, output, _user_data):
    global REGISTRY
    plugin_id = input_[0].value
    func_name = plugin.input_string(input_[1])
    # this is a string in this demo but can be anything so we keep it as bytes
    input = plugin.input_bytes(input_[2])
    result = REGISTRY[plugin_id].call(func_name, input)
    plugin.return_bytes(output[0], result)
```

## Plugin

I wrote the plug-ins in rust, but we can use any PDK that supports host functions.
On the plug-in side, we first need to register the external host functions:

```rust
extern "C" {
    fn register_plugin(ptr: u64) -> u64;
    fn call_plugin(id: u64, func: u64, input: u64) -> u64;
}
```

Now let's use use them to register a count-vowels plugin then call count_vowels function on it:

```rust
#[plugin_fn]
pub fn run(_: ()) -> FnResult<String> {
    // register a count_vowels plugin
    let name = "count_vowels".to_string();
    let m = Memory::from_bytes(name.as_bytes());
    let id = unsafe { register_plugin(m.offset) };
    // get back an id to the plugin
    // now we can call it:
    let func = "count_vowels".to_string();
    let funcm = Memory::from_bytes(func.as_bytes());
    let input = "Hello, World!".to_string();
    let inputm = Memory::from_bytes(input.as_bytes());
    let result = unsafe { call_plugin(id, funcm.offset, inputm.offset) };
    // get the string result back from the plugin
    let m = Memory::find(result).unwrap();
    Ok(m.to_string()?)
}
```

## Considerations

There lots of considerations when applying this pattern.

First you must consider the overhead of all this indirect copying. You should measure and optimize as best as you can. You might be able to optimize this with some extra host functions.

Second you should consider security and resource problems. Giving a plugin the ability to spin up as many plugins as it wants is probably not a good idea in production. You should apply some kind of access control to make sure it can only load the plugins you want, and maybe limit how many it can load and which functions it can call. Creating a more specific API than just `call_plugin` might help you narrow down how the plugin can interact with others.
