#!/bin/bash
circom circuits/poseidon2.circom --r1cs --wasm --sym -o build
snarkjs groth16 setup build/poseidon2.r1cs powersOfTau28_hez_final_10.ptau build/poseidon2.zkey
snarkjs zkey export verificationkey build/poseidon2.zkey build/verification_key.json
