# User Scenarios — Meeting Protocol Module

## Scenario 1: Admin Creating Organizations and People

**Actor**: Admin
**Goal**: Populate the system with organizations and external participants

1. Admin navigates to Admin panel
2. Selects Organizations tab, sees list of existing orgs
3. Clicks Add, fills in name, INN, profile, role
4. Saves, org appears in list
5. Selects People tab, clicks Add
6. Fills in full_name, job_title, selects org from dropdown
7. Creates external participant (Person) linked to organization

**Expected**: Organization and Person records stored in DB, available for meeting participant selection.

---

## Scenario 2: Creating Meeting with External Participants

**Actor**: Secretary
**Goal**: Create a meeting with both registered users and external people

1. Secretary creates meeting via Create Meeting modal
2. Opens meeting editor, adds participants
3. Selects from registered Users AND external People
4. Meeting participant list shows both types with appropriate labels
5. Proceeds to Start Work

**Expected**: Participant list includes both User-linked and Person-linked entries.

---

## Scenario 3: Full Meeting Lifecycle

**Actor**: Secretary, then Chairman
**Goal**: Complete meeting from preparation to approval

1. Secretary creates meeting, status: preparation
2. Edits content, autosave triggers protocol parsing
3. Clicks Start Work, status: in_progress
4. Adds more content during meeting
5. Clicks Finalize, status: on_approval
6. Chairman opens meeting, reviews tabular protocol
7. Clicks Approve, status: approved
8. PDF and XLSX exports generated via Celery tasks

**Expected**: Meeting transitions through all 4 states. Protocol parsed. Exports generated.

---

## Scenario 4: AI Parsing Meeting Notes into Tabular Protocol

**Actor**: Secretary
**Goal**: Convert free-text markdown into structured tabular data

1. Secretary types notes in GOST-compliant format: SLUSHALI / VYSTUPILI / POSTANOVILI
2. Autosave triggers parse_notes_to_protocol()
3. Protocol data stored as JSONB with sections: heard, spoke, decided
4. Each entry has speaker/topic/responsible/deadline fields

**Expected**: Structured tabular data available alongside raw markdown content.

---

## Scenario 5: Importing Protocol from File

**Actor**: Secretary
**Goal**: Upload a Word/Excel document and get a draft protocol

1. Secretary uploads .docx file containing meeting minutes
2. System parses file content, extracts text
3. AI parser extracts: sections, participants, action items
4. Returns protocol draft with structured data
5. If mandatory fields missing, shows clarification prompt

**Expected**: Draft protocol returned. User can review and save to a meeting.

---

## Scenario 6: View as Role (Admin Simulation)

**Actor**: Admin
**Goal**: Preview the application from another user perspective

1. Admin navigates to View as Role feature
2. Selects role: secretary / chairman / user
3. Session switches to simulated role with appropriate permissions
4. All UI elements reflect selected role
5. Admin can switch back to admin role at any time

**Expected**: Isolated session state. No data corruption.