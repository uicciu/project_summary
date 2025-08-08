const snarkjs = require("snarkjs");
const fs = require("fs");

async function main() {
    // 输入数据，私有输入in数组
    const input = {
        in: ["12345678901234567890", "98765432109876543210"]
    };

    // 生成证明
    const { proof, publicSignals } = await snarkjs.groth16.fullProve(
        input,
        "./build/poseidon2.wasm",
        "./build/poseidon2_final.zkey"
    );

    console.log("Public signals (hash output):", publicSignals);

    // 验证证明
    const vKey = JSON.parse(fs.readFileSync("./build/verification_key.json"));
    const res = await snarkjs.groth16.verify(vKey, publicSignals, proof);

    if (res === true) {
        console.log("Proof is valid");
    } else {
        console.log("Proof is NOT valid");
    }
}

main().then(() => {
    console.log("Test completed");
}).catch((err) => {
    console.error(err);
});
