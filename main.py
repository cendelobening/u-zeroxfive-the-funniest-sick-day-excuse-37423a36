#!/usr/bin/env python3
"""Write the funniest sick-day excuse to $MAKEFUN_OUTPUT_DIR/entry.txt.

Single line, under 200 characters, no trailing newline. Pure stdlib.
"""

import os
import sys
import tempfile

# Final excuse: tightened for rhythm — "spent all night" sets the scene,
# the diagnosis lands mid-line, and "either way" is the shrug that closes it.
LINE = "I spent all night Googling my symptoms and I'm either dying or a hypochondriac, so either way, I won't be in today."

OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "entry.txt")


def main() -> int:
    if "\n" in LINE or "\r" in LINE:
        print("error: excuse must be exactly one line", file=sys.stderr)
        return 1
    if not 1 <= len(LINE) <= 199:
        print("error: excuse must be 1-199 chars, got %d" % len(LINE),
              file=sys.stderr)
        return 1

    data = LINE.encode("utf-8")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=OUTPUT_DIR, prefix=".entry-",
                                    suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, OUTPUT_PATH)
    except OSError as exc:
        print("error: write failed: %s" % exc, file=sys.stderr)
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        return 1

    # Verify what landed on disk.
    try:
        with open(OUTPUT_PATH, "rb") as fh:
            back = fh.read()
        mode = os.stat(OUTPUT_PATH).st_mode & 0o777
    except OSError as exc:
        print("error: verify failed: %s" % exc, file=sys.stderr)
        return 1
    if back != data:
        print("error: bytes on disk differ from excuse", file=sys.stderr)
        return 1
    if mode != 0o644:
        print("error: mode is %o, expected 0644" % mode, file=sys.stderr)
        return 1
    text = back.decode("utf-8")
    if text != LINE or len(text) > 199 or "\n" in text:
        print("error: content verification failed", file=sys.stderr)
        return 1
    print("wrote %s (%d chars, %d bytes)" % (OUTPUT_PATH, len(LINE),
                                             len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
