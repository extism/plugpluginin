

build:
	@poetry install
	@cd plugins/host-plugin && cargo build --target wasm32-unknown-unknown && cd ../..
	@cp plugins/host-plugin/target/wasm32-unknown-unknown/debug/host_plugin.wasm plugins/host.wasm
	@cd plugins/guest-plugin && cargo build --target wasm32-unknown-unknown && cd ../..
	@cp plugins/guest-plugin/target/wasm32-unknown-unknown/debug/guest_plugin.wasm plugins/count_vowels.wasm

run:
	@poetry run main

