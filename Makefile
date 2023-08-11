

build:
	@poetry install
	@cd plugins/host-plugin && cargo build --target wasm32-unknown-unknown && cd ../..
	@cp plugins/host-plugin/target/wasm32-unknown-unknown/debug/host_plugin.wasm plugins/host.wasm

run:
	@poetry run main

