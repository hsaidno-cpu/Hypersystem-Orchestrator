import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import { createClient, type Session } from "@supabase/supabase-js";

type Workspace = { id: string; name: string; slug: string; description?: string | null };
type Board = { id: string; workspace_id: string; name: string; slug: string; revision: number };
type Column = { id: string; name: string; semantic_key: string; position: number; color: string };
type Card = {
  id: string; board_id: string; column_id: string; title: string; description: string | null;
  priority: "critical" | "high" | "medium" | "low"; acceptance_criteria: string | null;
  position: number; revision: number; metadata: Record<string, unknown>; created_at: string;
};

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY;
const supabase = supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

const DEFAULT_COLUMNS = [
  { name: "Backlog", semantic_key: "backlog", color: "gray" },
  { name: "Ready", semantic_key: "ready", color: "blue" },
  { name: "In Progress", semantic_key: "in_progress", color: "yellow" },
  { name: "Blocked", semantic_key: "blocked", color: "red" },
  { name: "Review & Verification", semantic_key: "review", color: "purple" },
  { name: "Done", semantic_key: "done", color: "green" },
];

function slugify(value: string) {
  return value.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 63);
}

function priorityLabel(priority: Card["priority"]) {
  return priority === "critical" ? "Critical" : priority[0].toUpperCase() + priority.slice(1);
}

export default function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [email, setEmail] = useState("");
  const [otpSent, setOtpSent] = useState(false);
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [workspaceId, setWorkspaceId] = useState("");
  const [boards, setBoards] = useState<Board[]>([]);
  const [boardId, setBoardId] = useState("");
  const [columns, setColumns] = useState<Column[]>([]);
  const [cards, setCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [workspaceName, setWorkspaceName] = useState("");
  const [boardName, setBoardName] = useState("");
  const [cardTitle, setCardTitle] = useState("");
  const [cardDescription, setCardDescription] = useState("");
  const [cardPriority, setCardPriority] = useState<Card["priority"]>("medium");

  const user = session?.user ?? null;
  const board = useMemo(() => boards.find((item) => item.id === boardId) ?? null, [boards, boardId]);

  useEffect(() => {
    if (!supabase) {
      setAuthLoading(false);
      return;
    }
    let mounted = true;
    supabase.auth.getSession().then(({ data }) => {
      if (mounted) {
        setSession(data.session);
        setAuthLoading(false);
      }
    });
    const { data } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession);
      setAuthLoading(false);
    });
    return () => {
      mounted = false;
      data.subscription.unsubscribe();
    };
  }, []);

  const loadWorkspaces = useCallback(async () => {
    if (!supabase || !user) return;
    setLoading(true);
    const { data, error } = await supabase.from("kanban_workspaces")
      .select("id,name,slug,description").order("name");
    setLoading(false);
    if (error) {
      setMessage(error.message);
      return;
    }
    const next = (data ?? []) as Workspace[];
    setWorkspaces(next);
    if (!next.some((item) => item.id === workspaceId)) {
      setWorkspaceId(next[0]?.id ?? "");
    }
  }, [user, workspaceId]);

  useEffect(() => {
    void loadWorkspaces();
  }, [loadWorkspaces]);

  const loadBoards = useCallback(async () => {
    if (!supabase || !workspaceId) {
      setBoards([]);
      setBoardId("");
      return;
    }
    const { data, error } = await supabase.from("kanban_boards")
      .select("id,workspace_id,name,slug,revision")
      .eq("workspace_id", workspaceId).eq("is_archived", false).order("position");
    if (error) {
      setMessage(error.message);
      return;
    }
    const next = (data ?? []) as Board[];
    setBoards(next);
    if (!next.some((item) => item.id === boardId)) setBoardId(next[0]?.id ?? "");
  }, [workspaceId, boardId]);

  useEffect(() => {
    void loadBoards();
  }, [loadBoards]);

  const loadBoardData = useCallback(async () => {
    if (!supabase || !boardId) {
      setColumns([]);
      setCards([]);
      return;
    }
    setLoading(true);
    const [columnResult, cardResult] = await Promise.all([
      supabase.from("kanban_columns").select("id,name,semantic_key,position,color")
        .eq("board_id", boardId).eq("is_archived", false).order("position"),
      supabase.from("kanban_cards").select("*")
        .eq("board_id", boardId).eq("is_archived", false).order("position"),
    ]);
    setLoading(false);
    if (columnResult.error || cardResult.error) {
      setMessage(columnResult.error?.message ?? cardResult.error?.message ?? "Unable to load board.");
      return;
    }
    setColumns((columnResult.data ?? []) as Column[]);
    setCards((cardResult.data ?? []) as Card[]);
  }, [boardId]);

  useEffect(() => {
    void loadBoardData();
  }, [loadBoardData]);

  async function signIn(event: FormEvent) {
    event.preventDefault();
    if (!supabase) return;
    setMessage("");
    const { error } = await supabase.auth.signInWithOtp({
      email: email.trim(),
      options: { emailRedirectTo: window.location.origin, shouldCreateUser: true },
    });
    if (error) setMessage(error.message);
    else {
      setOtpSent(true);
      setMessage("A sign-in link has been sent to your email.");
    }
  }

  async function createWorkspace(event: FormEvent) {
    event.preventDefault();
    if (!supabase || !user || !workspaceName.trim()) return;
    const slug = slugify(workspaceName);
    if (!slug) return setMessage("Workspace name needs at least one letter or number.");
    setLoading(true);
    const { data, error } = await supabase.from("kanban_workspaces").insert({
      name: workspaceName.trim(), slug, created_by: user.id,
    }).select("id,name,slug,description").single();
    setLoading(false);
    if (error) return setMessage(error.message);
    const created = data as Workspace;
    setWorkspaces((current) => [...current, created]);
    setWorkspaceId(created.id);
    setWorkspaceName("");
    setMessage("Workspace created.");
  }

  async function createBoard(event: FormEvent) {
    event.preventDefault();
    if (!supabase || !user || !workspaceId || !boardName.trim()) return;
    const slug = slugify(boardName);
    if (!slug) return setMessage("Board name needs at least one letter or number.");
    setLoading(true);
    const { data, error } = await supabase.rpc("kanban_create_board", {
      p_workspace_id: workspaceId,
      p_name: boardName.trim(),
      p_slug: slug,
      p_description: "PRE/HSO operational work board",
      p_columns: DEFAULT_COLUMNS,
    });
    setLoading(false);
    if (error) return setMessage(error.message);
    const createdBoard = data?.board as Board | undefined;
    setBoardName("");
    setMessage("Board created with six workflow columns.");
    await loadBoards();
    if (createdBoard?.id) setBoardId(createdBoard.id);
  }

  async function createCard(event: FormEvent) {
    event.preventDefault();
    if (!supabase || !user || !board || !cardTitle.trim() || columns.length === 0) return;
    const backlog = columns.find((column) => column.semantic_key === "backlog") ?? columns[0];
    setLoading(true);
    const { data, error } = await supabase.rpc("kanban_create_card", {
      p_workspace_id: workspaceId,
      p_board_id: board.id,
      p_column_id: backlog.id,
      p_title: cardTitle.trim(),
      p_description: cardDescription.trim() || null,
      p_priority: cardPriority,
      p_acceptance_criteria: null,
      p_due_date: null,
      p_metadata: {},
    });
    setLoading(false);
    if (error) return setMessage(error.message);
    setCards((current) => [...current, data as Card]);
    setCardTitle("");
    setCardDescription("");
    setCardPriority("medium");
    setMessage("Card created in Backlog.");
  }

  async function moveCard(card: Card, targetColumn: Column) {
    if (!supabase || card.column_id === targetColumn.id || !user) return;
    setMessage("");
    const { data, error } = await supabase.rpc("kanban_move_card", {
      p_card_id: card.id,
      p_target_column_id: targetColumn.id,
      p_expected_revision: card.revision,
    });
    if (error) {
      setMessage(error.message);
      await loadBoardData();
      return;
    }
    if (!data) {
      setMessage("Card changed in another session. Refreshing the board to reconcile the revision.");
      await loadBoardData();
      return;
    }
    setCards((current) => current.map((item) => item.id === card.id ? data as Card : item));
  }

  async function signOut() {
    if (!supabase) return;
    await supabase.auth.signOut();
    setWorkspaces([]);
    setBoards([]);
    setColumns([]);
    setCards([]);
  }

  if (!supabase) {
    return (
      <main className="center-screen">
        <section className="auth-panel">
          <div className="brand-mark">P</div>
          <p className="eyebrow">HSO · PRE CONTROL PLANE</p>
          <h1>PRE Kanban</h1>
          <p className="muted">Set VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY to connect this board to the persistent backend.</p>
        </section>
      </main>
    );
  }

  if (authLoading) {
    return <main className="center-screen"><div className="loading-orbit" /><span className="muted">Connecting to PRE workspace…</span></main>;
  }

  if (!user) {
    return (
      <main className="center-screen">
        <section className="auth-panel">
          <div className="brand-mark">P</div>
          <p className="eyebrow">HSO · PRE CONTROL PLANE</p>
          <h1>Work moves.<br /><span>Evidence stays.</span></h1>
          <p className="muted">Sign in to access persistent PRE workspaces and boards. Access is governed by workspace membership and database policies.</p>
          <form onSubmit={signIn} className="stack-form">
            <label htmlFor="email">Work email</label>
            <input id="email" type="email" required value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@company.com" />
            <button className="primary-button" type="submit">{otpSent ? "Resend sign-in link" : "Send sign-in link"}</button>
          </form>
          {message && <p className="notice">{message}</p>}
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark small">P</div>
          <div><strong>PRE Kanban</strong><span>HSO Control Plane</span></div>
        </div>
        <div className="topbar-right">
          <span className="connection-pill"><i /> Connected</span>
          <span className="user-email">{user.email}</span>
          <button className="quiet-button" onClick={signOut}>Sign out</button>
        </div>
      </header>

      <section className="page-heading">
        <div>
          <p className="eyebrow">ROADMAP OPERATIONS</p>
          <h1>Keep the work visible.</h1>
          <p className="muted">Kanban tracks execution state. PRE remains authoritative for lifecycle gates and acceptance.</p>
        </div>
        <div className="heading-meta">
          <span className="meta-label">PERSISTENCE</span>
          <strong>Supabase Postgres</strong>
          <span className="meta-label">AUTHORIZATION</span>
          <strong>OAuth · RLS · Workspace roles</strong>
        </div>
      </section>

      {message && <div className="notice notice-inline"><span>{message}</span><button onClick={() => setMessage("")}>×</button></div>}

      <section className="toolbar">
        <div className="select-group">
          <label htmlFor="workspace">Workspace</label>
          <select id="workspace" value={workspaceId} onChange={(event) => setWorkspaceId(event.target.value)}>
            {workspaces.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
          </select>
          <form className="inline-create" onSubmit={createWorkspace}>
            <input aria-label="New workspace name" value={workspaceName} onChange={(event) => setWorkspaceName(event.target.value)} placeholder="New workspace" />
            <button type="submit" disabled={loading || !workspaceName.trim()}>Create</button>
          </form>
        </div>
        <div className="select-group board-select">
          <label htmlFor="board">Board</label>
          <select id="board" value={boardId} onChange={(event) => setBoardId(event.target.value)} disabled={!boards.length}>
            {boards.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
          </select>
          <form className="inline-create" onSubmit={createBoard}>
            <input aria-label="New board name" value={boardName} onChange={(event) => setBoardName(event.target.value)} placeholder="New board" disabled={!workspaceId} />
            <button type="submit" disabled={loading || !workspaceId || !boardName.trim()}>Create</button>
          </form>
        </div>
        <button className="refresh-button" onClick={() => void loadBoardData()} disabled={!boardId || loading}>↻ Refresh</button>
      </section>

      {!workspaces.length ? (
        <section className="empty-state">
          <div className="empty-icon">⌂</div>
          <h2>Create your first workspace</h2>
          <p className="muted">A workspace is the tenant and permission boundary. The creator becomes its owner.</p>
          <form className="empty-form" onSubmit={createWorkspace}>
            <input value={workspaceName} onChange={(event) => setWorkspaceName(event.target.value)} placeholder="e.g. HSO Operations" />
            <button className="primary-button" type="submit" disabled={loading || !workspaceName.trim()}>Create workspace</button>
          </form>
        </section>
      ) : !boards.length ? (
        <section className="empty-state">
          <div className="empty-icon">▤</div>
          <h2>Start with a board</h2>
          <p className="muted">A new board is created with Backlog, Ready, In Progress, Blocked, Review & Verification, and Done.</p>
          <form className="empty-form" onSubmit={createBoard}>
            <input value={boardName} onChange={(event) => setBoardName(event.target.value)} placeholder="e.g. PRE Development" />
            <button className="primary-button" type="submit" disabled={loading || !boardName.trim()}>Create board</button>
          </form>
        </section>
      ) : (
        <>
          <section className="board-summary">
            <div>
              <p className="eyebrow">ACTIVE BOARD</p>
              <h2>{board?.name}</h2>
            </div>
            <div className="summary-stats">
              <div><strong>{cards.length}</strong><span>Active cards</span></div>
              <div><strong>{columns.length}</strong><span>Workflow stages</span></div>
              <div><strong>{cards.filter((card) => card.column_id === columns.find((column) => column.semantic_key === "blocked")?.id).length}</strong><span>Blocked</span></div>
            </div>
          </section>
          <form className="quick-add" onSubmit={createCard}>
            <div className="quick-add-icon">＋</div>
            <input value={cardTitle} onChange={(event) => setCardTitle(event.target.value)} placeholder="Add a work item…" aria-label="Card title" />
            <select value={cardPriority} onChange={(event) => setCardPriority(event.target.value as Card["priority"])} aria-label="Card priority">
              <option value="critical">Critical</option><option value="high">High</option><option value="medium">Medium</option><option value="low">Low</option>
            </select>
            <input className="description-input" value={cardDescription} onChange={(event) => setCardDescription(event.target.value)} placeholder="Description (optional)" aria-label="Card description" />
            <button className="primary-button" type="submit" disabled={loading || !cardTitle.trim()}>Add card</button>
          </form>
          <section className="kanban-board" aria-label="Kanban board">
            {columns.map((column) => {
              const columnCards = cards.filter((card) => card.column_id === column.id).sort((a,b) => Number(a.position)-Number(b.position));
              return (
                <div className="kanban-column" key={column.id}
                  onDragOver={(event) => event.preventDefault()}
                  onDrop={(event) => {
                    event.preventDefault();
                    const id = event.dataTransfer.getData("text/plain");
                    const dragged = cards.find((card) => card.id === id);
                    if (dragged) void moveCard(dragged, column);
                  }}>
                  <div className="column-header">
                    <div className="column-title">
                      <span className={"column-dot " + column.semantic_key} />
                      <h3>{column.name}</h3>
                    </div>
                    <span className="count-pill">{columnCards.length}</span>
                  </div>
                  <div className="column-content">
                    {columnCards.map((card) => (
                      <article className="kanban-card" key={card.id} draggable
                        onDragStart={(event) => event.dataTransfer.setData("text/plain", card.id)}>
                        <div className="card-topline"><span className={"priority-tag " + card.priority}>{priorityLabel(card.priority)}</span><span className="revision-tag">r{card.revision}</span></div>
                        <h4>{card.title}</h4>
                        {card.description && <p>{card.description}</p>}
                        {card.acceptance_criteria && <div className="acceptance"><span>ACCEPTANCE</span>{card.acceptance_criteria}</div>}
                        <div className="card-footer"><span>{new Date(card.created_at).toLocaleDateString()}</span><span>PRE work item</span></div>
                        <div className="card-move-mobile">
                          <select value={column.id} onChange={(event) => {
                            const target = columns.find((item) => item.id === event.target.value);
                            if (target) void moveCard(card, target);
                          }} aria-label={"Move " + card.title}>
                            {columns.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
                          </select>
                        </div>
                      </article>
                    ))}
                    {!columnCards.length && <div className="column-empty">Drop cards here</div>}
                  </div>
                  <div className="column-footnote">Drag a card to change its visual state</div>
                </div>
              );
            })}
          </section>
        </>
      )}
      <footer className="app-footer"><span>PRE is the authority for R0–R9 status and milestone acceptance.</span><span>Board actions are revision-checked and recorded.</span></footer>
      {loading && <div className="busy-bar" />}
    </main>
  );
}
