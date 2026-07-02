-- Add founder_blocked inbox status (founder decision required; not cancelled)
set search_path = public;

alter table noetfield_worker_inbox_queue
  drop constraint if exists noetfield_worker_inbox_queue_status_check;

alter table noetfield_worker_inbox_queue
  add constraint noetfield_worker_inbox_queue_status_check
  check (status in (
    'pending',
    'dispatched',
    'completed',
    'blocked',
    'cancelled',
    'founder_blocked'
  ));

comment on column noetfield_worker_inbox_queue.status is
  'pending=queue; founder_blocked=founder action required; cancelled=never run';
