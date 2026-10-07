"""c-murphy (Dryad doi:10.5061/dryad.nq4fs; Murphy et al. 2016 PLoS One) -> iEEG-BIDS (raw).

Source: 7 zips; per block a Blackrock NSx 2.2 '.ns3' (2 kS/s, int16, 128 or 80 amplifier inputs + 1 analog 'dynamometer')
and a Simulink 'SLCData_BlockN.mat' (game/target/dynamometer log).
Signals: the int16 sample bytes of the NSx data packet(s) are written unchanged as BrainVision INT_16 MULTIPLEXED,
with per-channel resolution = (max analog - min analog)/(max digital - min digital) from the NSx extended header
(0.25 uV/bit for amplifier inputs). No filtering, resampling or re-referencing.
Events: target periods from SLCdata.receivedTargetinfo(:,1) (nonzero = force target shown), timed by SLCdata.NSPtime
minus the NSx packet timestamp. Alignment checked by correlating SLC dynamometer with the NSx dynamometer channel.
Privacy: NSx TimeOrigin day -> 01 (weekday recomputed) and MAT text-header 'Created on' date -> 'Mmm 01 yyyy' in the
sourcedata copies; BIDS scans.tsv acq_time uses YYYY-MM-01. Original/patched sha256 recorded.
Usage: python b3w3_convert_murphy.py <sourcedata_dl> <bids_root>
"""
import datetime, hashlib, io, json, os, re, shutil, struct, sys, zipfile
import numpy as np, scipy.io as sio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b3w3_common import wtsv, wjson, write_vhdr, scrub_mat_header, sha256_file

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
SD = os.path.join(OUT, "sourcedata", "dryad-nq4fs-deidentified")
os.makedirs(SD, exist_ok=True)
report = {"runs": [], "sourcedata": []}


def parse_ns3(b):
    assert b[:8] == b"NEURALCD"
    hb, = struct.unpack("<I", b[10:14])
    period, tres = struct.unpack("<II", b[286:294])
    to = list(struct.unpack("<8H", b[294:310]))
    nch, = struct.unpack("<I", b[310:314])
    ch = []
    for k in range(nch):
        e = b[314 + 66 * k: 314 + 66 * (k + 1)]
        eid, = struct.unpack("<H", e[2:4])
        lab = e[4:20].split(b"\0")[0].decode()
        mind, maxd, mina, maxa = struct.unpack("<hhhh", e[22:30])
        unit = e[30:46].split(b"\0")[0].decode()
        hf, ho, ht, lf, lo, lt = struct.unpack("<IIHIIH", e[46:66])
        ch.append(dict(id=eid, label=lab, mind=mind, maxd=maxd, mina=mina, maxa=maxa, unit=unit,
                       hp_mHz=hf, hp_order=ho, hp_type=ht, lp_mHz=lf, lp_order=lo, lp_type=lt))
    pk, pos = [], hb
    while pos < len(b):
        assert b[pos] == 1, ("packet header", pos)
        ts, n = struct.unpack("<II", b[pos + 1: pos + 9])
        pk.append((ts, n, pos + 9))
        pos += 9 + n * nch * 2
    assert pos == len(b), (pos, len(b))
    return dict(hb=hb, period=period, tres=tres, origin=to, nch=nch, ch=ch, packets=pk)


def deid_ns3(b, to):
    y, mo = to[0], to[1]
    wd = (datetime.date(y, mo, 1).weekday() + 1) % 7  # SYSTEMTIME: 0 = Sunday
    nb = bytearray(b)
    nb[294 + 4: 294 + 8] = struct.pack("<HH", wd, 1)
    return bytes(nb)


UNIT = {"uV": "µV", "mV": "mV"}
blocks = []
for zn in sorted(x for x in os.listdir(SRC) if x.endswith(".zip")):
    z = zipfile.ZipFile(os.path.join(SRC, zn))
    sub = re.match(r"Participant([A-D])", zn).group(1)
    for n in sorted(x for x in z.namelist() if x.endswith(".ns3")):
        parts = n.split("/")
        if zn.startswith("ParticipantA"):
            grasp = re.match(r"ParticipantA(Power|Pinch)", zn).group(1).lower(); cond = parts[0].lower()
        else:
            grasp = parts[1].lower(); cond = parts[2].lower()
        blk = int(re.search(r"Block(\d+)\.ns3$", n).group(1))
        slc = n.replace("NSPdata", "SLCdata").replace(f"Block{blk}.ns3", f"SLCData_Block{blk}.mat")
        blocks.append((sub, grasp, cond, blk, zn, n, slc if slc in z.namelist() else None))

scans = {}
for sub, grasp, cond, blk, zn, n, slc in blocks:
    z = zipfile.ZipFile(os.path.join(SRC, zn))
    raw = z.read(n)
    H = parse_ns3(raw)
    fs = H["tres"] / H["period"]
    task = grasp + cond
    S = f"sub-{sub}"
    D = os.path.join(OUT, S, "ieeg"); os.makedirs(D, exist_ok=True)
    stem = f"{S}_task-{task}_run-{blk}"
    # packets: require contiguity
    nch = H["nch"]
    pk = H["packets"]
    gaps = []
    for (t0, n0, _), (t1, _, _) in zip(pk[:-1], pk[1:]):
        exp = t0 + n0 * H["period"]
        if t1 != exp:
            gaps.append((t0, n0, t1, exp))
    nsamp = sum(p[1] for p in pk)
    h = hashlib.sha256()
    with open(os.path.join(D, stem + "_ieeg.eeg"), "wb") as fo:
        for ts, ns, off in pk:
            seg = raw[off: off + ns * nch * 2]
            h.update(seg); fo.write(seg)
    res, units, names, types = [], [], [], []
    for c in H["ch"]:
        r = (c["maxa"] - c["mina"]) / (c["maxd"] - c["mind"])
        res.append(r); units.append(UNIT.get(c["unit"], c["unit"])); names.append(c["label"])
        types.append("MISC" if c["id"] > 128 else "SEEG")
    # events from SLCdata
    ev, align = [], None
    t0s = pk[0][0] / H["tres"]
    if slc:
        m = sio.loadmat(io.BytesIO(z.read(slc)), squeeze_me=True, struct_as_record=False)["SLCdata"]
        nt = np.asarray(m.NSPtime, float); tg = np.asarray(m.receivedTargetinfo)[:, 0].astype(int)
        dyn = np.asarray(m.receiveddynamometer, float)
        on = nt - t0s
        chg = np.flatnonzero(np.diff(np.r_[0, tg]) != 0)
        for i in chg:
            if tg[i] == 0:
                continue
            j = i
            while j + 1 < len(tg) and tg[j + 1] == tg[i]:
                j += 1
            end = on[j + 1] if j + 1 < len(on) else on[j]
            ev.append([round(on[i], 6), round(end - on[i], 6), "target", int(tg[i]), int(round(on[i] * fs))])
        # alignment check: NSx dynamometer channel sampled at SLC times
        di = [k for k, c in enumerate(H["ch"]) if c["label"] == "dynamometer"]
        if di:
            x = np.frombuffer(raw[pk[0][2]: pk[0][2] + pk[0][1] * nch * 2], dtype="<i2").reshape(-1, nch)[:, di[0]].astype(float)
            idx = np.round(on * fs).astype(int); ok = (idx >= 0) & (idx < len(x))
            if ok.sum() > 10 and np.std(dyn[ok]) > 0 and np.std(x[idx[ok]]) > 0:
                align = float(np.corrcoef(dyn[ok], x[idx[ok]])[0, 1])
    wtsv(os.path.join(D, stem + "_events.tsv"), ["onset", "duration", "trial_type", "value", "sample"], ev)
    write_vhdr(os.path.join(D, stem + "_ieeg"), nch, fs, names, units, fmt="INT_16", resolutions=res,
               comment=f"b3w3_convert_murphy.py: int16 samples of {zn}:{n} copied unchanged",
               markers=[("Stimulus", f"target_{e[3]}", e[4], max(1, int(round(e[1] * fs)))) for e in ev])
    flt = H["ch"][0]
    rows = []
    for c, t, u, r in zip(H["ch"], types, units, res):
        rows.append([c["label"], t, u, round(c["hp_mHz"] / 1000, 3) if c["hp_type"] else "n/a", round(c["lp_mHz"] / 1000, 3) if c["lp_type"] else "n/a",
                     fs, "n/a", "good", "n/a",
                     ("NSx electrode ID %d; amplifier input; contact identity/location not released" % c["id"] if t == "SEEG"
                      else "NSx analog input %d: grasp dynamometer / pinch gauge force signal" % c["id"]) + "; resolution %.6g %s/bit" % (r, u)])
    wtsv(os.path.join(D, stem + "_channels.tsv"), ["name", "type", "units", "low_cutoff", "high_cutoff", "sampling_frequency", "group", "status", "status_description", "description"], rows)
    nseeg = types.count("SEEG")
    wjson(os.path.join(D, stem + "_ieeg.json"), {
        "TaskName": task,
        "TaskDescription": f"Force-matching task, {'power grasp (dynamometer)' if grasp == 'power' else 'lateral pinch (pinch gauge)'}, {'executed' if cond == 'executed' else 'imagined (no force applied; visual cues still given)'}: targets at three force levels (20, 30 and 40% of maximum voluntary contraction per the article) shown for 5 s with 5 s rest, 5 trials per level per block.",
        "Instructions": "n/a",
        "SamplingFrequency": fs, "PowerLineFrequency": 60,
        "SoftwareFilters": "n/a",
        "HardwareFilters": {"NSx extended header (amplifier inputs)": {"HighPassCorner_Hz": flt["hp_mHz"] / 1000, "HighPassOrder": flt["hp_order"], "HighPassType": flt["hp_type"],
                                                                       "LowPassCorner_Hz": flt["lp_mHz"] / 1000, "LowPassOrder": flt["lp_order"], "LowPassType": flt["lp_type"]}},
        "iEEGReference": "Hardware reference: a depth electrode contact in a different anatomical region not related to seizure generation (article, Methods)",
        "Manufacturer": "Blackrock Microsystems", "ManufacturersModelName": "Neuroport",
        "RecordingDuration": nsamp / fs, "RecordingType": "continuous",
        "SEEGChannelCount": nseeg, "ECOGChannelCount": 0, "MiscChannelCount": types.count("MISC"),
        "iEEGElectrodeInfo": "SEEG depth electrodes (Integra or PMT, per the article); signals split from the clinical Nihon Kohden system",
        "ElectricalStimulation": False,
    })
    y, mo = H["origin"][0], H["origin"][1]
    hh, mi, ss = H["origin"][4:7]
    scans.setdefault(S, []).append([f"ieeg/{stem}_ieeg.vhdr", f"{y:04d}-{mo:02d}-01T{hh:02d}:{mi:02d}:{ss:02d}"])
    # roundtrip: MNE read-back of the first 10 s vs source int16 x resolution
    import mne
    rr = mne.io.read_raw_brainvision(os.path.join(D, stem + "_ieeg.vhdr"), preload=False, verbose="error")
    k = int(min(10 * fs, pk[0][1]))
    a = rr.get_data(start=0, stop=k)
    src = np.frombuffer(raw[pk[0][2]: pk[0][2] + k * nch * 2], dtype="<i2").reshape(k, nch).T.astype(float) * np.array(res)[:, None]
    scale = np.array([1e-6 if u == "µV" else 1e-3 if u == "mV" else 1.0 for u in units])[:, None]
    rt_ok = bool(rr.n_times == nsamp and rr.ch_names == names and np.allclose(a, src * scale, rtol=1e-6, atol=1e-12))
    report["runs"].append(dict(roundtrip_ok=rt_ok, sub=sub, task=task, run=blk, zip=zn, member=n, slc=slc, nch=nch, sfreq=fs, n_samples=nsamp, packets=len(pk),
                               packet_gaps=gaps, sha256_int16=h.hexdigest(), n_events=len(ev), slc_dyn_corr=align, first_ts=pk[0][0]))
    print("run", stem, "roundtrip", rt_ok, nch, nsamp, "packets", len(pk), "gaps", len(gaps), "events", len(ev), "dyncorr", align, flush=True)

for S, rows in scans.items():
    wtsv(os.path.join(OUT, S, f"{S}_scans.tsv"), ["filename", "acq_time"], sorted(rows))

# de-identified sourcedata
for zn in sorted(x for x in os.listdir(SRC) if x.endswith(".zip")):
    z = zipfile.ZipFile(os.path.join(SRC, zn))
    for i in z.infolist():
        if i.is_dir():
            continue
        b = z.read(i)
        o = hashlib.sha256(b).hexdigest()
        note = "unchanged"
        if i.filename.endswith(".ns3"):
            H = parse_ns3(b); b = deid_ns3(b, H["origin"]); note = "NSx TimeOrigin day -> 01, weekday recomputed"
        elif i.filename.endswith(".mat"):
            b, ch = scrub_mat_header(b); note = "MAT text header date -> Mmm 01 yyyy" if ch else "unchanged"
        rel = os.path.join(zn[:-4], i.filename)
        t = os.path.join(SD, rel); os.makedirs(os.path.dirname(t), exist_ok=True)
        open(t, "wb").write(b)
        report["sourcedata"].append([rel, i.file_size, o, hashlib.sha256(b).hexdigest(), note])
for f in sorted(os.listdir(SRC)):
    if f.endswith(".txt"):
        shutil.copy(os.path.join(SRC, f), os.path.join(SD, f))
        report["sourcedata"].append([f, os.path.getsize(os.path.join(SRC, f)), sha256_file(os.path.join(SRC, f)), sha256_file(os.path.join(SD, f)), "unchanged"])
wtsv(os.path.join(SD, "DEIDENTIFICATION_MANIFEST.tsv"), ["path", "bytes_original", "sha256_original", "sha256_here", "change"], report["sourcedata"])
os.makedirs(os.path.join(OUT, "code"), exist_ok=True)
for f in (__file__, os.path.join(os.path.dirname(os.path.abspath(__file__)), "b3w3_common.py")):
    shutil.copy(f, os.path.join(OUT, "code", os.path.basename(f)))
json.dump(report, open(os.path.join(OUT, "code", "conversion_report.json"), "w"), indent=1, default=str)
print(json.dumps({"runs": len(report["runs"]), "gaps": sum(len(r["packet_gaps"]) for r in report["runs"]), "multi_packet": sum(r["packets"] > 1 for r in report["runs"]),
                  "roundtrip_all_ok": all(r["roundtrip_ok"] for r in report["runs"]), "dyncorr_min": min((r["slc_dyn_corr"] for r in report["runs"] if r["slc_dyn_corr"] is not None), default=None)}, indent=1))
print("CONVERT_DONE")
