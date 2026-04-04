# Spec for Remove Mixed Event Type

## Summary
Remove the `MIXED` event type from the system. Only three event types are supported: `PAYMENT`, `POTLUCK`, and `PRESENCE`. All references to `MIXED` — including model choices, business logic properties, seed data, templates, migrations, and documentation — must be cleaned up.

## Functional Requirements
- Remove `MIXED` from the `EventType` choices in `Event.EventType`.
- Delete `is_payment_event` property and replace all usages with a direct `event_type == EventType.PAYMENT` check.
- Delete `is_potluck_event` property and replace all usages with a direct `event_type == EventType.POTLUCK` check.
- Update `requires_participation` property: remove `MIXED` from the list; keep `POTLUCK` and `PRESENCE`.
- Remove the MIXED event block from the seed command.
- Remove the `mixed` check from the event form JavaScript.
- Create a new migration that removes `mixed` from the `event_type` field choices.
- Update `CLAUDE.md` to reflect only 3 event types.

## Tech Plan
- Dependencies: None.
- Structure:
  - `apps/events/models.py` — remove `MIXED` choice and update properties.
  - `apps/events/migrations/` — add a new migration to drop the `mixed` choice from the DB field.
  - `apps/core/management/commands/seed.py` — remove the MIXED event creation block and all references.
  - `templates/events/event_form.html` — remove `|| eventType === 'mixed'` from the JavaScript conditional.
  - `CLAUDE.md` — update event type list.

## Possible Edge Cases
- Existing `Event` records in the database with `event_type = 'mixed'` will become invalid after the migration. A data migration step may be needed to reassign or delete those records before removing the choice.
- The seed command creates MIXED events; removing the block will also remove the payment/participation records created for that event. Seeds should still be coherent after removal.

## Acceptance Criteria
- `EventType.MIXED` no longer exists anywhere in the codebase.
- The three valid types (`PAYMENT`, `POTLUCK`, `PRESENCE`) continue to work as before.
- `is_payment_event` and `is_potluck_event` properties no longer exist; call sites use direct `event_type` comparisons.
- `requires_participation` returns `True` for `POTLUCK` and `PRESENCE` only.
- Running `make migrate` applies cleanly with no errors.
- Running `make seed` (or equivalent) creates data without MIXED events.
- All existing tests pass.
- No `mixed` string appears in any Python, HTML, or Markdown file in the project.

## Open Questions
- None.

## Testing Guidelines
Create or update test file(s) in `apps/events/tests/` for the following cases, without going too heavy:
- `EventType` choices contain exactly `PAYMENT`, `POTLUCK`, and `PRESENCE` (no `MIXED`).
- `is_payment_event` and `is_potluck_event` are deleted; all call sites use direct `event_type` comparisons.
- `requires_participation` is `True` for `POTLUCK` and `PRESENCE`, `False` for `PAYMENT`.
