import os
import re
import argparse
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

# Optional: lightweight sentiment with VADER
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    HAVE_VADER = True
except Exception:
    HAVE_VADER = False

COLOR_WORDS = [
    "red","blue","black","white","green","beige","pastel"
]

STYLE_WORDS = [
    "denim","linen","leather","knit","floral"
]

MOOD_WORDS = [
    "minimal","romantic","edgy","cozy","casual","bold","confident","lightweight","mood"
]

TAG_WORDS = set(COLOR_WORDS + STYLE_WORDS + MOOD_WORDS)

URL_RE = re.compile(r"http\S+|www\.\S+")
HASHTAG_RE = re.compile(r"#(\w+)")

def clean_text(s: str) -> str:
    s = s or ""
    s = URL_RE.sub("", s)
    return s.strip()

def extract_hashtags(s: str):
    return [h.lower() for h in HASHTAG_RE.findall(s or "")]

def keyword_tags(tokens):
    return sorted({t for t in tokens if t in TAG_WORDS})

def safe_week(d):
    if isinstance(d, str):
        d = datetime.fromisoformat(d)
    return d.strftime("%G-W%V")  # ISO week label like 2025-W27

def add_sentiment(df):
    if not HAVE_VADER:
        df["sentiment"] = None
        return df
    nltk.download("vader_lexicon", quiet=True)
    sia = SentimentIntensityAnalyzer()
    df["sentiment"] = df["text"].fillna("").apply(lambda t: sia.polarity_scores(t)["compound"])
    return df

def main(args):
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(os.path.join(args.output_dir,"charts"), exist_ok=True)

    df = pd.read_csv(args.input_csv)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"])

    # Basic cleaning
    df["text_clean"] = df["text"].astype(str).apply(clean_text).str.lower()

    # Hashtags + keyword tags
    df["hashtags"] = df["text_clean"].apply(extract_hashtags)
    df["tokens"] = df["text_clean"].str.findall(r"[a-z]+")
    df["kw_tags"] = df["tokens"].apply(keyword_tags)

    # Combine hashtag tags + keyword tags, then keep ones in our vocab
    df["all_tags"] = (df["hashtags"] + df["kw_tags"]).apply(lambda tags: sorted({t for t in tags if t in TAG_WORDS}))

    # Engagement proxy
    df["engagement"] = df["likes"].fillna(0) + 0.1 * df["views"].fillna(0)

    # Optional sentiment
    df = add_sentiment(df)

    # Weekly label
    df["week"] = df["date"].apply(safe_week)

    # Explode tags for counting
    exploded = df.explode("all_tags").dropna(subset=["all_tags"])

    # Weekly counts per tag
    weekly = (exploded
              .groupby(["week","all_tags"], as_index=False)
              .agg(posts=("post_id","count"),
                   avg_engagement=("engagement","mean"),
                   avg_sentiment=("sentiment","mean")))

    weekly.to_csv(os.path.join(args.output_dir,"weekly_tag_summary.csv"), index=False)

    # Identify top 5 rising tags (last 2 weeks vs prior 2 weeks)
    # If <4 weeks, fall back to top by recent posts
    try:
        weeks_sorted = sorted(weekly["week"].unique())
        recent = weeks_sorted[-2:]
        prior = weeks_sorted[-4:-2]
        recent_sum = weekly[weekly["week"].isin(recent)].groupby("all_tags")["posts"].sum()
        prior_sum = weekly[weekly["week"].isin(prior)].groupby("all_tags")["posts"].sum()
        delta = (recent_sum - prior_sum).fillna(recent_sum).sort_values(ascending=False)
        rising = list(delta.head(5).index)
    except Exception:
        rising = (weekly.groupby("all_tags")["posts"].sum().sort_values(ascending=False).head(5).index.tolist())

    # Plot trends for rising tags
    pivot = weekly.pivot(index="week", columns="all_tags", values="posts").fillna(0)
    if rising:
        plt.figure()
        pivot[rising].plot(ax=plt.gca(), marker="o")
        plt.title("Rising Fashion Tags (posts per week)")
        plt.xlabel("ISO Week")
        plt.ylabel("Posts")
        plt.tight_layout()
        chart_path = os.path.join(args.output_dir,"charts","top_trends.png")
        plt.savefig(chart_path, dpi=150)
        plt.close()
    else:
        chart_path = None

    # Simple report
    with open(os.path.join(args.output_dir,"report_summary.md"), "w") as f:
        f.write("# Weekly Fashion Trend Summary\n\n")
        f.write(f"**Input file:** `{os.path.basename(args.input_csv)}`\n\n")
        if rising:
            f.write("**Top rising tags (last 2 weeks):** " + ", ".join(rising) + "\n\n")
        top_engage = (weekly.groupby("all_tags")["avg_engagement"].mean()
                      .sort_values(ascending=False).head(5))
        f.write("**Tags with highest average engagement:**\n\n")
        for tag, val in top_engage.items():
            f.write(f"- {tag}: {val:.1f}\n")
        f.write("\n")
        if chart_path:
            f.write(f"![Top Trends](charts/{os.path.basename(chart_path)})\n\n")
        f.write("**Notes:** Counts come from simple tag/keyword matching. Sentiment uses optional VADER.\n")

    print("Pipeline finished.")
    print(f"- Weekly summary: {os.path.join(args.output_dir,'weekly_tag_summary.csv')}")
    if chart_path:
        print(f"- Chart: {chart_path}")
    print(f"- Report: {os.path.join(args.output_dir,'report_summary.md')}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple AI-aided fashion trend analytics pipeline")
    parser.add_argument("--input_csv", type=str, default="data/sample_posts.csv", help="Path to posts CSV")
    parser.add_argument("--output_dir", type=str, default="output", help="Directory for outputs")
    args = parser.parse_args()
    main(args)