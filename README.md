# TrustLens AI
Open-source browser extension for real-time credibility scoring. Uses scraping + Google Fact-Check API.

## Features
- S1: Domain provenance
- S2: Author credibility
- S3: Content consistency
- S4: Image authenticity
- S5: Fact-check via Google API

## Setup
1. Clone: `git clone https://github.com/yourusername/trustlens-ai`
2. API: `cd apps/api && pip install -r requirements.txt && uvicorn main:app --port 8001`
3. Extension: `cd apps/extension && npm install && npm run build`
4. Load in Chrome: chrome://extensions → Load unpacked → dist folder

## Contribute
- Fork and PR improvements (e.g., add PolitiFact API).
- Issues: Report bugs or suggest features.

## License
MIT
