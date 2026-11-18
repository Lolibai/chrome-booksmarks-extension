"""Example classification rules. Copy to rules.py (gitignored) and tailor it.

RULES: list of (target_folder, predicate). First match wins.
  predicate(p, t, h, u):  p = original folder path, t = title (lowercase),
                          h = host without "www.", u = URL (lowercase)
  target "Quick Links" puts the bookmark loose at the start of the Bookmarks bar.
  Use "/" for subfolders, e.g. "Dev/Angular".
OVERRIDES: list of (field, substring, target), field in {"path","title","host"}; checked before RULES.
FALLBACK: target for anything unmatched.
"""

def any_in(s, words):
    return any(w in s for w in words)

OVERRIDES = [
    # ("host", "example-client.atlassian.net", "Work/Example Client"),
]

RULES = [
    ("Quick Links", lambda p,t,h,u: h in ("mail.google.com", "accounts.google.com", "maps.google.com", "calendar.google.com")),
    ("AI", lambda p,t,h,u: any_in(h, ["chatgpt.com", "chat.openai.com", "claude.ai", "claude.com", "gemini.google.com", "deepseek.com", "huggingface.co", "perplexity.ai"]) or "mcp" in t),
    ("Work/Meetings", lambda p,t,h,u: h in ("meet.google.com", "zoom.us", "teams.microsoft.com")),
    ("Work/Trackers", lambda p,t,h,u: any_in(h, ["atlassian.net", "trello.com", "asana.com", "linear.app", "notion.so"])),
    ("Dev/Cloud", lambda p,t,h,u: any_in(h, ["aws.amazon.com", "azure", "cloud.google.com", "digitalocean.com"])),
    ("Dev/DevOps", lambda p,t,h,u: any_in(h, ["docker.com", "kubernetes.io"]) or any_in(t, ["docker", "kubernetes", "nginx", "jenkins", "ci/cd", "terraform"])),
    ("Dev/Angular", lambda p,t,h,u: any_in(t, ["angular", "rxjs", "ngrx"])),
    ("Dev/React", lambda p,t,h,u: any_in(t, ["react", "redux", "next.js"])),
    ("Dev/.NET", lambda p,t,h,u: any_in(t, ["asp.net", ".net core", "c#"])),
    ("Dev/Reference", lambda p,t,h,u: any_in(h, ["github.com", "stackoverflow.com", "developer.mozilla.org", "npmjs.com", "medium.com", "dev.to"])),
    ("Entertainment/Video", lambda p,t,h,u: any_in(h, ["youtube.com", "netflix.com", "imdb.com", "twitch.tv"])),
    ("Entertainment/Music", lambda p,t,h,u: any_in(h, ["spotify.com", "music.youtube.com", "deezer.com", "soundcloud.com"])),
    ("Entertainment/Games", lambda p,t,h,u: any_in(h, ["steampowered.com", "epicgames.com", "op.gg", "ubi.com"])),
    ("Shopping & Orders", lambda p,t,h,u: any_in(h, ["amazon.", "aliexpress", "ebay.", "17track", "rozetka"])),
    ("Finance & Crypto", lambda p,t,h,u: any_in(h, ["binance", "coinbase", "paypal.com"])),
    ("Social", lambda p,t,h,u: any_in(h, ["facebook.com", "twitter.com", "x.com", "instagram.com", "linkedin.com", "reddit.com", "t.me"])),
]

FALLBACK = "Unsorted"
