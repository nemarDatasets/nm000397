import argparse
import csv
import hashlib
import re
import struct
from pathlib import Path

import numpy as np

BAD_FRACTION = 0.01
HIGH_STD_UV = 1500.0
SOURCE = Path("sourcedata/dryad-nq4fs-deidentified")


def read_vhdr(path):
    txt = path.read_text(encoding="utf-8")
    assert "BinaryFormat=INT_16" in txt and "DataOrientation=MULTIPLEXED" in txt, path
    zip_name, member = re.search(r"int16 samples of (\S+)\.zip:(\S+) copied unchanged", txt).groups()
    names = re.findall(r"^Ch\d+=([^,]*),", txt, flags=re.M)
    return names, SOURCE / zip_name / member


def read_nsx(raw):
    assert raw[:8] == b"NEURALCD"
    (header_bytes,) = struct.unpack("<I", raw[10:14])
    (nch,) = struct.unpack("<I", raw[310:314])
    ranges = [struct.unpack("<hhhh", raw[314 + 66 * k + 22 : 314 + 66 * k + 30]) for k in range(nch)]
    units = [raw[314 + 66 * k + 30 : 314 + 66 * k + 46].split(b"\0")[0].decode() for k in range(nch)]
    packets, pos = [], header_bytes
    while pos < len(raw):
        assert raw[pos] == 1, pos
        (n,) = struct.unpack("<I", raw[pos + 5 : pos + 9])
        packets.append(np.frombuffer(raw, "<i2", n * nch, pos + 9).reshape(n, nch))
        pos += 9 + n * nch * 2
    return ranges, units, np.concatenate(packets)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="nm000397 dataset root (with the NSx files of sourcedata/)")
    root = parser.parse_args().root
    with open(root / SOURCE / "DEIDENTIFICATION_MANIFEST.tsv", encoding="utf-8") as f:
        manifest = {r["path"]: r["sha256_here"] for r in csv.DictReader(f, delimiter="\t")}
    print("| recording | samples | inputs | NSx digital / analog range of the inputs "
          "| inputs > 1%: % of samples at or beyond the NSx digital range (abs count >= 32764) "
          "| max % of the other inputs | inputs with std >= 1.5 mV | NSx int16 = .eeg int16; NSx sha256 = manifest |")
    print("|---|---:|---:|---|---|---:|---:|---|")
    n_files = n_bad = n_rail = n_limit = 0
    for vhdr in sorted(root.glob("sub-*/ieeg/*_ieeg.vhdr")):
        names, nsx_path = read_vhdr(vhdr)
        x = np.fromfile(vhdr.with_suffix(".eeg"), dtype="<i2").reshape(-1, len(names))
        nsx_raw = (root / nsx_path).read_bytes()
        ranges, units, nsx = read_nsx(nsx_raw)
        inputs = [j for j, name in enumerate(names) if name.startswith("chan")]
        (min_d, max_d, min_a, max_a), *rest = {ranges[j] for j in inputs}
        assert not rest and {units[j] for j in inputs} == {"uV"} and min_d == -max_d, vhdr
        counts = np.abs(x[:, inputs].astype(np.int32))
        rail = counts >= max_d
        frac = rail.mean(axis=0)
        bad = frac > BAD_FRACTION
        std_uv = x[:, inputs].std(axis=0) * (max_a - min_a) / (max_d - min_d)
        listed = ", ".join(f"{names[j]} {100 * f:.1f}" for j, f in zip(inputs, frac) if f > BAD_FRACTION)
        other = 100 * frac[~bad].max() if (~bad).any() else float("nan")
        same = np.array_equal(nsx, x)
        sha = hashlib.sha256(nsx_raw).hexdigest() == manifest[str(nsx_path.relative_to(SOURCE))]
        print(f"| {vhdr.name.removesuffix('_ieeg.vhdr')} | {len(x)} | {len(inputs)} | ±{max_d} / ±{max_a} uV "
              f"| {bad.sum()}: {listed or '-'} | {other:.2f} | {(std_uv >= HIGH_STD_UV).sum()} "
              f"| {'yes' if same else 'NO'}; {'yes' if sha else 'NO'} |")
        n_files += 1
        n_bad += int(bad.sum())
        n_rail += int(rail[:, bad].sum())
        pinned = x[:, inputs][:, bad]
        n_limit += int(((pinned == -32768) | (pinned == 32767)).sum())
    print(f"\n{n_files} recordings, {n_bad} amplifier inputs with more than 1% of samples at abs count >= 32764; "
          f"{100 * n_limit / n_rail:.1f}% of those inputs' samples at abs count >= 32764 are at -32768 or 32767.")


if __name__ == "__main__":
    main()
