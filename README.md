# Chrome Bookmarks Organizer

Sort a messy Chrome bookmark collection into categorized folders, removing exact-URL duplicates along the way.

It has two parts:

1. **`classify.py`** reads a Chrome profile's bookmarks file, applies your rules, and writes `organizer-extension/plan.js` (a map from URL to target folder).
2. **`organizer-extension/`** is a tiny unpacked Chrome extension that applies that plan through the `chrome.bookmarks` API.

The extension makes the changes through Chrome itself. Editing the bookmarks file on disk doesn't work for synced profiles, because sync overwrites it.

## Usage

```sh
cp rules.example.py rules.py          # then edit rules.py to taste (it's gitignored)
python classify.py --profile you@gmail.com --list
```

`--profile` accepts the profile's signed-in email or its folder name (e.g. `"Profile 4"`). The script reads `AccountBookmarks` (synced storage) or `Bookmarks` (local storage) from `%LOCALAPPDATA%\Google\Chrome\User Data\<profile>`. On macOS or Linux, adjust `USER_DATA` in `classify.py`.

Then, in the same Chrome profile:

1. Open `chrome://extensions` and enable **Developer mode**.
2. Click **Load unpacked** and select the `organizer-extension` folder.
3. Click the extension icon, then **Dry run** to preview the counts, then **Apply**.
4. Remove the extension when done.

## What Apply does

- Creates the target folders on the Bookmarks bar. Targets named `Quick Links` are placed loose at the front of the bar.
- Moves every bookmark whose URL is in the plan, and removes later copies of the same URL.
- Deletes folders left empty afterwards.
- Leaves bookmarks that aren't in the plan untouched.

Back up first. Copy the profile's `AccountBookmarks`/`Bookmarks` file, or use Chrome's Bookmark manager › Export.

## Rules

See `rules.example.py`. `RULES` is an ordered list of `(target, predicate)`, and the first match wins. `OVERRIDES` are simple substring matches on path, title or host that are checked first.

## License

MIT
