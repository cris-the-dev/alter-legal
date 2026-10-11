#!/usr/bin/env python3
"""Builds frames/v1/catalog.json: 50 frame designs per kind for the Alter app.

Designs are original, only *inspired by* places and eras: no real stamp artwork, no postal
authority names, no trademarks. Deterministic: same input, same file. Run: python3 generate.py
"""
import json, os

PER_KIND, FREE = 50, 3

SERIF = ["Didot", "Georgia-Bold", "Baskerville-Bold", "Copperplate-Bold", "Optima-Bold", "Palatino-Bold"]
SANS = ["Futura-Bold", "GillSans-Bold", "AvenirNext-Heavy", "HelveticaNeue-CondensedBlack", "AmericanTypewriter-Bold"]
HAND = ["Noteworthy-Bold", "MarkerFelt-Wide", "ChalkboardSE-Bold", "BradleyHandITCTT-Bold", "SnellRoundhand-Bold"]

# Stamps: (name, bottom word, value, paper, ink, accent)
STAMPS = [
    ("Boston", "POSTAGE", "5¢", "#F3EFE4", "#2F4858", "#C8202F"),
    ("Paris", "POSTES", "1 F", "#F4EBDD", "#1F3C88", "#C8202F"),
    ("Lisboa", "CORREIO", "2$50", "#F6EEDC", "#0E5E6F", "#E0A526"),
    ("Madrid", "CORREOS", "25 c", "#FAF0E0", "#8E1B1B", "#E3B23C"),
    ("Kyoto", "郵便", "84円", "#F7F1E3", "#B33A3A", "#2E4A62"),
    ("Hà Nội", "BƯU CHÍNH", "200đ", "#FFF6E5", "#B71C1C", "#F2C230"),
    ("Seoul", "우표", "₩300", "#F3F0E8", "#24476B", "#D1495B"),
    ("Bangkok", "ไปรษณีย์", "5 ฿", "#FBF2DF", "#6B2D5C", "#E2A400"),
    ("Shanghai", "邮政", "8分", "#F8EFE0", "#9B2226", "#386641"),
    ("Roma", "POSTA", "€1", "#F5EEDF", "#5B3A29", "#B5651D"),
    ("Berlin", "PORTO", "20 PF", "#EFEDE6", "#2B2B2B", "#C1121F"),
    ("London", "POSTAGE", "2½d", "#F6F1E7", "#4B2E83", "#B8860B"),
    ("Stockholm", "PORTO", "5 KR", "#EEF2F3", "#1D4E89", "#F2C14E"),
    ("Havana", "CORREOS", "10 c", "#FCEFD9", "#0B6E4F", "#E76F51"),
    ("Cairo", "POSTAGE", "5 m", "#F3E5C8", "#7F4F24", "#3A86FF"),
    ("Marrakech", "POSTES", "1 DH", "#F8E3CC", "#9C2C13", "#1B998B"),
    ("Mexico", "CORREOS", "$2", "#FFF1DD", "#B5179E", "#06A77D"),
    ("Rio", "CORREIO", "50 c", "#F1F7E8", "#2D6A4F", "#F4A259"),
    ("Istanbul", "POSTA", "5 K", "#F4ECE1", "#003F88", "#D00000"),
    ("Delhi", "POSTAGE", "₹5", "#FFF4E0", "#E85D04", "#3D5A80"),
    ("Sydney", "POSTAGE", "45c", "#EEF4F7", "#00509D", "#FDC500"),
    ("New York", "AIR MAIL", "8¢", "#F5F3EE", "#1D3557", "#E63946"),
    ("Reykjavík", "PÓSTUR", "10 KR", "#EAF1F5", "#264653", "#2A9D8F"),
    ("Athens", "POSTAGE", "5 Δ", "#F1F4F8", "#0D47A1", "#FFB703"),
    ("Amsterdam", "POST", "25 c", "#FFF3E6", "#E36414", "#0F4C5C"),
]
STAMP_STYLES = [  # (suffix, border, mark, font pool)
    ("", "single", "round", SERIF), (" Air", "airmail", "wave", SANS),
]
STAMP_EXTRA_BORDERS = ["double", "ornate", "dashed", "none"]
STAMP_MARKS = ["round", "box", "wave", "round"]

POLAROID = [  # (name, paper, ink, accent=date colour, text)
    ("Snow", "#FFFFFF", "#1F2937", "#FF5E3A", None), ("Cream", "#F6F0E1", "#4A3B2A", "#FF8C2B", None),
    ("Midnight", "#1C1C1E", "#F2F2F2", "#FFB347", None), ("Blush", "#F9DCDC", "#8C3B4A", "#FF6F61", "♡"),
    ("Mint", "#D8F0E3", "#25594A", "#FF8C2B", None), ("Sky", "#DCEBFA", "#23466E", "#FF8C2B", "☁︎"),
    ("Lavender", "#E6DDF5", "#4C3A72", "#FF7AA2", "✿"), ("Kraft", "#C9A97C", "#3B2A1A", "#FFF2D0", None),
    ("Lemon", "#FFF3B0", "#5C4A00", "#FF7B00", "☀︎"), ("Peach", "#FFDCC2", "#7A3E1D", "#E85D04", None),
    ("Sage", "#C9D5B9", "#3A4A2E", "#FF8C2B", "☘︎"), ("Coral", "#FF8A80", "#FFFFFF", "#FFF59D", None),
    ("Navy", "#1F2A44", "#E8EEF8", "#FFC857", "★"), ("Forest", "#24453A", "#F1F5EC", "#FFB703", None),
    ("Cherry", "#9E1B32", "#FFF5F5", "#FFD166", "♡"), ("Butter", "#FBF1C7", "#3C3836", "#D65D0E", None),
    ("Ocean", "#BEE3F8", "#1A365D", "#F6AD55", "〜"), ("Bubblegum", "#FFC8DD", "#7B2CBF", "#FF5D8F", "★"),
    ("Charcoal", "#3A3A3C", "#FFFFFF", "#FF9F0A", None), ("Sand", "#E9DCC4", "#5E4B36", "#E07A5F", None),
    ("Lilac", "#D7C4F0", "#3D2C5E", "#FF85A1", "✦"), ("Pistachio", "#DDE8B9", "#44533A", "#F28C28", None),
    ("Terracotta", "#C8664B", "#FFF4EC", "#FFE29A", None), ("Ice", "#EAF6FB", "#2B4C5E", "#5BC0EB", "❄︎"),
    ("Sunset", "#FFB4A2", "#6D2E46", "#FFD6A5", "☀︎"),
]

FILM = [  # (name, base, edge-text colour, label)
    ("Amber 400", "#171512", "#E69A3B", "ALTER 400"), ("Gold 200", "#1A1610", "#F2C14E", "ALTER 200"),
    ("Noir 3200", "#0E0E0E", "#D9D9D9", "NOIR 3200"), ("Cine 500T", "#14100E", "#FF6B35", "CINE 500T"),
    ("Slide 64", "#0F1A24", "#7FDBFF", "SLIDE 64"), ("Chrome 100", "#141414", "#E8E8E8", "CHROME 100"),
    ("Sepia 125", "#2A1E14", "#F4D6A0", "SEPIA 125"), ("Rose 160", "#1E1215", "#FF8FAB", "ROSE 160"),
    ("Lime 800", "#121A10", "#B5E655", "LIME 800"), ("Infra 50", "#1A0F14", "#FF4D6D", "INFRA 50"),
    ("Mono 100", "#202020", "#FFFFFF", "MONO 100"), ("Ocean 250", "#0B1C26", "#48CAE4", "OCEAN 250"),
    ("Violet 640", "#160F22", "#C77DFF", "VIOLET 640"), ("Rust 320", "#1F120B", "#E07A5F", "RUST 320"),
    ("Mint 100", "#0F1A17", "#80ED99", "MINT 100"), ("Night 1600", "#08090D", "#9DB4FF", "NIGHT 1600"),
    ("Daylight 50", "#211A12", "#FFD166", "DAYLIGHT 50"),
]
FILM_BASES = ["#171512", "#2B2420", "#121820", "#1E1A2B", "#2A1A14"]

GAMEBOY = [  # (name, body, logo, buttons, text)
    ("Stone", "#B9B4A9", "#3B3B98", "#C0392B", "ALTER"), ("Grape", "#6C4FA3", "#F2E9FF", "#2B1B4A", "ALTER"),
    ("Teal", "#2BA39B", "#0B2E2B", "#F25C54", "POCKET"), ("Banana", "#F6D743", "#3A2E00", "#E63946", "ALTER"),
    ("Cherry", "#D62839", "#FFF1F1", "#1B1B1E", "PIXEL"), ("Berry", "#B5179E", "#FFE5F7", "#3A0CA3", "ALTER"),
    ("Ice", "#DDEBF2", "#2C5D7C", "#5BC0EB", "POCKET"), ("Onyx", "#2B2B2E", "#E5E5E5", "#E63946", "8-BIT"),
    ("Bubblegum", "#FFB3C6", "#7A1F45", "#7209B7", "ALTER"), ("Lime", "#B7E35A", "#1F3A0F", "#3A86FF", "PIXEL"),
    ("Sky", "#8EC5FF", "#0A2463", "#FB5607", "ALTER"), ("Mustard", "#E0A526", "#3B2500", "#264653", "POCKET"),
    ("Coral", "#FF7F6E", "#3D0C02", "#2EC4B6", "ALTER"), ("Forest", "#2F5D50", "#E9F5DB", "#E9C46A", "8-BIT"),
    ("Clear", "#E9ECEF", "#495057", "#ADB5BD", "ALTER"), ("Gold", "#D4AF37", "#2B2100", "#7B2D26", "ALTER"),
    ("Cocoa", "#6F4E37", "#FFE8D6", "#D4A373", "POCKET"),
]

TERMINAL = [  # (name, window, text, prompt accent, command)
    ("Midnight", "#0D1117", "#E6EDF3", "#3FB950", "alter --style"), ("Vampire", "#282A36", "#F8F8F2", "#FF79C6", "alter --dark"),
    ("Solar Light", "#FDF6E3", "#586E75", "#268BD2", "alter --light"), ("Solar Dark", "#002B36", "#93A1A1", "#B58900", "alter --mood"),
    ("Arctic", "#2E3440", "#ECEFF4", "#88C0D0", "alter --cool"), ("Retro Amber", "#1A1200", "#FFB000", "#FFD27F", "run memories.exe"),
    ("Matrix", "#000000", "#00FF41", "#00FF41", "wake up…"), ("Forest", "#1D2021", "#EBDBB2", "#B8BB26", "git commit -m ✨"),
    ("Ocean", "#0F1C2E", "#CFE3FF", "#5CCFE6", "ls ~/memories"), ("Paper", "#FFFFFF", "#24292F", "#CF222E", "sudo make art"),
    ("Candy", "#1E1E2E", "#CDD6F4", "#F5C2E7", "brew install joy"), ("Tokyo", "#1A1B26", "#C0CAF5", "#7AA2F7", "npm run photo"),
    ("Mocha", "#2B211C", "#F1E3D3", "#E3A857", "make coffee"), ("Synth", "#241B2F", "#F8F8F2", "#FF7EDB", "play --loud"),
    ("Mono", "#111111", "#D0D0D0", "#FFFFFF", "echo hello"), ("Rose", "#FFF0F3", "#590D22", "#FF4D6D", "cat love.txt"),
    ("Mint", "#F1FAEE", "#1D3557", "#2A9D8F", "deploy --smile"),
]

COMIC = [  # (name, gutter, dot colour, caption box, text)
    ("Paper", "#FAF7F0", "#E3DCCB", "#FFD23F", None), ("Pop Red", "#FFF1E6", "#F4A39A", "#FFD60A", "POW!"),
    ("Sky Blue", "#E8F4FF", "#A9CCF0", "#FFE45C", "MEANWHILE…"), ("Mint", "#E9FFF4", "#A6E3C4", "#FFB4A2", None),
    ("Sunny", "#FFF9DB", "#F2D16B", "#7FDBFF", "BOOM!"), ("Bubble", "#FFE5EC", "#FFB3C6", "#FFF3B0", "WOW!"),
    ("Noir", "#1B1B1B", "#3A3A3A", "#FFFFFF", "LATER…"), ("Pulp", "#F3E3C3", "#D9B98A", "#E63946", None),
    ("Lilac", "#F3EEFF", "#CDBDF5", "#FFE45C", "ZAP!"), ("Retro", "#FCEBD5", "#E8B07D", "#2EC4B6", None),
    ("Ocean", "#DFF6FF", "#8FD3F4", "#FFCB77", "SPLASH!"), ("Lime", "#F4FFE0", "#C5E88A", "#FF70A6", None),
    ("Halftone", "#FFFFFF", "#9E9E9E", "#FF5252", "KAPOW!"), ("Peach", "#FFEDE1", "#F7B89A", "#5390D9", None),
    ("Night", "#14213D", "#26375E", "#FCA311", "TO BE CONTINUED"), ("Vintage", "#EADCC2", "#C9AE85", "#F4D35E", None),
    ("Candy", "#FFF0FA", "#F7A8D8", "#9BF6FF", "SWEET!"),
]

def spread(rows, n, vary):
    """First pass uses each row as written; later passes reuse rows with `vary(row, pass)` until n."""
    out, p = [], 0
    while len(out) < n:
        for r in rows:
            if len(out) == n: break
            out.append(vary(r, p))
        p += 1
    return out

def stamps():
    out = []
    for p in range(PER_KIND):
        name, cap, val, paper, ink, acc = STAMPS[p % len(STAMPS)]
        suffix, border, mark, fonts = STAMP_STYLES[p // len(STAMPS) % 2]
        if p and p % 3 == 0 and border != "airmail":  # keep variety in border/mark beyond the two base styles
            border, mark = STAMP_EXTRA_BORDERS[p // 3 % 4], STAMP_MARKS[p // 3 % 4]
        out.append(dict(name=name + suffix, paper=paper, ink=ink, accent=acc, text=val,
                        caption="PAR AVION" if border == "airmail" and cap in ("POSTES",) else ("AIR MAIL" if border == "airmail" else cap),
                        border=border, mark=mark, font=fonts[p % len(fonts)], perf=[1, 0.8, 1.25][p % 3]))
    return out

SUFFIX = [None, "II", "III", "IV"]

def named(n, p): return n if p == 0 else f"{n} {SUFFIX[p]}"

def polaroids():
    def v(r, p):
        n, paper, ink, acc, txt = r
        return dict(name=named(n, p), paper=paper, ink=ink, accent=acc, text=txt or (None if p == 0 else "★"),
                    font=HAND[(POLAROID.index(r) + p) % len(HAND)])
    return spread(POLAROID, PER_KIND, v)

def films():
    def v(r, p):
        n, base, ink, txt = r
        return dict(name=named(n, p), paper=base if p == 0 else FILM_BASES[(FILM.index(r) + p) % len(FILM_BASES)], ink=ink, text=txt)
    return spread(FILM, PER_KIND, v)

def gameboys():
    def v(r, p):
        n, body, logo, btn, txt = r
        return dict(name=named(n, p), paper=body, ink=logo, accent=btn, text=txt,
                    font=None if p == 0 else (SANS + HAND)[(GAMEBOY.index(r) + p) % (len(SANS) + len(HAND))])
    return spread(GAMEBOY, PER_KIND, v)

def terminals():
    alt = ["vim ~/story.md", "python3 smile.py", "cargo run --release", "ssh home", "top --memories"]
    def v(r, p):
        n, win, fg, acc, cmd = r
        return dict(name=named(n, p), paper=win, ink=fg, accent=acc, text=cmd if p == 0 else alt[(TERMINAL.index(r) + p) % len(alt)])
    return spread(TERMINAL, PER_KIND, v)

def comics():
    def v(r, p):
        n, gut, dot, box, txt = r
        return dict(name=named(n, p), paper=gut, ink=dot, accent=box, text=txt,
                    font=["ChalkboardSE-Bold", "MarkerFelt-Wide", "Noteworthy-Bold", "AvenirNext-Heavy"][(COMIC.index(r) + p) % 4])
    return spread(COMIC, PER_KIND, v)

def build():
    looks = []
    for kind, gen in [("stamp", stamps), ("polaroid", polaroids), ("film", films),
                      ("gameBoy", gameboys), ("terminal", terminals), ("comic", comics)]:
        items = gen()
        assert len(items) == PER_KIND, kind
        names = [i["name"] for i in items]
        assert len(set(names)) == len(names), (kind, [n for n in names if names.count(n) > 1])
        for i, it in enumerate(items):
            looks.append({"id": f"{kind}-{i + 1:03d}", "kind": kind, "free": i < FREE,
                          **{k: v for k, v in it.items() if v is not None}})
    for l in looks:  # what the app's decoder requires
        assert all(len(l[c]) == 7 and l[c][0] == "#" for c in ("paper", "ink", "accent") if c in l), l
        assert len(l["name"]) <= 30 and len(l.get("text", "")) <= 40, l
    return {"version": 1, "looks": looks}

if __name__ == "__main__":
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "v1", "catalog.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = build()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{len(data['looks'])} looks -> {path}")
