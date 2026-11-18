const ORDER = [
  "Work", "Dev", "AI", "Home & Life", "Entertainment", "Shopping & Orders",
  "Finance & Crypto", "Education", "Personal & Accounts", "Social", "Archive (old tech)",
];
const QUICK = "Quick Links"; // these go loose at the start of the bar

const logEl = document.getElementById("log");
const log = (s) => { logEl.textContent += s + "\n"; };
const bm = chrome.bookmarks;

function walk(node, fn, parents = []) {
  fn(node, parents);
  for (const c of node.children || []) walk(c, fn, [...parents, node]);
}

async function run(apply) {
  logEl.textContent = "";
  const [root] = await bm.getTree();
  // Use the account (synced) roots when Chrome exposes both local and account ones.
  let roots = root.children;
  if (roots.some((r) => r.syncing === true)) roots = roots.filter((r) => r.syncing === true);
  const bar = roots.find((r) => r.folderType === "bookmarks-bar") || roots.find((r) => r.id === "1") || roots[0];
  log(`Bookmarks bar id=${bar.id}`);

  const leaves = [];
  for (const r of roots) walk(r, (n, ps) => { if (n.url) leaves.push({ n, ps }); });

  const folderCache = new Map();
  async function ensureFolder(path) {
    if (folderCache.has(path)) return folderCache.get(path);
    const parts = path.split("/");
    const parentId = parts.length === 1 ? bar.id : await ensureFolder(parts.slice(0, -1).join("/"));
    const name = parts[parts.length - 1];
    const siblings = String(parentId).startsWith("new:") ? [] : await bm.getChildren(parentId);
    let f = siblings.find((c) => !c.url && c.title === name);
    if (!f) {
      if (!apply) { folderCache.set(path, `new:${path}`); return `new:${path}`; }
      f = await bm.create({ parentId, title: name });
    }
    folderCache.set(path, f.id);
    return f.id;
  }

  // Create top-level folders in the desired order.
  for (const top of ORDER) await ensureFolder(top);

  const placed = new Set();
  let moved = 0, removed = 0, skipped = 0, quickIdx = 0;
  const counts = {};
  for (const { n } of leaves) {
    const target = PLAN[n.url];
    if (!target) { skipped++; continue; }
    if (placed.has(n.url)) {
      removed++;
      if (apply) await bm.remove(n.id);
      continue;
    }
    placed.add(n.url);
    counts[target] = (counts[target] || 0) + 1;
    moved++;
    if (!apply) continue;
    if (target === QUICK) await bm.move(n.id, { parentId: bar.id, index: quickIdx++ });
    else await bm.move(n.id, { parentId: await ensureFolder(target) });
  }

  // Order top-level folders right after the quick links.
  if (apply) {
    let idx = quickIdx;
    for (const top of ORDER) await bm.move(folderCache.get(top), { parentId: bar.id, index: idx++ });
  }

  // Remove folders left empty (old structure), deepest first.
  let emptied = 0;
  if (apply) {
    const keep = new Set([...folderCache.values()]);
    const [fresh] = await bm.getTree();
    const folders = [];
    walk(fresh, (n, ps) => { if (!n.url && ps.length >= 2) folders.push({ n, depth: ps.length }); });
    folders.sort((a, b) => b.depth - a.depth);
    for (const { n } of folders) {
      if (keep.has(n.id)) continue;
      const kids = await bm.getChildren(n.id).catch(() => null);
      if (kids && kids.length === 0) { await bm.remove(n.id); emptied++; }
    }
  }

  log(`${apply ? "Moved" : "Would move"}: ${moved}`);
  log(`${apply ? "Removed" : "Would remove"} duplicates: ${removed}`);
  log(`Not in plan (left untouched): ${skipped}`);
  if (apply) log(`Empty old folders removed: ${emptied}`);
  log("");
  for (const k of Object.keys(counts).sort()) log(`${String(counts[k]).padStart(3)}  ${k}`);
  log(apply ? "\nDone." : "\nDry run only, nothing changed.");
}

document.getElementById("dry").onclick = () => run(false).catch((e) => log("ERROR: " + e.message));
document.getElementById("apply").onclick = () => {
  document.getElementById("apply").disabled = true;
  run(true).catch((e) => log("ERROR: " + e.message));
};
