
import re
import sys

def migrate_prints_to_log(filepath):
    with open(filepath, "r") as f:
        lines = f.readlines()

    updated = []
    pattern = re.compile(r'^\s*print\(f?"\\[(\w+)\\]\s?(.*?)"\)$')

    for line in lines:
        match = pattern.match(line.strip())
        if match:
            tag, msg = match.groups()
            updated.append(f'log("{tag}", f"{msg}")\n')
        else:
            updated.append(line)

    with open(filepath, "w") as f:
        f.writelines(updated)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate_prints.py path/to/script.py")
        sys.exit(1)

    target_file = sys.argv[1]
    migrate_prints_to_log(target_file)
    print(f"✅ Migration complete: {target_file}")
