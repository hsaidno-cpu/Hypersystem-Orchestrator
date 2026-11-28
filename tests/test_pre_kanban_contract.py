import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "supabase" / "functions" / "pre-kanban-mcp" / "index.ts"
MIGRATIONS = ROOT / "supabase" / "migrations"
UI = ROOT / "apps" / "pre-kanban" / "src" / "App.tsx"
SEED = ROOT / "examples" / "hso-ecosystem-development-board-seed.v1.json"


class PreKanbanContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.edge = EDGE.read_text(encoding="utf-8")
        cls.sql = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(MIGRATIONS.glob("*_pre_kanban_*.sql"))
        )
        cls.ui = UI.read_text(encoding="utf-8")
        cls.seed = json.loads(SEED.read_text(encoding="utf-8"))

    def test_all_requested_mcp_tool_names_are_registered(self):
        expected = [
            "kanban.board.list", "kanban.board.get", "kanban.board.create", "kanban.board.update",
            "kanban.column.list", "kanban.column.create", "kanban.column.reorder",
            "kanban.card.list", "kanban.card.get", "kanban.card.create", "kanban.card.update",
            "kanban.card.move", "kanban.card.archive",
            "kanban.label.create", "kanban.label.assign", "kanban.label.remove",
            "kanban.sync.preview", "kanban.sync.apply", "kanban.sync.read_back",
            "kanban.audit.list", "kanban.audit.get", "kanban.sync.status",
        ]
        for name in expected:
            with self.subTest(name=name):
                self.assertIn(f'register("{name}"', self.edge)

    def test_reverse_sync_outbox_tools_are_registered(self):
        for name in (
            "kanban.sync.outbox.list",
            "kanban.sync.outbox.acknowledge",
            "kanban.sync.outbox.conflict",
        ):
            with self.subTest(name=name):
                self.assertIn(f'register("{name}"', self.edge)

    def test_mcp_uses_supabase_oauth_and_user_scoped_rls_client(self):
        self.assertIn("withOAuthProtectedResource()", self.edge)
        self.assertIn('withSupabase({ auth: "user" })', self.edge)
        self.assertIn("pipeline(", self.edge)
        self.assertNotIn("service_role", self.edge.lower())
        self.assertNotIn("SUPABASE_SECRET_KEY", self.edge)
        self.assertIn("withOAuthProtectedResource()", self.edge)

    def test_persistent_tables_and_rls_are_defined(self):
        tables = [
            "kanban_workspaces", "kanban_workspace_members", "kanban_boards",
            "kanban_columns", "kanban_cards", "kanban_labels", "kanban_card_labels",
            "kanban_sync_runs", "kanban_sync_bindings", "kanban_sync_events",
            "kanban_audit_events", "kanban_sync_outbox",
        ]
        for table in tables:
            with self.subTest(table=table):
                self.assertIn(f"public.{table}", self.sql)
                self.assertIn(f"alter table public.{table} enable row level security", self.sql.lower())

    def test_sync_claim_and_per_item_write_are_transactional(self):
        self.assertIn("kanban_claim_sync_run", self.sql)
        self.assertIn("for update", self.sql.lower())
        self.assertIn("kanban_apply_sync_item", self.sql)
        self.assertIn("kanban_ack_sync_outbox", self.sql)
        self.assertIn("kanban_finalize_sync_run", self.sql)
        self.assertIn("kanban_mark_sync_outbox_conflict", self.sql)
        self.assertIn("kanban_create_sync_preview", self.sql)
        self.assertIn("kanban_record_sync_readback", self.sql)
        self.assertIn("sync_item_not_part_of_approved_preview", self.sql)
        self.assertIn("claim_token", self.sql)
        self.assertIn("kanban_create_sync_preview", self.sql)
        self.assertIn("kanban_create_sync_preview(uuid,uuid,text,text,text,jsonb)", self.sql)
        self.assertIn("kanban_create_card", self.sql)
        self.assertIn("kanban_move_card", self.sql)
        self.assertIn("column_wip_limit_exceeded", self.sql)

    def test_sync_state_is_not_directly_writable_by_authenticated_clients(self):
        self.assertIn("revoke insert,update,delete on public.kanban_sync_runs from authenticated", self.sql.lower())
        self.assertIn("revoke insert,update,delete on public.kanban_sync_bindings from authenticated", self.sql.lower())
        self.assertIn("grant select on public.kanban_sync_outbox to authenticated", self.sql.lower())
        self.assertNotIn("grant select,update on public.kanban_sync_outbox", self.sql.lower())
        self.assertIn("revoke insert,update,delete on public.kanban_sync_events from authenticated", self.sql.lower())
        self.assertIn("revoke insert,update,delete on public.kanban_sync_runs from authenticated", self.sql.lower())

    def test_oauth_consent_ui_preserves_request_and_shows_permissions(self):
        self.assertIn('window.location.pathname === "/oauth/consent"', self.ui)
        self.assertIn("getAuthorizationDetails", self.ui)
        self.assertIn("approveAuthorization", self.ui)
        self.assertIn("denyAuthorization", self.ui)
        self.assertIn("authorization_id=", self.ui)
        self.assertIn("details.redirect_uri", self.ui)
        self.assertIn("details?.scope", self.ui)

    def test_card_changes_create_outbox_and_source_updates_suppress_echo(self):
        self.assertIn("capture_card_change_outbox", self.sql)
        self.assertIn("kanban.suppress_outbox", self.sql)
        self.assertIn("on conflict (idempotency_key) do nothing", self.sql.lower())

    def test_default_board_has_eight_columns_in_hso_order(self):
        expected = [
            ("Intake", "intake"), ("Backlog", "backlog"), ("Ready", "ready"),
            ("In Progress", "in_progress"), ("Blocked", "blocked"),
            ("Review & Verification", "review"), ("Done", "done"), ("Archive", "archive"),
        ]
        for name, semantic_key in expected:
            with self.subTest(column=semantic_key):
                self.assertIn(f'"name":"{name}","semantic_key":"{semantic_key}"', self.sql)
                self.assertIn(f'name: "{name}", semantic_key: "{semantic_key}"', self.ui)
                self.assertIn(f'name: "{name}", semantic_key: "{semantic_key}"', self.edge)
        sql_positions = [self.sql.index(f'"semantic_key":"{key}"') for _, key in expected]
        self.assertEqual(sql_positions, sorted(sql_positions))
        self.assertIn("eight workflow columns", self.ui.lower())

    def test_sync_source_digest_covers_extra_metadata(self):
        digest_start = self.edge.index("const sourceDigest = await sha256")
        digest_end = self.edge.index("});", digest_start)
        self.assertIn("extra: item.extra ?? {}", self.edge[digest_start:digest_end])

    def test_visible_archive_is_not_technical_soft_archive(self):
        self.assertIn('"semantic_key":"archive"', self.sql)
        self.assertIn('register("kanban.card.archive"', self.edge)

    def test_sync_writes_use_scoped_rpc_contracts_not_direct_table_mutations(self):
        self.assertIn('rpc("kanban_create_sync_preview"', self.edge)
        self.assertIn('rpc("kanban_claim_sync_run"', self.edge)
        self.assertIn('rpc("kanban_apply_sync_item"', self.edge)
        self.assertIn('rpc("kanban_finalize_sync_run"', self.edge)
        self.assertIn('rpc("kanban_record_sync_readback"', self.edge)
        self.assertIn('rpc("kanban_ack_sync_outbox"', self.edge)
        self.assertIn('rpc("kanban_mark_sync_outbox_conflict"', self.edge)
        self.assertNotIn('from("kanban_sync_runs").insert', self.edge)
        self.assertNotIn('from("kanban_sync_runs").update', self.edge)
        self.assertNotIn('from("kanban_sync_events").insert', self.edge)
        self.assertNotIn('from("kanban_sync_outbox").update', self.edge)

    def test_done_is_fail_closed_until_independent_evidence_gate_exists(self):
        self.assertIn('targetColumn.semantic_key === "done"', self.ui)
        self.assertIn("done_completion_evidence_gate_not_implemented", self.edge)
        self.assertIn('column.semantic_key === "done"', self.edge)
        self.assertIn("HSO Issue #64", self.ui)
        self.assertIn("independent evidence gate", self.sql.lower() + self.edge.lower() + self.ui.lower() + Path(ROOT / "docs/PRE-KANBAN-MCP-ARCHITECTURE.md").read_text(encoding="utf-8").lower())

    def test_kanban_ui_uses_authenticated_persistent_backend(self):
        self.assertIn("VITE_SUPABASE_URL", self.ui)
        self.assertIn("VITE_SUPABASE_PUBLISHABLE_KEY", (ROOT / "apps/pre-kanban/src/vite-env.d.ts").read_text())
        self.assertIn("createClient(", self.ui)
        self.assertIn('from("kanban_cards")', self.ui)
        self.assertIn('rpc("kanban_create_board"', self.ui)

    def test_hso_seed_manifest_is_source_backed_and_never_seeds_done(self):
        columns = self.seed["board"]["columns"]
        self.assertEqual(
            [column["semantic_key"] for column in columns],
            ["intake", "backlog", "ready", "in_progress", "blocked", "review", "done", "archive"],
        )
        items = self.seed["items"]
        self.assertEqual(len(items), 12)
        source_ids = [item["source_work_item_id"] for item in items]
        self.assertEqual(len(source_ids), len(set(source_ids)))
        for item in items:
            with self.subTest(source=item["source_work_item_id"]):
                self.assertTrue(item["source_work_item_id"].startswith("https://github.com/hsaidno-cpu/Hypersystem-Orchestrator/"))
                self.assertTrue(item["source_work_item_id"].endswith(tuple(["/issues/" + item["source_work_item_id"].rsplit("/", 1)[-1], "/pull/" + item["source_work_item_id"].rsplit("/", 1)[-1]])))
                self.assertTrue(item["source_revision"])
                self.assertTrue(item["title"].strip())
                self.assertTrue(item["description"].strip())
                self.assertTrue(item["acceptance_criteria"].strip())
                self.assertTrue(item["evidence_refs"])
                self.assertNotEqual(item["column_semantic_key"], "done")
                self.assertIsInstance(item.get("extra"), dict)

    def test_ui_does_not_mutate_pre_lifecycle_stages(self):
        forbidden = ("PRE Stage", "kanban_set_pre_stage", "milestone_acceptance =")
        for value in forbidden:
            with self.subTest(value=value):
                self.assertNotIn(value, self.ui)


if __name__ == "__main__":
    unittest.main()
