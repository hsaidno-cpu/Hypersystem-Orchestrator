import unittest

from tools.verify_ecig_trust_root_approval import (
    GOV01_LOGIN,
    GateError,
    active_key_map,
    exact_owner_approval,
)


class TrustRootApprovalGateTests(unittest.TestCase):
    def test_empty_trust_store_does_not_require_owner_action(self):
        empty = {"schema_version": "1.0.0", "algorithm": "Ed25519", "keys": []}
        self.assertEqual(active_key_map(empty), {})

    def test_only_active_keys_affect_the_approval_gate(self):
        before = {"algorithm": "Ed25519", "keys": []}
        after = {"algorithm": "Ed25519", "keys": [
            {"key_id": "retired", "status": "REVOKED", "public_key_base64": "A" * 44}
        ]}
        self.assertEqual(active_key_map(before), active_key_map(after))

    def test_active_key_addition_is_detected(self):
        before = {}
        after = {"algorithm": "Ed25519", "keys": [
            {"key_id": "key-1", "status": "ACTIVE", "public_key_base64": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="}
        ]}
        self.assertNotEqual(active_key_map(before), active_key_map(after))

    def test_malformed_active_key_fails_closed(self):
        after = {"algorithm": "Ed25519", "keys": [
            {"key_id": "key-1", "status": "ACTIVE", "public_key_base64": "not-base64"}
        ]}
        with self.assertRaises(GateError):
            active_key_map(after)

    def test_exact_head_owner_comment_is_required(self):
        head = "a" * 40
        comments = [
            {"id": 1, "body": f"APPROVE TRUST ROOT {head}", "user": {"login": "someone-else"}},
            {"id": 2, "body": f"APPROVE TRUST ROOT {'b' * 40}", "user": {"login": GOV01_LOGIN}},
            {"id": 3, "body": f"APPROVE TRUST ROOT {head}\nPlease merge", "user": {"login": GOV01_LOGIN}},
        ]
        self.assertIsNone(exact_owner_approval(comments, head))

    def test_exact_head_owner_comment_is_accepted(self):
        head = "a" * 40
        comment = {
            "id": 7,
            "body": f"APPROVE TRUST ROOT {head}",
            "user": {"login": GOV01_LOGIN},
            "created_at": "2026-11-25T13:00:00Z",
            "html_url": "https://github.com/example/repo/pull/7#issuecomment-7",
        }
        self.assertEqual(exact_owner_approval([comment], head), comment)

    def test_duplicate_exact_approvals_choose_stable_first_receipt(self):
        head = "a" * 40
        comments = [
            {"id": 10, "body": f"APPROVE TRUST ROOT {head}", "user": {"login": GOV01_LOGIN}, "created_at": "2026-11-25T13:02:00Z"},
            {"id": 9, "body": f"APPROVE TRUST ROOT {head}", "user": {"login": GOV01_LOGIN}, "created_at": "2026-11-25T13:01:00Z"},
        ]
        self.assertEqual(exact_owner_approval(comments, head), comments[1])


if __name__ == "__main__":
    unittest.main()
