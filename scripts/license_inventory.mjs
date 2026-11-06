import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"../frontend");
const lock=JSON.parse(fs.readFileSync(path.join(root,"package-lock.json"),"utf8"));
const notices=["OmniMatch frontend dependency notices", "Generated from the installed production dependency tree. Optional platform packages may differ by installation.", "Each component retains its original license. This inventory is not a legal clearance opinion."];
for(const [location,entry] of Object.entries(lock.packages).sort(([a],[b])=>a.localeCompare(b))){
  if(!location || entry.dev) continue;
  const directory=path.join(root,location);
  if(!fs.existsSync(directory)) continue;
  const pkg=JSON.parse(fs.readFileSync(path.join(directory,"package.json"),"utf8"));
  notices.push(`\n${"=".repeat(72)}\n${pkg.name}@${pkg.version}\nLicense: ${typeof pkg.license==="string"?pkg.license:"See upstream license"}\nSource: ${pkg.homepage||pkg.repository?.url||"See package metadata"}`);
  const files=fs.readdirSync(directory).filter(file=>/^(licen[cs]e|notice)(?:[.-].*)?$/i.test(file) && fs.statSync(path.join(directory,file)).isFile());
  if(!files.length)notices.push("No top-level license file found in this installed package; consult upstream metadata before redistribution.");
  for(const file of files)notices.push(`\n--- ${file} ---\n${fs.readFileSync(path.join(directory,file),"utf8")}`);
}
fs.mkdirSync(path.join(root,"public"),{recursive:true});
fs.writeFileSync(path.join(root,"public/third-party-notices.txt"),notices.join("\n").split(/\r?\n/).map(line=>line.trimEnd()).join("\n").trimEnd()+"\n");
console.log("Generated frontend/public/third-party-notices.txt from installed packages.");
