# tests/test_ddh_psi.py
import unittest
from party import Party1, Party2

class TestDDHPSISum(unittest.TestCase):
    def setUp(self):
        # P1和P2的输入数据
        self.p1_input = ['alice', 'bob', 'carol', 'dave']
        self.p2_input = [('bob', 10), ('carol', 20), ('eve', 30)]

        self.P1 = Party1(self.p1_input)
        self.P2 = Party2(self.p2_input)

        # 公钥交换
        pk = self.P2.get_public_key()
        self.P1.receive_public_key(pk)

    def test_intersection_sum_and_size(self):
        # Round 1
        round1_msg = self.P1.round1_send_hashed()

        # Round 2
        Z, enc_data = self.P2.round2_process_and_send(round1_msg)
        self.P1.receive_Z(Z)

        # Round 3
        encrypted_sum = self.P1.round3_compute_intersection_sum(enc_data)
        total = self.P2.round3_decrypt_sum(encrypted_sum)

        # 交集应该是 {'bob', 'carol'}，大小为2，总和值为30
        self.assertEqual(self.P1.intersection_size, 2)
        self.assertEqual(total, 30)

    def test_no_intersection(self):
        # P2 输入无交集
        P2_no_inter = Party2([('eve', 10), ('frank', 20)])
        pk = P2_no_inter.get_public_key()
        self.P1.receive_public_key(pk)

        round1_msg = self.P1.round1_send_hashed()
        Z, enc_data = P2_no_inter.round2_process_and_send(round1_msg)
        self.P1.receive_Z(Z)
        encrypted_sum = self.P1.round3_compute_intersection_sum(enc_data)
        total = P2_no_inter.round3_decrypt_sum(encrypted_sum)

        self.assertEqual(self.P1.intersection_size, 0)
        self.assertEqual(total, 0)

if __name__ == '__main__':
    unittest.main()
