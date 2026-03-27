from pathlib import Path

path = Path(r"c:\Users\eloo\SITE\src\components\LastFmStatus.svelte")
text = path.read_text(encoding="utf-8")

old_label_block = "    <span class=\"truncate\">\n      <span class=\"sr-only\">{statusLabel}: </span>\n      {#if status}\n        <span aria-hidden=\"true\">{statusLabel}: {status.artist} - {status.title}</span>\n      {:else}\n        <span aria-hidden=\"true\">Last.fm</span>\n      {/if}\n    </span>\n  </a>\n"

if old_label_block not in text:
    raise SystemExit("Old label block not found")

text = text.replace(old_label_block, "    <span class=\"truncate\" aria-hidden=\"true\">{displayText}</span>\n  </a>\n")

old_status_label = "  $: statusLabel = status\n    ? status.nowPlaying\n      ? \"Nu aan het luisteren\"\n      : \"Recent gespeeld\"\n    : \"Last.fm\";\n"

if old_status_label not in text:
    raise SystemExit("Old status label not found")

text = text.replace(old_status_label, "  $: displayText = status ? `${status.artist} — ${status.title}` : \"Last.fm\";\n  $: statusTitle = status\n    ? status.nowPlaying\n      ? `Luistert nu: ${status.artist} — ${status.title}`\n      : `Recent gespeeld: ${status.artist} — ${status.title}`\n    : \"Last.fm\";\n")

old_anchor = "  <a\n    class=\"ms-4 hidden max-w-xs items-center gap-2 rounded-full px-3 py-1 text-sm text-accent transition-colors hover:bg-accent/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-transparent sm:flex\"\n    href={status?.url ?? profileUrl}\n    rel=\"noopener noreferrer\"\n    target=\"_blank\"\n  >\n"

if old_anchor not in text:
    raise SystemExit("Old anchor not found")

text = text.replace(old_anchor, "  <a\n    class=\"ms-4 hidden items-center gap-2 rounded-md border border-transparent px-2.5 py-1 text-sm text-accent transition hover:border-accent/40 hover:bg-accent/10 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:ring-offset-2 focus-visible:ring-offset-transparent sm:inline-flex\"\n    href={status?.url ?? profileUrl}\n    rel=\"noopener noreferrer\"\n    target=\"_blank\"\n    title={statusTitle}\n  >\n")

path.write_text(text, encoding="utf-8")
