"""Собирает manifest.json для автообновления Hermea: python3 tools/build_manifest.py 1.2.0"""
import hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES = json.load(open(os.path.join(ROOT, "tools", "notes.json"), encoding="utf-8"))
EXEC_EXT = (".command",)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main(version):
    files = []
    for base, target in (("program", ""), ("bundle", "../Hermea.app/")):
        for dp, _, fs in os.walk(os.path.join(ROOT, base)):
            for f in sorted(fs):
                full = os.path.join(dp, f)
                rel = os.path.relpath(full, os.path.join(ROOT, base)).replace(os.sep, "/")
                files.append({"path": target + rel, "src": base + "/" + rel, "sha256": sha(full),
                              "exec": f.endswith(EXEC_EXT) or rel == "Contents/MacOS/Hermea"})
    files.sort(key=lambda x: x["path"])
    m = {"version": version, "notes": NOTES.get(version, {}), "pip": [], "files": files}
    json.dump(m, open(os.path.join(ROOT, "manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(ROOT, "VERSION"), "w").write(version + "\n")
    print(f"manifest {version}: {len(files)} files")


if __name__ == "__main__":
    main(sys.argv[1])
