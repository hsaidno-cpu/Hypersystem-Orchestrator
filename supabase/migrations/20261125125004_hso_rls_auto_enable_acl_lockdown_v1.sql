-- Restrict execution of the SECURITY DEFINER RLS event-trigger helper.
-- The ensure_rls event trigger runs in the database's trusted event-trigger context.
-- Do not expose this function as a PostgREST/Data API RPC to client roles.

REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION public.rls_auto_enable() FROM anon, authenticated, service_role;
