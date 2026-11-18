"""Classify Chrome bookmarks into folders and emit a plan for the organizer extension.

Usage:
    python classify.py --profile you@gmail.com        # pick profile by signed-in email
    python classify.py --profile "Profile 4"          # or by profile folder name
    python classify.py --profile ... --list           # print the full grouped plan

Rules come from rules.py (your private copy) or, if absent, rules.example.py.
Output: organizer-extension/plan.js  (maps URL -> target folder path)
"""
import argparse, importlib.util, json, os, sys
from collections import Counter
from itertools import groupby
from urllib.parse import urlparse

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
USER_DATA = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data")


def resolve_profile(arg):
    if os.path.isdir(os.path.join(USER_DATA, arg)):
        return arg
    state = json.load(open(os.path.join(USER_DATA, "Local State"), encoding="utf-8"))
    for folder, info in state["profile"]["info_cache"].items():
        if info.get("user_name", "").lower() == arg.lower():
            return folder
    sys.exit(f"No Chrome profile matches {arg!r}")


def load_bookmarks(profile):
    base = os.path.join(USER_DATA, profile)
    # Account-stored (synced) bookmarks live in AccountBookmarks; local ones in Bookmarks.
    for name in ("AccountBookmarks", "Bookmarks"):
        path = os.path.join(base, name)
        if os.path.exists(path):
            return json.load(open(path, encoding="utf-8"))
    sys.exit(f"No bookmarks file in {base}")


def flatten(data):
    items = []
    def walk(n, path):
        if n.get("type") == "folder":
            for c in n.get("children", []):
                walk(c, path + [n["name"]])
        else:
            items.append({"path": "/".join(path), "title": n.get("name", ""), "url": n.get("url", "")})
    for r in ("bookmark_bar", "other", "synced"):
        if r in data["roots"]:
            walk(data["roots"][r], [])
    return items


def host(u):
    h = urlparse(u).hostname or ""
    return h[4:] if h.startswith("www.") else h


def make_classifier(rules):
    overrides = getattr(rules, "OVERRIDES", [])
    def classify(it):
        fields = {"path": it["path"], "title": it["title"].lower(), "host": host(it["url"])}
        for field, sub, target in overrides:
            if sub in fields[field]:
                return target
        p, t, h, u = it["path"], fields["title"], fields["host"], it["url"].lower()
        for target, pred in rules.RULES:
            try:
                if pred(p, t, h, u):
                    return target
            except Exception:
                pass
        return getattr(rules, "FALLBACK", "Unsorted")
    return classify


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True, help="signed-in email or profile folder name")
    ap.add_argument("--list", action="store_true", help="print every bookmark grouped by target")
    args = ap.parse_args()

    rules_mod = "rules" if os.path.exists(os.path.join(HERE, "rules.py")) else "rules.example"
    spec = importlib.util.spec_from_file_location("rules", os.path.join(HERE, rules_mod + ".py"))
    rules = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rules)
    classify = make_classifier(rules)

    profile = resolve_profile(args.profile)
    items = flatten(load_bookmarks(profile))

    plan, dups = {}, 0
    for it in items:
        if it["url"] in plan:
            dups += 1
            continue
        plan[it["url"]] = classify(it)

    out = os.path.join(HERE, "organizer-extension", "plan.js")
    with open(out, "w", encoding="utf-8") as f:
        f.write("const PLAN = " + json.dumps(plan, ensure_ascii=False, indent=0) + ";\n")

    print(f"profile: {profile}   rules: {rules_mod}.py   bookmarks: {len(items)}   unique: {len(plan)}   duplicates: {dups}")
    for k, v in sorted(Counter(plan.values()).items()):
        print(f"{v:4} {k}")
    if args.list:
        by_url = {it["url"]: it for it in reversed(items)}
        for target, urls in groupby(sorted(plan, key=plan.get), key=plan.get):
            print(f"\n## {target}")
            for u in urls:
                print(f"  {by_url[u]['title'][:55]} | {host(u)}")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
