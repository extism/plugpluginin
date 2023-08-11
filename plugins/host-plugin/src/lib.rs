use extism_pdk::*;

extern "C" {
    fn register_plugin(ptr: u64) -> u64;
    fn call_plugin(id: u64, func: u64, input: u64) -> u64;
}

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
