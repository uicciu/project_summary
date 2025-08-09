# ddh_psi_sum.py
from party import Party1, Party2

def run_protocol():
    # P1 只有标识符
    p1_input = ['alice', 'bob', 'carol', 'dave']
    # P2 拥有标识符和值对
    p2_input = [('bob', 10), ('carol', 20), ('eve', 30)]

    P1 = Party1(p1_input)
    P2 = Party2(p2_input)

    # P2 生成 Paillier 公钥，P1 接收
    pk = P2.get_public_key()
    P1.receive_public_key(pk)

    # Round 1: P1 计算 H(vi)^k1 并发送
    round1_msg = P1.round1_send_hashed()

    # Round 2: P2 接收，计算 H(vi)^{k1k2} 和自身数据处理，返回
    Z, enc_data = P2.round2_process_and_send(round1_msg)
    P1.receive_Z(Z)

    # Round 3: P1 找交集匹配，累加加密值并发送总和
    encrypted_sum = P1.round3_compute_intersection_sum(enc_data)

    # P2 解密得到总和
    total = P2.round3_decrypt_sum(encrypted_sum)

    print("交集求和值 (Intersection sum):", total)
    print("交集大小 (Intersection size):", P1.intersection_size)

if __name__ == "__main__":
    run_protocol()
