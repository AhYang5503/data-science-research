# Fashion Trend Analytics (Volunteer Research Sample)

A simple, teaching-friendly project that shows how **AI and data analysis** can help track fashion trends for a **Fashion Psychology Institute**. It uses plain tools (pandas, simple keyword tagging, basic charts) so the whole pipeline is easy to understand and present.

## What this does (in plain English)
- Loads a small dataset of fashion posts (sample provided).
- Cleans text and **extracts tags/hashtags** like colors, fabrics, and moods (e.g., `#denim`, `#black`, `#romantic`).
- Counts how tags change **week by week** to spot **rising trends**.
- Calculates a simple **engagement score** (likes + 0.1 × views) to see what resonates.
- (Optional) Adds a basic **sentiment score** using VADER to capture tone.
- Saves a **weekly summary CSV**, a **trend chart**, and a short **Markdown report** with takeaways.

> This is intentionally simple (keyword tagging + counts) so it is easy to explain on a resume/portfolio. You can plug in real data later with the same file format.

---

## Project layout
```text
fashion_trend_analytics/
├── data/
│   └── sample_posts.csv
├── output/
│   └── charts/
├── scripts/
│   └── pipeline.py
├── requirements.txt
└── README.md
```

## Data format (CSV)
Minimal columns required by the pipeline:
- `date` (YYYY-MM-DD)
- `platform` (e.g., instagram, tiktok, pinterest)
- `post_id` (unique id per post)
- `text` (caption or description; hashtags allowed)
- `likes` (integer)
- `views` (integer)

Example row:
```csv
2025-07-01,instagram,ig_001,"Loving the #red #denim jacket — cozy vibe for rainy days. #minimal",320,5500
```

## Install
```bash
# 1) (Recommended) use a virtual environment
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) install packages
pip install -r requirements.txt
```

## Run the pipeline
```bash
# From the project root
python scripts/pipeline.py --input_csv data/sample_posts.csv --output_dir output
```

### Outputs
- `output/weekly_tag_summary.csv` — pivot-like summary of tag counts per week (plus avg engagement & sentiment)
- `output/charts/top_trends.png` — line chart for the top rising tags
- `output/report_summary.md` — 1-pager with highlights you can paste into slides/Docs

---

## How the "AI" part works (kept simple)
- **Keyword/hashtag tagging:** A small vocabulary (colors, fabrics, moods) is matched in captions/hashtags to create tags.
- **Trend detection:** We count tags **by week** and look for increases in the last 2 weeks versus the prior 2.
- **Engagement linkage:** We average an engagement score per tag to see which tags get more reactions.
- **Optional sentiment:** VADER sentiment gives a rough "tone" score per post.

You can later swap in fancier pieces (e.g., topic modeling or image tagging) without changing the overall flow.

## Customize the tag vocabulary
Open `scripts/pipeline.py` and edit these lists near the top:
```python
COLOR_WORDS = ["red","blue","black","white","green","beige","pastel"]
STYLE_WORDS = ["denim","linen","leather","knit","floral"]
MOOD_WORDS  = ["minimal","romantic","edgy","cozy","casual","bold","confident","lightweight","mood"]
```
Add or remove words to fit your study.

## Using your real data
- Export your posts to CSV with the **same columns** as the sample.
- Place the file under `data/` and change the `--input_csv` path.
- If you have **private/identifiable** fields, remove names/IDs before analysis.

## Ethics & privacy (what to say on your resume/report)
- We removed personal names/IDs and only analyze **text + public engagement counts**.
- We comply with platform TOS; data is for research/education.
- We check for **bias**: tag vocabularies can skew results (e.g., color names more common in English).
- We document **limits**: counts reflect what people post (not full sales or offline behavior).

## Talking points for interviews
- Problem: teams need fast, reliable signals on color/style/mood trends.
- Approach: simple keyword tagging + weekly counts + engagement linkage.
- Impact: turns messy posts into **clear, weekly trend lines** and a 1‑page brief.
- Next steps: expand tag lists; add image tagging (e.g., CLIP) and time-series forecasting if needed.

## Troubleshooting
- If you see `LookupError` about VADER lexicon, the script will auto‑download it when NLTK is installed.
- If plots are empty, your last 2 weeks may have few tags; expand the date range or add more tags.
- For non-English captions, add translated keywords, or skip sentiment.

---

## License
MIT for the sample code. Use your own data responsibly.