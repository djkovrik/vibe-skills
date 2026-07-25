# Time and scheduling

- Inject clock and current time-zone providers.
- Store instants for global events and local date/time plus zone/recurrence semantics for wall-clock schedules.
- Define inclusive/exclusive boundaries, DST gaps/overlaps, locale week rules, and day-closing behavior.
- Separate a logical recurring schedule from platform alarm instances.
- Recompute next future occurrence after resume, reboot, time-zone change, and app update when required.
- Test multiple zones, DST transitions, month/year boundaries, overdue inputs, and repeated calculation.

Primary reference:

- https://kotlinlang.org/api/kotlinx-datetime/

Blinkly adaptation: logical reminder schedules with physical alarms and resume-time next-occurrence projection are evidence-backed examples, not universal schemas.

