/*
 * Smoke test for the built app. Loads Redstone_Block_Index.html in a headless
 * DOM and exercises the data + core interactions.
 *
 * Requires jsdom:  npm install jsdom
 * Run:            node scripts/validate.js
 */
const path = require("path");
const fs = require("fs");
const { JSDOM } = require("jsdom");

const HTML_PATH = path.join(__dirname, "..", "Redstone_Block_Index.html");
const html = fs.readFileSync(HTML_PATH, "utf-8");
const dom = new JSDOM(html, { runScripts: "dangerously" });
const { window: win } = dom;
const doc = win.document;

let failures = 0;
function check(name, cond) {
  console.log((cond ? "PASS" : "FAIL") + " - " + name);
  if (!cond) failures++;
}

const total = Number(doc.getElementById("totalCount").textContent);
check("data loaded (>100 blocks)", total > 100);

const rows = doc.querySelectorAll("#tbody tr:not(.detail-row)");
check("one table row per block", rows.length === total);

const rowTexts = Array.from(rows).map((r) => r.textContent);
check(
  "no leftover 'Slime Block, Honey Block' stub row",
  !rowTexts.some((t) => t.includes("Slime Block, Honey Block"))
);

const honeyRow = rows[rowTexts.findIndex((t) => t.includes("Honey Block"))];
check("honey block present", !!honeyRow);
check("honey height cell = 15px", /15px/.test(honeyRow.textContent));
check("honey width cell = 14px", /14px/.test(honeyRow.textContent));

const headers = Array.from(doc.querySelectorAll("#headRow th")).map((th) => th.textContent.trim());
check("header has 13 columns", headers.length === 13);
check("has merged 'Piston' column", headers.includes("Piston"));
check("no separate 'Movable' column", !headers.includes("Movable"));

// piston categorical filter (Immovable)
const pistonTri = doc.querySelector('.tri.choice[data-key="piston"]');
check("piston choice filter rendered", !!pistonTri);
if (pistonTri) {
  pistonTri.querySelector('[data-v="Immovable"]').dispatchEvent(new win.Event("click", { bubbles: true }));
  const afterPiston = Number(doc.getElementById("shownCount").textContent);
  check("piston=Immovable filter narrows results", afterPiston > 0 && afterPiston < total);
  doc.getElementById("resetBtn").dispatchEvent(new win.Event("click", { bubbles: true }));
}

// search
const search = doc.getElementById("search");
search.value = "honey";
search.dispatchEvent(new win.Event("input", { bubbles: true }));
check("search narrows results", Number(doc.getElementById("shownCount").textContent) < total);
doc.getElementById("resetBtn").dispatchEvent(new win.Event("click", { bubbles: true }));

// width filter
const wMin = doc.getElementById("wMin");
wMin.value = "15";
wMin.dispatchEvent(new win.Event("input", { bubbles: true }));
const afterW = Number(doc.getElementById("shownCount").textContent);
check("width filter narrows results", afterW > 0 && afterW < total);
doc.getElementById("resetBtn").dispatchEvent(new win.Event("click", { bubbles: true }));

// detail expand
rows[0].dispatchEvent(new win.Event("click", { bubbles: true }));
const detail = doc.querySelector("#tbody tr.detail-row");
check("row expands to detail view", !!detail);
check("detail shows Width / Length", detail && detail.innerHTML.includes("Width / Length"));

console.log(failures === 0 ? "\nALL PASS" : `\n${failures} FAILED`);
process.exit(failures === 0 ? 0 : 1);
