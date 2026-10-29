# Outage Status Feed

Publishes planned and unplanned outage notices for the Larkspur Utilities public website and for partners that subscribe to the RSS feed.

## Requirements

Node.js 18 or newer. No third-party packages.

## Run

```bash
npm start            # listens on port 8090
```

```bash
curl http://localhost:8090/notices
curl "http://localhost:8090/notices?region=east&upcoming=true"
curl http://localhost:8090/notices/OUT-1043
curl http://localhost:8090/feed.rss
```

## Tests

```bash
npm test
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `OUTAGE_FEED_PORT` | `8090` | HTTP port |
| `FEED_BASE_URL` | `http://localhost:8090` | Public base URL used in feed links |
| `NOTICES_FILE` | `data/notices.json` | Notice data file |
| `FEED_CACHE_SECONDS` | `300` | How long clients and the CDN may cache the RSS feed |

## Notes

* Notices are loaded once at startup; restart the service to publish changes.
* Notices without an end time stay active until an operator closes them.
