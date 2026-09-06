#!/usr/bin/env python3
"""List every normative-document section for independent prose-to-obligation review."""
import argparse
import json
from pathlib import Path
from audit_evidence import source_sections

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("app_spec", type=Path)
    print(json.dumps(source_sections(parser.parse_args().app_spec.resolve()), ensure_ascii=False, indent=2))
