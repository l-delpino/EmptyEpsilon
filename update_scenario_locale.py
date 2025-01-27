# python3 script to update localization files.

import glob
import subprocess
import json
import os

def update_other_languages(base):
    assert base.endswith(".en.po")
    for other in glob.glob(base[:-5] + "*.po"):
        if other == base:
            continue
        print("Merge %s -> %s" % (base, other))
        cmd = ["msgmerge", "-U", other, base]
        subprocess.run(cmd, check=True)


os.makedirs("scripts/locale", exist_ok=True)
for scenario in glob.glob("scripts/scenario_*.lua"):
    output = scenario.replace(".lua", ".en.po").replace("scripts/", "scripts/locale/")
    info = {}
    key = None
    for line in open(scenario):
        if not line.startswith("--"):
            break
        if line.startswith("---"):
            if key is not None:
                info[key] = info[key] + "\n" + line[3:].strip()
        elif ":" in line:
            key, _, value = line[2:].partition(":")
            key = key.strip().lower()
            value = value.strip()
            info[key] = value
    f = open(output, "wt")
    if "name" in info:
        f.write("# Scenario name\n")
        f.write("msgid %s\n" % (json.dumps(info["name"])))
        f.write("msgstr \"\"\n")
    if "description" in info:
        f.write("# Scenario description\n")
        f.write("msgid %s\n" % (json.dumps(info["description"].replace("\r", ""))))
        f.write("msgstr \"\"\n")
    f.close()
    print(open(output, "rt").read())
    cmd = ["xgettext", "--keyword=_:1c,2", "--keyword=_:1", "--omit-header", "-j", "-d", output[:-3], "-C", "-"]
    subprocess.run(cmd, check=True, input=b"")
    pre = open(output, "rt").read()
    cmd = ["xgettext", "--keyword=_:1c,2", "--keyword=_:1", "--omit-header", "-j", "-d", output[:-3], scenario]
    subprocess.run(cmd, check=True)
    post = open(output, "rt").read()
    if pre == post:
        os.unlink(output)
        print("Skipped %s" % (scenario))
    else:
        update_other_languages(output)
        print("Done %s" % (scenario))

update_other_languages("resources/locale/main.en.po")
update_other_languages("resources/locale/tutorial.en.po")
