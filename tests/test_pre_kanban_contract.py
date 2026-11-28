from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EDGE = ROOT / "supabase" / "functions" / "pre-kanban-mcp" / "index.ts"
MIGRATIONS = ROOT / "supabase" / "migrations"
UI = ROOT / "apps" / "pre-kanban" / "src" / "App.tsx"


class PreKanbanContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.edge = EDGE.read_text(encoding="utf-8")
        cls.sql = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(MIGRATIONS.glob("*_pre_kanban_*.sql"))
        )
        cls.ui = UI.read_text(encoding="utf-8")

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
        self.assertIn("kanban_create_card", self.sql)
        self.assertIn("kanban_move_card", self.sql)
        self.assertIn("column_wip_limit_exceeded", self.sql)

    def test_card_changes_create_outbox_and_source_updates_suppress_echo(self):
        self.assertIn("capture_card_change_outbox", self.sql)
        self.assertIn("kanban.suppress_outbox", self.sql)
        self.assertIn("on conflict (idempotency_key) do nothing", self.sql.lower())

    def test_default_board_has_six_columns(self):
        for semantic_key in ("backlog", "ready", "in_progress", "blocked", "review", "done"):
            with self.subTest(column=semantic_key):
                self.assertIn(f'"semantic_key":"{semantic_key}"', self.sql)

    def test_kanban_ui_uses_authenticated_persistent_backend(self):
        self.assertIn("VITE_SUPABASE_URL", self.ui)
        self.assertIn("VITE_SUPABASE_PUBLISHABLE_KEY", (ROOT / "apps/pre-kanban/src/vite-env.d.ts").read_text())
        self.assertIn("createClient(", self.ui)
        self.assertIn('from("kanban_cards")', self.ui)
        self.assertIn('rpc("kanban_create_board"', self.ui)

    def test_ui_does_not_mutate_pre_lifecycle_stages(self):
        forbidden = ("PRE Stage", "kanban_set_pre_stage", "milestone_acceptance =")
        for value in forbidden:
            with self.subTest(value=value):
                self.assertNotIn(value, self.ui)


if __name__ == "__main__":
    unittest.main()
