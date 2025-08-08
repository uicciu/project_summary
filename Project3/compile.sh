#!/bin/bash

# 1. 编译电路
circom circuits/poseidon2.circom --r1cs --wasm --sym -o build

# 2. 生成可信设置
snarkjs groth16 setup build/poseidon2.r1cs powersOfTau28_hez_final_10.ptau build/poseidon2_0000.zkey

# 3. 贡献阶段（无交互，直接跳过可用 --name 设定）
snarkjs zkey contribute build/poseidon2_0000.zkey build/poseidon2_final.zkey --name="First contribution" -v

# 4. 导出验证密钥
snarkjs zkey export verificationkey build/poseidon2_final.zkey build/verification_key.json

# 5. 生成证明
snarkjs groth16 prove build/poseidon2_final.zkey input.json proof.json public.json

# 6. 验证证明
snarkjs groth16 verify build/verification_key.json public.json proof.json
