# Scheduled-job profile

This explicit operational profile represents a recurring occurrence as a
Schema.org Event with `eventSchedule` pointing to a Schedule and
`potentialAction` pointing to the declared job Action. An explicit `q:ScheduledJob`
marker distinguishes these Actions from other applications using the same public
class; it adds no executable command property. All public terms are checked
against the pinned Schema.org term list. See [Schedule](https://schema.org/Schedule) and
[eventSchedule](https://schema.org/eventSchedule).

The optional marker must accompany `schema:Action`; marked subjects receive the
full Action constraints even without an Event link. It grants no execution
authority. Other profiles may exempt exactly this marker from tracker-only
constraints while retaining their targets and malformed-item controls.

The Action carries a name, immutable manifest revision, declared provenance,
owner, explicit enablement, host IRI and command-manifest target IRI. A target
IRI is a reference for an independently admitted local manifest, never shell
text to execute from the graph. Host identity must also be resolved by the
consumer. Disabled declarations remain fully described and queryable.

The reader contract supports positive fixed day/hour/minute/second intervals,
or a weekly local-time form: `repeatFrequency P7D`, exactly one Schema.org
weekday in `byDay`, and one `startTime` as `HH:MM:00` (`xsd:time`, no offset).
Both require an IANA timezone and offset-aware activation anchor. See the
disabled [weekly example](weekly-example.ttl). Consumers verify anchor alignment
with its weekday and local time in that zone, then convert each occurrence to
UTC separately. Monday 09:17 New York is 13:17 UTC on October 26, 2026, then
14:17 UTC after the November 1 fallback. Gaps and overlaps refuse as UNKNOWN;
consumers retain pending state instead of shifting a time or choosing a fold.
SHACL alone cannot verify IANA rules or execution eligibility.

Partial/multiple weekdays, sub-minute times, exceptions, repeat counts and other
calendar bounds remain refused. They are never silently approximated as fixed
intervals. Complex cron jobs stay in their original
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

For a before/after source demonstration, run
`uv run --locked --script scripts/demo_weekly_profile.py`. It checks the same
weekly declaration against base `2374dd5` and the candidate, retains a positive
fixed-interval control and refuses partial qualifiers. The exact candidate
head is recorded in the PR. Download the [recording](demo.log) and
[timing](demo.timing), then use
`scriptreplay --log-out demo.log --log-timing demo.timing`.
Terminal playback was checked; no inline video or installed profile is claimed.
