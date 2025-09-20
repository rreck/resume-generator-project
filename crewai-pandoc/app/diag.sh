#!/usr/bin/env bash
# Copyright (c) RRECKTEK LLC | Version: 1.0.0 | Built: @EPOCH
set -euo pipefail
cd "$(dirname "$0")"

TEX="${1:-template.tex}"
echo "== Diag: template = $TEX"
if [[ ! -f "$TEX" ]]; then echo "ERR: $TEX not found" >&2; exit 2; fi

awk '
/\\documentclass/{
  if (match($0, /\\documentclass(\[[^]]*\])?\{([^}]+)\}/, m)) print "class:" m[2]
}
/\\(usepackage|RequirePackage)/{
  while (match($0, /\\(usepackage|RequirePackage)(\[[^]]*\])?\{([^}]+)\}/, m)) {
    n=m[3]; gsub(/,/, " ", n); print "pkg:" n; $0=substr($0, RSTART+RLENGTH)
  }
}
/\\set(main|sans|mono)font\{[^}]+\}/{
  while (match($0, /\\set(main|sans|mono)font\{([^}]+)\}/, m)) { print "font:" m[2]; $0=substr($0, RSTART+RLENGTH) }
}
/\\bibliographystyle\{[^}]+\}/{
  if (match($0, /\\bibliographystyle\{([^}]+)\}/, m)) print "bibtex-style:" m[1]
}
' "$TEX" | sort -u > .diag.tmp

echo "== Extracted from template:"
cat .diag.tmp

have(){ command -v "$1" >/dev/null 2>&1 && echo yes || echo no; }
echo "== Binaries:"
for b in pandoc xelatex lualatex pdflatex biber bibtex makeindex xindy inkscape gs pygmentize tectonic; do
  echo "bin:$b=$(have $b)"
done

echo "== Font presence (fontconfig):"
if command -v fc-list >/dev/null 2>&1; then
  awk '/^font:/{print $2}' .diag.tmp | while read -r f; do
    if fc-list : family | grep -i -q -F "$f"; then echo "font:$f=ok"; else echo "font:$f=missing"; fi
  done
else
  echo "fc-list: not available"
fi

echo "== TeX packages present (kpsewhich):"
if command -v kpsewhich >/dev/null 2>&1; then
  awk '/^pkg:/{print $2}' .diag.tmp | tr ' ' '\n' | sort -u | while read -r p; do
    [[ -z "$p" ]] && continue
    if kpsewhich "$p.sty" >/dev/null 2>&1; then echo "texpkg:$p=ok"; else echo "texpkg:$p=missing"; fi
  done
  cls=$(awk -F: '/^class:/{print $2}' .diag.tmp)
  if [[ -n "$cls" ]]; then
    if kpsewhich "$cls.cls" >/dev/null 2>&1; then echo "texclass:$cls=ok"; else echo "texclass:$cls=missing"; fi
  fi
else
  echo "kpsewhich: not available"
fi

echo "== Pandoc filters:"
for f in pandoc-crossref pandoc-citeproc; do
  echo -n "filter:$f="
  if command -v "$f" >/dev/null 2>&1; then echo yes; else echo no; fi
done

echo "== Suggested engine:"
if grep -qi '^pkg:.*fontspec' .diag.tmp; then echo "engine: xelatex|lualatex"; else echo "engine: pdflatex ok"; fi

rm -f .diag.tmp
