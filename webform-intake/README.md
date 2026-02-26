# Jodi Website (Local Test)

This project now runs as a full local website:

- Landing page: `http://localhost:4173/`
- Intake flow: `http://localhost:4173/intake`
- Local API endpoint: `POST /api/intake` (stores submissions in `data/submissions.ndjson`)

## Run locally

```bash
cd /Users/nikunjvora/clawd/ventures/jodi-webform-intake
npm start
```

Then open:

- [http://localhost:4173/](http://localhost:4173/)
- [http://localhost:4173/intake](http://localhost:4173/intake)

## Project structure

- `server.js` - local HTTP server + API stub
- `public/index.html` - marketing/landing page
- `public/site.css` - landing page styles
- `public/intake/index.html` - intake app shell
- `public/intake/app.js` - intake logic and conditional flow
- `public/intake/styles.css` - intake design
- `public/intake/schema.json` - 77-field schema extracted from XLSX

## Notes

- Intake answers are still logged in browser devtools (`console.log`).
- Submissions are also posted to the local API and appended to `data/submissions.ndjson` for local testing.
