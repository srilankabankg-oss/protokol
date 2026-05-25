export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'secretary' | 'chairman' | 'user';
  org_id?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export type MeetingLevel = 'strategic' | 'coordination' | 'operational' | 'situational';
export type MeetingStatus = 'preparation' | 'in_progress' | 'on_approval' | 'approved';

export interface MeetingListItem {
  meeting_id: string;
  title: string;
  level: MeetingLevel;
  status: MeetingStatus;
  notebook_path?: string;
  date?: string;
  updated_at: string;
}

export interface AgendaItem {
  agenda_id: string;
  title: string;
  position: number;
  is_completed: boolean;
}

export interface Participant {
  user_id: string;
  name: string;
  role: string;
  is_present: boolean;
}

export interface MeetingWorkspace {
  meeting_id: string;
  title: string;
  breadcrumbs: string[];
  status: MeetingStatus;
  content_markdown?: string;
  protocol_data?: any;
  participants: Participant[];
  agenda: AgendaItem[];
}

export interface MeetingCreatePayload {
  title: string;
  template_id?: string;
  project_id?: string;
  level: MeetingLevel;
  agenda_items: { position: number; title: string }[];
}

export interface MeetingCreateResponse {
  meeting_id: string;
  status: MeetingStatus;
  imported_legacy_tasks_count: number;
  celery_task_id?: string;
}

export type WorkflowStage = 'to_do' | 'in_progress' | 'escalated' | 'completed';
export type RaciRoleType = 'R' | 'A' | 'C' | 'I';

export interface TaskResponse {
  task_id: string;
  task_number: string;
  description: string;
  workflow_stage: WorkflowStage;
  raci_valid: boolean;
  is_ai_processed?: boolean;
  planned_start?: string;
  deadline?: string;
  created_at: string;
}

export interface RaciAssignment {
  user_id: string;
  role: RaciRoleType;
  name?: string;
}

export interface RaciResponse {
  task_id: string;
  assignments: RaciAssignment[];
  is_valid: boolean;
  errors: string[];
}

export interface SuggestedActionItem {
  temporary_id: string;
  extracted_description: string;
  confidence_score: number;
  json_schema_matched: boolean;
}

export interface DetectedRisk {
  risk_id: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  text_anchor: string;
  message: string;
}

export interface AIInsights {
  suggested_action_items: SuggestedActionItem[];
  detected_risks: DetectedRisk[];
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
}

export interface Organization {
  id: string;
  name: string;
  inn?: string;
  profile?: string;
  role?: string;
  parent_id?: string;
  is_active: boolean;
}

export interface Person {
  id: string;
  full_name: string;
  job_title?: string;
  org_id?: string;
}

export interface Contract {
  id: string;
  subject: string;
  end_date?: string;
  client_org_id: string;
  contractor_org_id: string;
  meeting_id?: string;
}