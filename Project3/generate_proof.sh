# 编译电路
circom circuits/poseidon2.circom --r1cs --wasm --sym -o build/

# 生成可信设置
snarkjs groth16 setup build/poseidon2.r1cs powersOfTau28_hez_final_10.ptau build/poseidon2_0000.zkey
snarkjs zkey contribute build/poseidon2_0000.zkey build/poseidon2_final.zkey --name="First contribution" -v
snarkjs zkey export verificationkey build/poseidon2_final.zkey build/verification_key.json

# 生成证明和验证（需准备 input.json）
snarkjs groth16 prove build/poseidon2_final.zkey input.json proof.json public.json
snarkjs groth16 verify build/verification_key.json public.json proof.json
