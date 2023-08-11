use extism_pdk::*;

const VOWELS: &[char] = &['a', 'A', 'e', 'E', 'i', 'I', 'o', 'O', 'u', 'U'];

#[plugin_fn]
pub fn count_vowels(input: String) -> FnResult<String> {
    let mut count = 0;
    for ch in input.chars() {
        if VOWELS.contains(&ch) {
            count += 1;
        }
    }

    Ok(count.to_string())
}
