#!/usr/bin/env python3
"""Validate the agents-kit marketplace: manifests, agents, commands and README."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PREFIXES = {"sdlc": ("dev-", "product-", "meta-"), "marketing": ("marketing-",), "sales": ("sales-",)}
AGENT_KEYS = {"name", "description", "model", "disallowedTools", "tools", "color"}
# Claude Code removes these tools from every subagent, so agent bodies must not rely on them.
SUBAGENT_REMOVED_TOOLS = re.compile(r"\b(AskUserQuestion|EnterPlanMode|ExitPlanMode|ScheduleWakeup|Workflow|EndConversation|WaitForMcpServers)\b")
COMMAND_KEYS = {"description", "argument-hint"}
LEGACY = re.compile(r"docker|install\.sh|install\.ps1|\.zip\b|DEPLOY_BASE_URL|agents-en|with-marketing|with-sales|blinkbrosai|nginx", re.I)

errors = []


def err(msg):
    errors.append(msg)


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not m:
        err(f"{path.relative_to(ROOT)}: missing frontmatter")
        return {}, text
    fields = {}
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep and not line.startswith((" ", "\t")):
            fields[k.strip()] = v.strip().strip('"')
    return fields, text[m.end():]


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        err(f"{path.relative_to(ROOT)}: {e}")
        return {}


market = load_json(ROOT / ".claude-plugin/marketplace.json")
entries = market.get("plugins", [])
if sorted(e.get("name") for e in entries) != sorted(PREFIXES):
    err(f"marketplace plugins {[e.get('name') for e in entries]} != {sorted(PREFIXES)}")

agents = {}    # plugin -> set of agent names
commands = {}  # plugin -> set of command names
for entry in entries:
    plugin = entry.get("name")
    src = entry.get("source", "")
    pdir = ROOT / src
    if not src.startswith("./") or ".." in src or not pdir.is_dir():
        err(f"{plugin}: bad source {src!r}")
        continue
    manifest = load_json(pdir / ".claude-plugin/plugin.json")
    if manifest.get("name") != plugin:
        err(f"{plugin}: plugin.json name {manifest.get('name')!r} != marketplace entry")
    if not re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")):
        err(f"{plugin}: plugin.json version missing or not semver")

    agents[plugin] = set()
    for f in sorted((pdir / "agents").glob("*.md")):
        fm, body = frontmatter(f)
        name = fm.get("name", "")
        rel = f.relative_to(ROOT)
        removed = sorted(set(SUBAGENT_REMOVED_TOOLS.findall(body)))
        if removed:
            err(f"{rel}: relies on tools unavailable to subagents {removed}")
        if f.name != f"{name}.agent.md":
            err(f"{rel}: file name does not match name {name!r}")
        if not name.startswith(PREFIXES.get(plugin, ())):
            err(f"{rel}: {name!r} does not belong in plugin {plugin}")
        if not fm.get("description"):
            err(f"{rel}: empty description")
        if set(fm) - AGENT_KEYS:
            err(f"{rel}: unsupported frontmatter keys {sorted(set(fm) - AGENT_KEYS)}")
        if any(name in s for s in agents.values()):
            err(f"{rel}: duplicate agent name {name!r}")
        agents[plugin].add(name)

    commands[plugin] = set()
    for f in sorted((pdir / "commands").glob("*.md")):
        fm, _ = frontmatter(f)
        if not fm.get("description"):
            err(f"{f.relative_to(ROOT)}: empty description")
        if set(fm) - COMMAND_KEYS:
            err(f"{f.relative_to(ROOT)}: unsupported frontmatter keys {sorted(set(fm) - COMMAND_KEYS)}")
        commands[plugin].add(f.stem)

# Namespaced references (`plugin:agent`, `/plugin:command`) must resolve.
for f in sorted(ROOT.glob("plugins/*/commands/*.md")) + [ROOT / "README.md", ROOT / "USE-CASE.md"]:
    text = f.read_text(encoding="utf-8") if f.exists() else ""
    for slash, plugin, name in re.findall(r"(/?)\b(sdlc|marketing|sales):([a-z][a-z-]*)", text):
        pool = commands if slash else agents
        if name not in pool.get(plugin, set()):
            err(f"{f.relative_to(ROOT)}: unknown reference {slash}{plugin}:{name}")

for doc in ("README.md", "USE-CASE.md"):
    path = ROOT / doc
    if not path.is_file():
        err(f"{doc}: missing")
        continue
    hits = sorted({m.group(0) for m in LEGACY.finditer(path.read_text(encoding="utf-8"))})
    if hits:
        err(f"{doc}: legacy distribution terms {hits}")

readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").is_file() else ""
for plugin in PREFIXES:
    if f"/plugin install {plugin}@{market.get('name')}" not in readme:
        err(f"README.md: missing install command for {plugin}")
for name in sorted(set().union(*agents.values())):
    if not re.search(rf"\b{re.escape(name)}\b", readme):
        err(f"README.md: agent {name} not listed")

total = sum(len(s) for s in agents.values())
if errors:
    print("\n".join(f"FAIL: {e}" for e in errors))
    sys.exit(1)
print(f"PASS: {len(agents)} plugins, {total} agents, {sum(len(s) for s in commands.values())} commands")
