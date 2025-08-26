#!/bin/bash
rustup +nightly component add llvm-tools-preview
~/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/llvm-profdata merge -sparse ./*.profraw -o merged.profdata
~/.rustup/toolchains/stable-x86_64-unknown-linux-gnu/lib/rustlib/x86_64-unknown-linux-gnu/bin/llvm-cov     show /home/maksim/rust-url/fuzz/target/x86_64-unknown-linux-gnu/release/fuzz_target_1     --instr-profile=merged.profdata     --format=html     --output-dir=coverage-html     --show-line-counts-or-regions  --ignore-filename-regex='/.cargo/registry'
cargo +nightly fuzz run fuzz_target_1 -- -runs=100000
export RUSTFLAGS="-C instrument-coverage -C link-dead-code -C opt-level=0 -C debuginfo=2"
