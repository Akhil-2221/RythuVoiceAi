# Knowledge base (RAG sources)

No documents are bundled. Download REAL publications yourself and place the PDFs here, e.g.:
- ICAR / ICAR institutes (CICR Nagpur for cotton, IIRR Hyderabad for rice, IIOR for oilseeds, IIMR for maize)
- Acharya N.G. Ranga Agricultural University (ANGRAU), Professor Jayashankar Telangana State Agricultural University (PJTSAU)
- KVK advisories, Package of Practices booklets
- Government scheme guidelines (PM-KISAN, PMFBY etc.) from official .gov.in sites

Optional `manifest.json` gives proper citation metadata (only write what is true):
{ "cotton_pop.pdf": {"title": "...", "publisher": "...", "url": "https://..."} }

Then run:  python -m scripts.ingest
Scanned PDFs without a text layer need OCR first (not included).
