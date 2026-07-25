# Notifications, alarms, and background work

- Separate logical schedules from physical platform alarm IDs.
- Persist enough semantic data to derive the next future occurrence.
- Check exact-alarm policy/access before scheduling on applicable Android versions.
- Rebuild physical registrations after reboot, package replacement, time-zone change, or permission restoration when required.
- Cancel each stable physical identifier; do not assume a library `cancelAll` cancels scheduled alarms.
- Run database-backed broadcast work asynchronously and finish ownership correctly.
- Keep notification content, channels/categories, and deep-link outputs specified and localized.

Primary sources:

- https://developer.android.com/develop/background-work/services/alarms/schedule
- https://developer.android.com/develop/ui/views/notifications
- https://developer.apple.com/documentation/usernotifications

