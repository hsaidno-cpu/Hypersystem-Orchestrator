export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "17.1"
  }
  public: {
    Tables: {
      hso_change_events: {
        Row: {
          after_state: Json
          before_state: Json
          delivery_id: string
          event_at: string
          event_type: string
          external_subject: string | null
          follow_up: string
          id: string
          impact: string
          provider: string
          related_milestone: string | null
          related_work_item_id: string | null
          source_url: string | null
          title: string
        }
        Insert: {
          after_state?: Json
          before_state?: Json
          delivery_id: string
          event_at?: string
          event_type: string
          external_subject?: string | null
          follow_up?: string
          id?: string
          impact?: string
          provider: string
          related_milestone?: string | null
          related_work_item_id?: string | null
          source_url?: string | null
          title: string
        }
        Update: {
          after_state?: Json
          before_state?: Json
          delivery_id?: string
          event_at?: string
          event_type?: string
          external_subject?: string | null
          follow_up?: string
          id?: string
          impact?: string
          provider?: string
          related_milestone?: string | null
          related_work_item_id?: string | null
          source_url?: string | null
          title?: string
        }
        Relationships: [
          {
            foreignKeyName: "hso_change_events_related_work_item_id_fkey"
            columns: ["related_work_item_id"]
            isOneToOne: false
            referencedRelation: "hso_verified_work_items_v"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "hso_change_events_related_work_item_id_fkey"
            columns: ["related_work_item_id"]
            isOneToOne: false
            referencedRelation: "hso_work_items"
            referencedColumns: ["id"]
          },
        ]
      }
      hso_completion_criteria: {
        Row: {
          acceptance_rule: Json
          criterion_key: string
          description: string | null
          evidence_record_id: string | null
          id: string
          last_evaluated_at: string | null
          project_key: string
          required: boolean
          scope_weight: number | null
          source_external_id: string | null
          source_key: string | null
          state: string
          title: string
        }
        Insert: {
          acceptance_rule?: Json
          criterion_key: string
          description?: string | null
          evidence_record_id?: string | null
          id?: string
          last_evaluated_at?: string | null
          project_key?: string
          required?: boolean
          scope_weight?: number | null
          source_external_id?: string | null
          source_key?: string | null
          state?: string
          title: string
        }
        Update: {
          acceptance_rule?: Json
          criterion_key?: string
          description?: string | null
          evidence_record_id?: string | null
          id?: string
          last_evaluated_at?: string | null
          project_key?: string
          required?: boolean
          scope_weight?: number | null
          source_external_id?: string | null
          source_key?: string | null
          state?: string
          title?: string
        }
        Relationships: [
          {
            foreignKeyName: "hso_completion_criteria_evidence_record_id_fkey"
            columns: ["evidence_record_id"]
            isOneToOne: false
            referencedRelation: "hso_evidence_records"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "hso_completion_criteria_source_key_fkey"
            columns: ["source_key"]
            isOneToOne: false
            referencedRelation: "hso_sources"
            referencedColumns: ["source_key"]
          },
        ]
      }
      hso_decision_runs: {
        Row: {
          blocked_actions: Json
          completion_gap: Json
          computed_at: string
          decision_inputs_complete: boolean
          decision_state: string
          engine_version: string
          id: string
          pending_decisions: Json
          policy_version: string
          primary_action: Json | null
          primary_work_item_id: string | null
          prompt_artifact_id: string | null
          ranking_snapshot: Json
          snapshot_coverage: Json
          source_health: Json
          source_sync_run_id: string | null
          supporting_actions: Json
        }
        Insert: {
          blocked_actions?: Json
          completion_gap?: Json
          computed_at?: string
          decision_inputs_complete?: boolean
          decision_state: string
          engine_version: string
          id?: string
          pending_decisions?: Json
          policy_version: string
          primary_action?: Json | null
          primary_work_item_id?: string | null
          prompt_artifact_id?: string | null
          ranking_snapshot?: Json
          snapshot_coverage?: Json
          source_health?: Json
          source_sync_run_id?: string | null
          supporting_actions?: Json
        }
        Update: {
          blocked_actions?: Json
          completion_gap?: Json
          computed_at?: string
          decision_inputs_complete?: boolean
          decision_state?: string
          engine_version?: string
          id?: string
          pending_decisions?: Json
          policy_version?: string
          primary_action?: Json | null
          primary_work_item_id?: string | null
          prompt_artifact_id?: string | null
          ranking_snapshot?: Json
          snapshot_coverage?: Json
          source_health?: Json
          source_sync_run_id?: string | null
          supporting_actions?: Json
        }
        Relationships: [
          {
            foreignKeyName: "hso_decision_runs_primary_work_item_id_fkey"
            columns: ["primary_work_item_id"]
            isOneToOne: false
            referencedRelation: "hso_verified_work_items_v"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "hso_decision_runs_primary_work_item_id_fkey"
            columns: ["primary_work_item_id"]
            isOneToOne: false
            referencedRelation: "hso_work_items"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "hso_decision_runs_source_sync_run_id_fkey"
            columns: ["source_sync_run_id"]
            isOneToOne: false
            referencedRelation: "hso_sync_runs"
            referencedColumns: ["id"]
          },
        ]
      }
      hso_decisions: {
        Row: {
          computed_at: string
          decision_type: string
          eligibility_state: string
          evidence_snapshot_id: string | null
          id: string
          policy_version: string
          priority_score: number | null
          rationale: Json
          work_item_id: string | null
        }
        Insert: {
          computed_at?: string
          decision_type: string
          eligibility_state: string
          evidence_snapshot_id?: string | null
          id?: string
          policy_version: string
          priority_score?: number | null
          rationale?: Json
          work_item_id?: string | null
        }
        Update: {
          computed_at?: string
          decision_type?: string
          eligibility_state?: string
          evidence_snapshot_id?: string | null
          id?: string
          policy_version?: string
          priority_score?: number | null
          rationale?: Json
          work_item_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "hso_decisions_evidence_snapshot_id_fkey"
            columns: ["evidence_snapshot_id"]
            isOneToOne: false
            referencedRelation: "hso_source_snapshots"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "hso_decisions_work_item_id_fkey"
            columns: ["work_item_id"]
            isOneToOne: false
            referencedRelation: "hso_verified_work_items_v"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "hso_decisions_work_item_id_fkey"
            columns: ["work_item_id"]
            isOneToOne: false
            referencedRelation: "hso_work_items"
            referencedColumns: ["id"]
          },
        ]
      }
      hso_evidence_records: {
        Row: {
          artifact_url: string | null
          branch_ref: string | null
          ci_run_url: string | null
          claim_supported: string | null
          commit_sha: string | null
          content_digest: string | null
          evidence_id: string | null
          evidence_state: string
          evidence_type: string
          external_id: string
          freshness: string
          id: string
          known_limitation: string | null
          observed_at: string
          payload: Json
          pr_url: string | null
          related_work_item: string | null
          repository_url: string | null
          source_key: string
          source_locator: string | null
          source_url: string | null
          title: string
          verified_at: string | null
          verifier_role: string | null
        }
        Insert: {
          artifact_url?: string | null
          branch_ref?: string | null
          ci_run_url?: string | null
          claim_supported?: string | null
          commit_sha?: string | null
          content_digest?: string | null
          evidence_id?: string | null
          evidence_state?: string
          evidence_type?: string
          external_id: string
          freshness?: string
          id?: string
          known_limitation?: string | null
          observed_at?: string
          payload?: Json
          pr_url?: string | null
          related_work_item?: string | null
          repository_url?: string | null
          source_key: string
          source_locator?: string | null
          source_url?: string | null
          title: string
          verified_at?: string | null
          verifier_role?: string | null
        }
        Update: {
          artifact_url?: string | null
          branch_ref?: string | null
          ci_run_url?: string | null
          claim_supported?: string | null
          commit_sha?: string | null
          content_digest?: string | null
          evidence_id?: string | null
          evidence_state?: string
          evidence_type?: string
          external_id?: string
          freshness?: string
          id?: string
          known_limitation?: string | null
          observed_at?: string
          payload?: Json
          pr_url?: string | null
          related_work_item?: string | null
          repository_url?: string | null
          source_key?: string
          source_locator?: string | null
          source_url?: string | null
          title?: string
          verified_at?: string | null
          verifier_role?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "hso_evidence_records_source_key_fkey"
            columns: ["source_key"]
            isOneToOne: false
            referencedRelation: "hso_sources"
            referencedColumns: ["source_key"]
          },
        ]
      }
      hso_executions: {
        Row: {
          acceptance_result: string | null
          audit_url: string | null
          changed_files: Json
          completed_at: string | null
          correlation_id: string | null
          executing_agent: string | null
          execution_id: string | null
          execution_receipt_url: string | null
          external_id: string
          failure_recovery_summary: string | null
          github_run_id: string | null
          github_workflow_url: string | null
          head_commit_sha: string | null
          id: string
          observed_at: string
          owner_role: string | null
          plan_artifact_url: string | null
          pre_stage: string | null
          raw_properties: Json
          related_work_item: string | null
          retry_count: number
          run_name: string
          run_type: string | null
          source_commit: string | null
          source_key: string
          source_repository: string | null
          source_url: string | null
          status: string
          stop_reason: string | null
          supporting_evidence: Json
          supporting_specialists: Json
          target_branch: string | null
          validation_summary: string | null
          verification_state: string | null
        }
        Insert: {
          acceptance_result?: string | null
          audit_url?: string | null
          changed_files?: Json
          completed_at?: string | null
          correlation_id?: string | null
          executing_agent?: string | null
          execution_id?: string | null
          execution_receipt_url?: string | null
          external_id: string
          failure_recovery_summary?: string | null
          github_run_id?: string | null
          github_workflow_url?: string | null
          head_commit_sha?: string | null
          id?: string
          observed_at?: string
          owner_role?: string | null
          plan_artifact_url?: string | null
          pre_stage?: string | null
          raw_properties?: Json
          related_work_item?: string | null
          retry_count?: number
          run_name: string
          run_type?: string | null
          source_commit?: string | null
          source_key: string
          source_repository?: string | null
          source_url?: string | null
          status?: string
          stop_reason?: string | null
          supporting_evidence?: Json
          supporting_specialists?: Json
          target_branch?: string | null
          validation_summary?: string | null
          verification_state?: string | null
        }
        Update: {
          acceptance_result?: string | null
          audit_url?: string | null
          changed_files?: Json
          completed_at?: string | null
          correlation_id?: string | null
          executing_agent?: string | null
          execution_id?: string | null
          execution_receipt_url?: string | null
          external_id?: string
          failure_recovery_summary?: string | null
          github_run_id?: string | null
          github_workflow_url?: string | null
          head_commit_sha?: string | null
          id?: string
          observed_at?: string
          owner_role?: string | null
          plan_artifact_url?: string | null
          pre_stage?: string | null
          raw_properties?: Json
          related_work_item?: string | null
          retry_count?: number
          run_name?: string
          run_type?: string | null
          source_commit?: string | null
          source_key?: string
          source_repository?: string | null
          source_url?: string | null
          status?: string
          stop_reason?: string | null
          supporting_evidence?: Json
          supporting_specialists?: Json
          target_branch?: string | null
          validation_summary?: string | null
          verification_state?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "hso_executions_source_key_fkey"
            columns: ["source_key"]
            isOneToOne: false
            referencedRelation: "hso_sources"
            referencedColumns: ["source_key"]
          },
        ]
      }
      hso_integration_events: {
        Row: {
          delivery_id: string
          event_type: string
          external_subject: string | null
          id: string
          last_error: string | null
          payload: Json
          payload_hash: string
          processed_at: string | null
          processing_state: string
          provider: string
          received_at: string
        }
        Insert: {
          delivery_id: string
          event_type: string
          external_subject?: string | null
          id?: string
          last_error?: string | null
          payload?: Json
          payload_hash: string
          processed_at?: string | null
          processing_state?: string
          provider: string
          received_at?: string
        }
        Update: {
          delivery_id?: string
          event_type?: string
          external_subject?: string | null
          id?: string
          last_error?: string | null
          payload?: Json
          payload_hash?: string
          processed_at?: string | null
          processing_state?: string
          provider?: string
          received_at?: string
        }
        Relationships: []
      }
      hso_issue_records: {
        Row: {
          affected_milestones: Json
          affected_work_items: Json
          detected_at: string
          external_id: string | null
          first_seen_at: string
          id: string
          impact: string | null
          issue_type: string
          last_seen_at: string
          location: string | null
          occurrence_count: number
          resolution: string | null
          root_cause: string | null
          root_cause_key: string
          root_cause_state: string
          severity: string
          source_key: string | null
          verification_evidence_url: string | null
          verification_state: string
        }
        Insert: {
          affected_milestones?: Json
          affected_work_items?: Json
          detected_at?: string
          external_id?: string | null
          first_seen_at?: string
          id?: string
          impact?: string | null
          issue_type: string
          last_seen_at?: string
          location?: string | null
          occurrence_count?: number
          resolution?: string | null
          root_cause?: string | null
          root_cause_key: string
          root_cause_state?: string
          severity: string
          source_key?: string | null
          verification_evidence_url?: string | null
          verification_state?: string
        }
        Update: {
          affected_milestones?: Json
          affected_work_items?: Json
          detected_at?: string
          external_id?: string | null
          first_seen_at?: string
          id?: string
          impact?: string | null
          issue_type?: string
          last_seen_at?: string
          location?: string | null
          occurrence_count?: number
          resolution?: string | null
          root_cause?: string | null
          root_cause_key?: string
          root_cause_state?: string
          severity?: string
          source_key?: string | null
          verification_evidence_url?: string | null
          verification_state?: string
        }
        Relationships: [
          {
            foreignKeyName: "hso_issue_records_source_key_fkey"
            columns: ["source_key"]
            isOneToOne: false
            referencedRelation: "hso_sources"
            referencedColumns: ["source_key"]
          },
        ]
      }
      hso_members: {
        Row: {
          active: boolean
          created_at: string
          created_by: string | null
          role: string
          user_id: string
        }
        Insert: {
          active?: boolean
          created_at?: string
          created_by?: string | null
          role: string
          user_id: string
        }
        Update: {
          active?: boolean
          created_at?: string
          created_by?: string | null
          role?: string
          user_id?: string
        }
        Relationships: []
      }
      hso_notifications: {
        Row: {
          category: string
          created_at: string
          dedupe_key: string
          external_id: string | null
          id: string
          message: string
          metadata: Json
          resolved_at: string | null
          severity: string
          source_key: string | null
          state: string
        }
        Insert: {
          category: string
          created_at?: string
          dedupe_key: string
          external_id?: string | null
          id?: string
          message: string
          metadata?: Json
          resolved_at?: string | null
          severity: string
          source_key?: string | null
          state?: string
        }
        Update: {
          category?: string
          created_at?: string
          dedupe_key?: string
          external_id?: string | null
          id?: string
          message?: string
          metadata?: Json
          resolved_at?: string | null
          severity?: string
          source_key?: string | null
          state?: string
        }
        Relationships: [
          {
            foreignKeyName: "hso_notifications_source_key_fkey"
            columns: ["source_key"]
            isOneToOne: false
            referencedRelation: "hso_sources"
            referencedColumns: ["source_key"]
          },
        ]
      }
      hso_progress_snapshots: {
        Row: {
          active_count: number
          baseline_start_date: string | null
          blocked_count: number
          computed_at: string
          expected_progress_pct: number | null
          failed_count: number
          group_type: string
          id: string
          is_publishable: boolean
          measurement_reasons: Json
          measurement_state: string
          methodology_version: string
          milestone_key: string | null
          milestone_title: string | null
          partial_weighted_progress_pct: number | null
          pending_approval_count: number
          project_key: string
          scope_decision_coverage_pct: number | null
          scope_hash: string | null
          scope_weight_total: number
          source_sync_run_id: string | null
          target_date: string | null
          total_work_items: number
          unweighted_work_items: number
          verified_count: number
          verified_weight: number
          weight_approval_coverage_pct: number | null
          weight_coverage_pct: number | null
          weighted_progress_pct: number | null
          weighted_work_items: number
        }
        Insert: {
          active_count?: number
          baseline_start_date?: string | null
          blocked_count?: number
          computed_at?: string
          expected_progress_pct?: number | null
          failed_count?: number
          group_type?: string
          id?: string
          is_publishable?: boolean
          measurement_reasons?: Json
          measurement_state?: string
          methodology_version?: string
          milestone_key?: string | null
          milestone_title?: string | null
          partial_weighted_progress_pct?: number | null
          pending_approval_count?: number
          project_key?: string
          scope_decision_coverage_pct?: number | null
          scope_hash?: string | null
          scope_weight_total?: number
          source_sync_run_id?: string | null
          target_date?: string | null
          total_work_items?: number
          unweighted_work_items?: number
          verified_count?: number
          verified_weight?: number
          weight_approval_coverage_pct?: number | null
          weight_coverage_pct?: number | null
          weighted_progress_pct?: number | null
          weighted_work_items?: number
        }
        Update: {
          active_count?: number
          baseline_start_date?: string | null
          blocked_count?: number
          computed_at?: string
          expected_progress_pct?: number | null
          failed_count?: number
          group_type?: string
          id?: string
          is_publishable?: boolean
          measurement_reasons?: Json
          measurement_state?: string
          methodology_version?: string
          milestone_key?: string | null
          milestone_title?: string | null
          partial_weighted_progress_pct?: number | null
          pending_approval_count?: number
          project_key?: string
          scope_decision_coverage_pct?: number | null
          scope_hash?: string | null
          scope_weight_total?: number
          source_sync_run_id?: string | null
          target_date?: string | null
          total_work_items?: number
          unweighted_work_items?: number
          verified_count?: number
          verified_weight?: number
          weight_approval_coverage_pct?: number | null
          weight_coverage_pct?: number | null
          weighted_progress_pct?: number | null
          weighted_work_items?: number
        }
        Relationships: [
          {
            foreignKeyName: "hso_progress_snapshots_source_sync_run_id_fkey"
            columns: ["source_sync_run_id"]
            isOneToOne: false
            referencedRelation: "hso_sync_runs"
            referencedColumns: ["id"]
          },
        ]
      }
      hso_prompt_artifacts: {
        Row: {
          context_hash: string | null
          created_at: string
          created_from_decision_run: string | null
          id: string
          prompt_payload: Json
          prompt_state: string
          prompt_text: string
          prompt_version: string
          snapshot_id: string | null
          task_key: string | null
          work_item_id: string | null
        }
        Insert: {
          context_hash?: string | null
          created_at?: string
          created_from_decision_run?: string | null
          id?: string
          prompt_payload?: Json
          prompt_state?: string
          prompt_text: string
          prompt_version: string
          snapshot_id?: string | null
          task_key?: string | null
          work_item_id?: string | null
        }
        Update: {
          context_hash?: string | null
          created_at?: string
          created_from_decision_run?: string | null
          id?: string
          prompt_payload?: Json
          prompt_state?: string
          prompt_text?: string
          prompt_version?: string
          snapshot_id?: string | null
          task_key?: string | null
          work_item_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "hso_prompt_artifacts_created_from_decision_run_fkey"
            columns: ["created_from_decision_run"]
            isOneToOne: false
            referencedRelation: "hso_decision_runs"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "hso_prompt_artifacts_snapshot_id_fkey"
            columns: ["snapshot_id"]
            isOneToOne: false
            referencedRelation: "hso_source_snapshots"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "hso_prompt_artifacts_work_item_id_fkey"
            columns: ["work_item_id"]
            isOneToOne: false
            referencedRelation: "hso_verified_work_items_v"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "hso_prompt_artifacts_work_item_id_fkey"
            columns: ["work_item_id"]
            isOneToOne: false
            referencedRelation: "hso_work_items"
            referencedColumns: ["id"]
          },
        ]
      }
      hso_source_snapshots: {
        Row: {
          completeness_state: string
          content_hash: string
          freshness: string
          id: string
          is_complete: boolean
          observed_at: string
          page_count: number
          pagination_complete: boolean
          pagination_pages: number
          record_count: number
          scope_hash: string | null
          snapshot: Json
          source_key: string
          source_total_count: number | null
          sync_run_id: string | null
        }
        Insert: {
          completeness_state?: string
          content_hash: string
          freshness?: string
          id?: string
          is_complete?: boolean
          observed_at?: string
          page_count?: number
          pagination_complete?: boolean
          pagination_pages?: number
          record_count?: number
          scope_hash?: string | null
          snapshot?: Json
          source_key: string
          source_total_count?: number | null
          sync_run_id?: string | null
        }
        Update: {
          completeness_state?: string
          content_hash?: string
          freshness?: string
          id?: string
          is_complete?: boolean
          observed_at?: string
          page_count?: number
          pagination_complete?: boolean
          pagination_pages?: number
          record_count?: number
          scope_hash?: string | null
          snapshot?: Json
          source_key?: string
          source_total_count?: number | null
          sync_run_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "hso_source_snapshots_source_key_fkey"
            columns: ["source_key"]
            isOneToOne: false
            referencedRelation: "hso_sources"
            referencedColumns: ["source_key"]
          },
          {
            foreignKeyName: "hso_source_snapshots_sync_run_id_fkey"
            columns: ["sync_run_id"]
            isOneToOne: false
            referencedRelation: "hso_sync_runs"
            referencedColumns: ["id"]
          },
        ]
      }
      hso_sources: {
        Row: {
          authority_role: string
          created_at: string
          display_name: string
          enabled: boolean
          freshness_seconds: number
          last_complete_at: string | null
          last_error: string | null
          last_event_at: string | null
          last_record_count: number | null
          last_scope_hash: string | null
          last_success_at: string | null
          last_sync_at: string | null
          metadata: Json
          provider: string
          source_key: string
          source_uri: string | null
          status: string
          updated_at: string
        }
        Insert: {
          authority_role: string
          created_at?: string
          display_name: string
          enabled?: boolean
          freshness_seconds?: number
          last_complete_at?: string | null
          last_error?: string | null
          last_event_at?: string | null
          last_record_count?: number | null
          last_scope_hash?: string | null
          last_success_at?: string | null
          last_sync_at?: string | null
          metadata?: Json
          provider: string
          source_key: string
          source_uri?: string | null
          status?: string
          updated_at?: string
        }
        Update: {
          authority_role?: string
          created_at?: string
          display_name?: string
          enabled?: boolean
          freshness_seconds?: number
          last_complete_at?: string | null
          last_error?: string | null
          last_event_at?: string | null
          last_record_count?: number | null
          last_scope_hash?: string | null
          last_success_at?: string | null
          last_sync_at?: string | null
          metadata?: Json
          provider?: string
          source_key?: string
          source_uri?: string | null
          status?: string
          updated_at?: string
        }
        Relationships: []
      }
      hso_sync_runs: {
        Row: {
          correlation_id: string | null
          created_at: string
          error_summary: string | null
          finished_at: string | null
          id: string
          records_seen: number
          records_upserted: number
          source_results: Json
          started_at: string
          status: string
          trigger_kind: string
        }
        Insert: {
          correlation_id?: string | null
          created_at?: string
          error_summary?: string | null
          finished_at?: string | null
          id?: string
          records_seen?: number
          records_upserted?: number
          source_results?: Json
          started_at?: string
          status?: string
          trigger_kind: string
        }
        Update: {
          correlation_id?: string | null
          created_at?: string
          error_summary?: string | null
          finished_at?: string | null
          id?: string
          records_seen?: number
          records_upserted?: number
          source_results?: Json
          started_at?: string
          status?: string
          trigger_kind?: string
        }
        Relationships: []
      }
      hso_work_item_history: {
        Row: {
          changed_at: string
          changed_fields: Json
          external_id: string
          from_execution_state: string | null
          from_gate_state: string | null
          from_verification_state: string | null
          id: string
          observed_payload: Json
          source_key: string
          source_updated_at: string | null
          source_url: string | null
          to_execution_state: string | null
          to_gate_state: string | null
          to_verification_state: string | null
          transition_key: string
          work_item_id: string
        }
        Insert: {
          changed_at?: string
          changed_fields?: Json
          external_id: string
          from_execution_state?: string | null
          from_gate_state?: string | null
          from_verification_state?: string | null
          id?: string
          observed_payload?: Json
          source_key: string
          source_updated_at?: string | null
          source_url?: string | null
          to_execution_state?: string | null
          to_gate_state?: string | null
          to_verification_state?: string | null
          transition_key: string
          work_item_id: string
        }
        Update: {
          changed_at?: string
          changed_fields?: Json
          external_id?: string
          from_execution_state?: string | null
          from_gate_state?: string | null
          from_verification_state?: string | null
          id?: string
          observed_payload?: Json
          source_key?: string
          source_updated_at?: string | null
          source_url?: string | null
          to_execution_state?: string | null
          to_gate_state?: string | null
          to_verification_state?: string | null
          transition_key?: string
          work_item_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "hso_work_item_history_source_key_fkey"
            columns: ["source_key"]
            isOneToOne: false
            referencedRelation: "hso_sources"
            referencedColumns: ["source_key"]
          },
          {
            foreignKeyName: "hso_work_item_history_work_item_id_fkey"
            columns: ["work_item_id"]
            isOneToOne: false
            referencedRelation: "hso_verified_work_items_v"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "hso_work_item_history_work_item_id_fkey"
            columns: ["work_item_id"]
            isOneToOne: false
            referencedRelation: "hso_work_items"
            referencedColumns: ["id"]
          },
        ]
      }
      hso_work_items: {
        Row: {
          acceptance_criteria: string | null
          accountable_role: string | null
          approval_state: string | null
          baseline_start_date: string | null
          blocker: string | null
          change_surface: string | null
          ci_commit_sha: string | null
          critical_path_impact: number | null
          dependencies: Json
          dependency_unlock_value: number | null
          dependency_work_item_ids: Json
          ecosystem_stage: string | null
          effort_efficiency: number | null
          estimated_effort_hours: number | null
          evidence_confidence: number | null
          execution_risk: string | null
          execution_state: string
          execution_target: string | null
          expected_progress_pct: number | null
          external_id: string
          gate_state: string
          head_commit_sha: string | null
          id: string
          item_key: string | null
          milestone_key: string | null
          next_action: string | null
          observed_at: string
          parent_milestone_id: string | null
          pre_stage: string | null
          priority: string | null
          progress_basis: string | null
          progress_percent: number | null
          project_area: string | null
          raw_properties: Json
          record_type: string | null
          requires_human_approval: boolean | null
          reviewed_commit_sha: string | null
          risk_reduction: number | null
          scope_decision_at: string | null
          scope_decision_by: string | null
          scope_decision_rationale: string | null
          scope_inclusion_state: string
          scope_weight: number | null
          scope_weight_approval: string
          scope_weight_approved_at: string | null
          scope_weight_approved_by: string | null
          security_disposition: string | null
          source_commit: string | null
          source_key: string
          source_updated_at: string | null
          source_url: string | null
          source_verified_at: string | null
          target_branch: string | null
          target_date: string | null
          title: string
          urgency: number | null
          verification_state: string
          weight_rationale: string | null
        }
        Insert: {
          acceptance_criteria?: string | null
          accountable_role?: string | null
          approval_state?: string | null
          baseline_start_date?: string | null
          blocker?: string | null
          change_surface?: string | null
          ci_commit_sha?: string | null
          critical_path_impact?: number | null
          dependencies?: Json
          dependency_unlock_value?: number | null
          dependency_work_item_ids?: Json
          ecosystem_stage?: string | null
          effort_efficiency?: number | null
          estimated_effort_hours?: number | null
          evidence_confidence?: number | null
          execution_risk?: string | null
          execution_state?: string
          execution_target?: string | null
          expected_progress_pct?: number | null
          external_id: string
          gate_state?: string
          head_commit_sha?: string | null
          id?: string
          item_key?: string | null
          milestone_key?: string | null
          next_action?: string | null
          observed_at?: string
          parent_milestone_id?: string | null
          pre_stage?: string | null
          priority?: string | null
          progress_basis?: string | null
          progress_percent?: number | null
          project_area?: string | null
          raw_properties?: Json
          record_type?: string | null
          requires_human_approval?: boolean | null
          reviewed_commit_sha?: string | null
          risk_reduction?: number | null
          scope_decision_at?: string | null
          scope_decision_by?: string | null
          scope_decision_rationale?: string | null
          scope_inclusion_state?: string
          scope_weight?: number | null
          scope_weight_approval?: string
          scope_weight_approved_at?: string | null
          scope_weight_approved_by?: string | null
          security_disposition?: string | null
          source_commit?: string | null
          source_key: string
          source_updated_at?: string | null
          source_url?: string | null
          source_verified_at?: string | null
          target_branch?: string | null
          target_date?: string | null
          title: string
          urgency?: number | null
          verification_state?: string
          weight_rationale?: string | null
        }
        Update: {
          acceptance_criteria?: string | null
          accountable_role?: string | null
          approval_state?: string | null
          baseline_start_date?: string | null
          blocker?: string | null
          change_surface?: string | null
          ci_commit_sha?: string | null
          critical_path_impact?: number | null
          dependencies?: Json
          dependency_unlock_value?: number | null
          dependency_work_item_ids?: Json
          ecosystem_stage?: string | null
          effort_efficiency?: number | null
          estimated_effort_hours?: number | null
          evidence_confidence?: number | null
          execution_risk?: string | null
          execution_state?: string
          execution_target?: string | null
          expected_progress_pct?: number | null
          external_id?: string
          gate_state?: string
          head_commit_sha?: string | null
          id?: string
          item_key?: string | null
          milestone_key?: string | null
          next_action?: string | null
          observed_at?: string
          parent_milestone_id?: string | null
          pre_stage?: string | null
          priority?: string | null
          progress_basis?: string | null
          progress_percent?: number | null
          project_area?: string | null
          raw_properties?: Json
          record_type?: string | null
          requires_human_approval?: boolean | null
          reviewed_commit_sha?: string | null
          risk_reduction?: number | null
          scope_decision_at?: string | null
          scope_decision_by?: string | null
          scope_decision_rationale?: string | null
          scope_inclusion_state?: string
          scope_weight?: number | null
          scope_weight_approval?: string
          scope_weight_approved_at?: string | null
          scope_weight_approved_by?: string | null
          security_disposition?: string | null
          source_commit?: string | null
          source_key?: string
          source_updated_at?: string | null
          source_url?: string | null
          source_verified_at?: string | null
          target_branch?: string | null
          target_date?: string | null
          title?: string
          urgency?: number | null
          verification_state?: string
          weight_rationale?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "hso_work_items_source_key_fkey"
            columns: ["source_key"]
            isOneToOne: false
            referencedRelation: "hso_sources"
            referencedColumns: ["source_key"]
          },
        ]
      }
    }
    Views: {
      hso_verified_work_items_v: {
        Row: {
          acceptance_criteria: string | null
          approval_state: string | null
          blocker: string | null
          change_surface: string | null
          ci_commit_sha: string | null
          critical_path_impact: number | null
          dependencies: Json | null
          dependency_unlock_value: number | null
          dependency_work_item_ids: Json | null
          ecosystem_stage: string | null
          effort_efficiency: number | null
          estimated_effort_hours: number | null
          evidence_confidence: number | null
          evidence_verified: boolean | null
          execution_risk: string | null
          execution_state: string | null
          execution_target: string | null
          external_id: string | null
          gate_state: string | null
          head_commit_sha: string | null
          id: string | null
          item_key: string | null
          milestone_key: string | null
          next_action: string | null
          observed_at: string | null
          pre_stage: string | null
          priority: string | null
          progress_basis: string | null
          progress_percent: number | null
          project_area: string | null
          raw_properties: Json | null
          record_type: string | null
          requires_human_approval: boolean | null
          reviewed_commit_sha: string | null
          risk_reduction: number | null
          scope_weight: number | null
          security_disposition: string | null
          source_commit: string | null
          source_key: string | null
          source_updated_at: string | null
          source_url: string | null
          source_verified_at: string | null
          target_branch: string | null
          target_date: string | null
          title: string | null
          urgency: number | null
          verification_state: string | null
          verified_completion: boolean | null
          weight_rationale: string | null
        }
        Insert: {
          acceptance_criteria?: string | null
          approval_state?: string | null
          blocker?: string | null
          change_surface?: string | null
          ci_commit_sha?: string | null
          critical_path_impact?: number | null
          dependencies?: Json | null
          dependency_unlock_value?: number | null
          dependency_work_item_ids?: Json | null
          ecosystem_stage?: string | null
          effort_efficiency?: number | null
          estimated_effort_hours?: number | null
          evidence_confidence?: number | null
          evidence_verified?: never
          execution_risk?: string | null
          execution_state?: string | null
          execution_target?: string | null
          external_id?: string | null
          gate_state?: string | null
          head_commit_sha?: string | null
          id?: string | null
          item_key?: string | null
          milestone_key?: string | null
          next_action?: string | null
          observed_at?: string | null
          pre_stage?: string | null
          priority?: string | null
          progress_basis?: string | null
          progress_percent?: number | null
          project_area?: string | null
          raw_properties?: Json | null
          record_type?: string | null
          requires_human_approval?: boolean | null
          reviewed_commit_sha?: string | null
          risk_reduction?: number | null
          scope_weight?: number | null
          security_disposition?: string | null
          source_commit?: string | null
          source_key?: string | null
          source_updated_at?: string | null
          source_url?: string | null
          source_verified_at?: string | null
          target_branch?: string | null
          target_date?: string | null
          title?: string | null
          urgency?: number | null
          verification_state?: string | null
          verified_completion?: never
          weight_rationale?: string | null
        }
        Update: {
          acceptance_criteria?: string | null
          approval_state?: string | null
          blocker?: string | null
          change_surface?: string | null
          ci_commit_sha?: string | null
          critical_path_impact?: number | null
          dependencies?: Json | null
          dependency_unlock_value?: number | null
          dependency_work_item_ids?: Json | null
          ecosystem_stage?: string | null
          effort_efficiency?: number | null
          estimated_effort_hours?: number | null
          evidence_confidence?: number | null
          evidence_verified?: never
          execution_risk?: string | null
          execution_state?: string | null
          execution_target?: string | null
          external_id?: string | null
          gate_state?: string | null
          head_commit_sha?: string | null
          id?: string | null
          item_key?: string | null
          milestone_key?: string | null
          next_action?: string | null
          observed_at?: string | null
          pre_stage?: string | null
          priority?: string | null
          progress_basis?: string | null
          progress_percent?: number | null
          project_area?: string | null
          raw_properties?: Json | null
          record_type?: string | null
          requires_human_approval?: boolean | null
          reviewed_commit_sha?: string | null
          risk_reduction?: number | null
          scope_weight?: number | null
          security_disposition?: string | null
          source_commit?: string | null
          source_key?: string | null
          source_updated_at?: string | null
          source_url?: string | null
          source_verified_at?: string | null
          target_branch?: string | null
          target_date?: string | null
          title?: string | null
          urgency?: number | null
          verification_state?: string | null
          verified_completion?: never
          weight_rationale?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "hso_work_items_source_key_fkey"
            columns: ["source_key"]
            isOneToOne: false
            referencedRelation: "hso_sources"
            referencedColumns: ["source_key"]
          },
        ]
      }
    }
    Functions: {
      hso_get_notion_webhook_verification_token: {
        Args: never
        Returns: string
      }
      hso_register_notion_webhook_verification_token: {
        Args: { p_token: string }
        Returns: boolean
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends (DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never) = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends (PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never) = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {},
  },
} as const
