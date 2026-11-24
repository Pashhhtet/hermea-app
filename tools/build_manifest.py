"""Собирает manifest.json для автообновления Hermea: python3 tools/build_manifest.py 1.2.0"""
import hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES = json.load(open(os.path.join(ROOT, "tools", "notes.json"), encoding="utf-8"))
EXEC_EXT = (".command",)
PIP = ["pypdf>=4", "reportlab>=4,<4.3"]    # reportlab 4.3+ не работает на Python 3.9 (встроенный в macOS)          # библиотеки, которые нужно доставить при обновлении
SKIP = {"telegram.txt", "готово.txt", "app_settings.json", "app_searches.json", "app_svk.json", "update.json",
        "app_clients.json", "app_market.json", "app_owners.json", "app_calls.json"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main(version):
    files = []
    for base, target in (("program", ""), ("bundle", "../Hermea.app/")):
        for dp, dirs, fs in os.walk(os.path.join(ROOT, base)):
            dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".")]
            for f in sorted(fs):
                if f.endswith((".pyc", ".DS_Store")) or f in SKIP:
                    continue
                full = os.path.join(dp, f)
                rel = os.path.relpath(full, os.path.join(ROOT, base)).replace(os.sep, "/")
                files.append({"path": target + rel, "src": base + "/" + rel, "sha256": sha(full),
                              "exec": f.endswith(EXEC_EXT) or rel == "Contents/MacOS/Hermea"})
    files.sort(key=lambda x: x["path"])
    m = {"version": version, "notes": NOTES.get(version, {}), "pip": PIP, "files": files}
    json.dump(m, open(os.path.join(ROOT, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(ROOT, "VERSION"), "w").write(version + "\n")
    print(f"manifest {version}: {len(files)} files")


if __name__ == "__main__":
    import subprocess
    # перед релизом: вкладки не должны перебивать стили друг друга
    if subprocess.call([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "css_check.py")]) != 0:
        sys.exit("CSS: один класс задан в разных файлах, переименуй перед релизом")
    main(sys.argv[1])
