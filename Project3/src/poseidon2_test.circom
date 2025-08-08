pragma circom 2.0.0;
include "poseidon2.circom";

template Poseidon2Test() {
    signal input preimage[2];
    signal output hash;
    component h = Poseidon2();
    for (var i = 0; i < 2; i++) {
        h.preimage[i] <== preimage[i];
    }
    h.hash <== hash;
}

component main = Poseidon2Test();
