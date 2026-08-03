---
tags:
   - Occurrence

---
# Work with Occurrences

An <glossary:Occurrence> is created every time an <glossary:Event> is triggered.
It is the audit trail of a single delivery attempt: it stores the context sent
by the caller, which recipients were selected, which messages were rendered
and the final outcome. Occurrences let you verify that notifications actually
happened and debug routing issues without guessing.

## Occurrence list

Every triggered occurrence appears in the list at
<https://SERVER_ADDRESS/admin/bitcaster/occurrence/> with:

- **timestamp** — when the occurrence was created
- **application / event** — the source of the trigger
- **status** — `NEW` (waiting to be processed), `PROCESSED` or `FAILED`
- **attempts** — remaining processing attempts before the occurrence is marked as failed
- **recipients** — number of recipients reached

Use the filters (time range, application, event, status) to narrow the list.

## Occurrence detail

Open an occurrence to inspect what happened. The change page is organised in tabs:

- **General** — timestamp, event and newsletter mode
- **Process** — attempts left and current status
- **Input** — correlation id, the context payload and the routing options sent by the caller
- **Delivery** — number of recipients and the processing data (recipients, channels, errors, rendered content)

## Inspect

The **Inspect** button runs a dry-run of the recipient pipeline: it collects and
renders the recipients without sending anything, so you can verify context and
templates before the real send.

## Recipients

From an occurrence you can navigate to the recipients page to see which
<glossary:Assignment>s were selected and for which channel.

## Purge

Occurrences older than the configured retention are purged automatically. The
**Purge occurrences** action in the admin sidebar removes them immediately.

Occurrences whose event did not reach any recipient trigger the
`OCCURRENCE_SILENCE` system event, so you can monitor silent events.
