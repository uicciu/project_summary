#!/bin/bash
node build/poseidon2_js/generate_witness.js build/poseidon2_js/poseidon2.wasm input.json build/witness.wtns
snarkjs groth16 prove build/poseidon2.zkey build/witness.wtns build/proof.json build/public.json
snarkjs groth16 verify build/verification_key.json build/public.json build/proof.json
