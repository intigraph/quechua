# Scheduled-job profile

This explicit operational profile represents a recurring occurrence as a
Schema.org Event with `eventSchedule` pointing to a Schedule and
`potentialAction` pointing to the declared job Action. It adds no bespoke class
or public-vocabulary property. All public terms are checked against the pinned
Schema.org term list. See [Schedule](https://schema.org/Schedule) and
[eventSchedule](https://schema.org/eventSchedule).

The Action carries a name, immutable manifest revision, declared provenance,
owner, explicit enablement, host IRI and command-manifest target IRI. A target
IRI is a reference for an independently admitted local manifest, never shell
text to execute from the graph. Host identity must also be resolved by the
consumer. Disabled declarations remain fully described and queryable.

The first reader contract supports positive fixed day/hour/minute/second
intervals, an explicit timezone and offset-aware activation anchor. Calendar
qualifiers, exceptions, repeat counts and additional wall-clock bounds are
refused until a reader explicitly supports them. They are never silently
approximated as fixed intervals. Complex cron jobs stay in their original
schedule until a compatible migration is proved. Multiple schedules per Event
are permitted, but consumers must define overlap deduplication before admission.

Schedule bounds are distinct from actual Action activity times. Keep the
existing [valid-time profile](../valid-time.json): an activity starts and ends
when performed; a deadline is not its end. A recurring Event carries its bounds
on the Schedule, not conflicting Event start/end dates.

This file is an opt-in profile, not an automatic global store policy. The
`eventSchedule` target selects every such subject in the validated graph;
loading it globally could also select unrelated calendar series. Check actual
target coverage and use the scheduled-job data scope or obtain explicit global
policy approval before installation. Unrelated Events and Actions without an
`eventSchedule` are not required to become job declarations. Publishing the
profile does not load it, authorize commands, register a key, create jobs,
activate a scheduler, or retire cron lines.

SHACL validation is only a declaration check. Consumers must additionally
validate IANA timezone existence, duration bounds, supported recurrence,
manifest revision, host/credential scope, ownership, holds, retries and complete
catalogue coverage. Signed run registration/integrity does not prove the
performing agent's authorship under a shared Unix account. A missed-deadline
checker must observe matching verified run outcomes rather than treating a
firing receipt or a stored command result as success.

Run `uv run --locked --script scripts/check_scheduled_jobs.py` for a valid
example, a disabled declaration, unrelated-data controls and individual refusal
cases. Runtime acceptance still requires natural firings, signed-result
read-back and an observed missed-deadline drill.
