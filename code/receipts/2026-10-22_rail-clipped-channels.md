# Mark rail-clipped amplifier inputs as bad

**Claim**: 394 amplifier inputs in 24 recordings (sub-A 2, sub-B 130, sub-C 262) have more than 1% of samples at the
±8191 uV rail (digital ±32764), up to 48.2%, and are marked `bad`; the clipping is in the Dryad NSx files.

**Source**
- PR nemarDatasets/nm000397#3, computed at head `ddb33041`. Data: NEMAR copy of `origin/main` `1dbc0521` (only a CI
  workflow change since the PR base `a0cacab4`). The sha256 of each of the 92 BrainVision files read (46 `.vhdr`,
  46 `.eeg`) equals its SHA256E git-annex key at `1dbc0521`.
- The 46 NSx files of `sourcedata/dryad-nq4fs-deidentified/` were fetched from NEMAR storage by annex key (sha256
  verified against the keys at `1dbc0521`). Their sha256 equals `sha256_here` in `DEIDENTIFICATION_MANIFEST.tsv`
  (last column), which gives each file's Dryad sha256 and the only change (NSx TimeOrigin day set to 01).
- Upstream: Dryad doi:10.5061/dryad.nq4fs, version 1 (2016-04-21).

**Method**: numpy reads the `.eeg` int16 counts and the NSx 2.2 file (extended headers and data packets); no MNE,
no scaling. Amplifier inputs are `chan1`-`chan128` (`dynamometer` excluded). Every amplifier input's NSx extended
header declares digital ±32764 for analog ±8191 uV (0.25 uV/count). Per input: fraction of all samples with
|count| >= 32764 (at or beyond the declared digital range); `bad` if above 1%. The 1% cut-off is the PR's rule, not
taken from a source: the fractions form a continuum (see the max of the other inputs). 99.8% of the counted samples
are at -32768 or 32767, the int16 limits just beyond ±32764. The std column (0.25 uV/count) checks the PR
description's 41 of 80 sub-C inputs with std >= 1.5 mV.

**Result** (script output, unedited)

| recording | samples | inputs | NSx digital / analog range of the inputs | inputs > 1%: % of samples at or beyond the NSx digital range (abs count >= 32764) | max % of the other inputs | inputs with std >= 1.5 mV | NSx int16 = .eeg int16; NSx sha256 = manifest |
|---|---:|---:|---|---|---:|---:|---|
| sub-A_task-pinchexecuted_run-1 | 328142 | 128 | ±32764 / ±8191 uV | 0: - | 0.50 | 0 | yes; yes |
| sub-A_task-pinchexecuted_run-2 | 328904 | 128 | ±32764 / ±8191 uV | 0: - | 0.01 | 0 | yes; yes |
| sub-A_task-pinchexecuted_run-3 | 322464 | 128 | ±32764 / ±8191 uV | 1: chan97 7.6 | 0.00 | 1 | yes; yes |
| sub-A_task-pinchexecuted_run-4 | 320744 | 128 | ±32764 / ±8191 uV | 0: - | 0.00 | 0 | yes; yes |
| sub-A_task-pinchimagined_run-1 | 326344 | 128 | ±32764 / ±8191 uV | 0: - | 0.71 | 1 | yes; yes |
| sub-A_task-pinchimagined_run-2 | 322282 | 128 | ±32764 / ±8191 uV | 1: chan97 1.1 | 0.00 | 1 | yes; yes |
| sub-A_task-pinchimagined_run-3 | 322962 | 128 | ±32764 / ±8191 uV | 0: - | 0.00 | 0 | yes; yes |
| sub-A_task-pinchimagined_run-4 | 323524 | 128 | ±32764 / ±8191 uV | 0: - | 0.00 | 0 | yes; yes |
| sub-A_task-powerexecuted_run-1 | 532986 | 128 | ±32764 / ±8191 uV | 0: - | 0.33 | 0 | yes; yes |
| sub-A_task-powerexecuted_run-2 | 321122 | 128 | ±32764 / ±8191 uV | 0: - | 0.30 | 1 | yes; yes |
| sub-A_task-powerexecuted_run-3 | 328862 | 128 | ±32764 / ±8191 uV | 0: - | 0.06 | 0 | yes; yes |
| sub-A_task-powerexecuted_run-4 | 324324 | 128 | ±32764 / ±8191 uV | 0: - | 0.08 | 1 | yes; yes |
| sub-A_task-powerimagined_run-1 | 323244 | 128 | ±32764 / ±8191 uV | 0: - | 0.00 | 0 | yes; yes |
| sub-A_task-powerimagined_run-2 | 327522 | 128 | ±32764 / ±8191 uV | 0: - | 0.03 | 0 | yes; yes |
| sub-A_task-powerimagined_run-3 | 323844 | 128 | ±32764 / ±8191 uV | 0: - | 0.00 | 0 | yes; yes |
| sub-A_task-powerimagined_run-4 | 325184 | 128 | ±32764 / ±8191 uV | 0: - | 0.26 | 0 | yes; yes |
| sub-B_task-pinchexecuted_run-1 | 325822 | 128 | ±32764 / ±8191 uV | 10: chan47 39.4, chan48 41.0, chan57 43.3, chan58 43.4, chan59 42.9, chan60 42.3, chan61 43.0, chan62 42.9, chan63 43.5, chan64 42.9 | 0.00 | 10 | yes; yes |
| sub-B_task-pinchexecuted_run-2 | 323882 | 128 | ±32764 / ±8191 uV | 10: chan47 39.1, chan48 41.0, chan57 43.0, chan58 43.2, chan59 42.5, chan60 42.0, chan61 42.8, chan62 42.6, chan63 43.3, chan64 42.5 | 0.41 | 10 | yes; yes |
| sub-B_task-pinchexecuted_run-3 | 326662 | 128 | ±32764 / ±8191 uV | 10: chan47 39.1, chan48 40.9, chan57 42.9, chan58 43.0, chan59 42.5, chan60 41.8, chan61 42.5, chan62 42.5, chan63 43.2, chan64 42.5 | 0.00 | 10 | yes; yes |
| sub-B_task-pinchexecuted_run-4 | 324282 | 128 | ±32764 / ±8191 uV | 10: chan47 39.2, chan48 40.8, chan57 42.8, chan58 43.0, chan59 42.5, chan60 41.8, chan61 42.5, chan62 42.4, chan63 43.1, chan64 42.4 | 0.00 | 10 | yes; yes |
| sub-B_task-pinchimagined_run-1 | 324782 | 128 | ±32764 / ±8191 uV | 10: chan47 39.1, chan48 40.9, chan57 43.0, chan58 43.1, chan59 42.6, chan60 41.9, chan61 42.6, chan62 42.6, chan63 43.2, chan64 42.6 | 0.00 | 10 | yes; yes |
| sub-B_task-pinchimagined_run-2 | 322982 | 128 | ±32764 / ±8191 uV | 10: chan47 39.3, chan48 40.9, chan57 42.9, chan58 43.0, chan59 42.6, chan60 42.0, chan61 42.7, chan62 42.5, chan63 43.2, chan64 42.5 | 0.00 | 10 | yes; yes |
| sub-B_task-pinchimagined_run-3 | 320722 | 128 | ±32764 / ±8191 uV | 10: chan47 39.1, chan48 40.8, chan57 42.9, chan58 43.1, chan59 42.5, chan60 41.8, chan61 42.6, chan62 42.5, chan63 43.2, chan64 42.5 | 0.00 | 10 | yes; yes |
| sub-B_task-powerexecuted_run-1 | 325942 | 128 | ±32764 / ±8191 uV | 8: chan57 42.9, chan58 42.2, chan59 42.2, chan60 41.1, chan61 41.6, chan62 42.0, chan63 42.6, chan64 42.2 | 0.00 | 10 | yes; yes |
| sub-B_task-powerexecuted_run-2 | 338022 | 128 | ±32764 / ±8191 uV | 8: chan57 42.8, chan58 42.3, chan59 42.2, chan60 41.0, chan61 41.6, chan62 42.0, chan63 42.6, chan64 42.2 | 0.00 | 10 | yes; yes |
| sub-B_task-powerexecuted_run-3 | 318922 | 128 | ±32764 / ±8191 uV | 8: chan57 42.6, chan58 42.1, chan59 42.0, chan60 40.8, chan61 41.5, chan62 41.8, chan63 42.4, chan64 41.9 | 0.00 | 10 | yes; yes |
| sub-B_task-powerexecuted_run-4 | 323182 | 128 | ±32764 / ±8191 uV | 10: chan47 39.0, chan48 40.6, chan57 42.3, chan58 42.2, chan59 42.0, chan60 40.9, chan61 41.3, chan62 41.7, chan63 42.5, chan64 42.0 | 0.00 | 10 | yes; yes |
| sub-B_task-powerimagined_run-1 | 322044 | 128 | ±32764 / ±8191 uV | 8: chan57 42.4, chan58 41.5, chan59 41.6, chan60 40.2, chan61 40.8, chan62 41.3, chan63 42.1, chan64 41.6 | 0.00 | 8 | yes; yes |
| sub-B_task-powerimagined_run-2 | 327322 | 128 | ±32764 / ±8191 uV | 8: chan57 41.9, chan58 41.4, chan59 41.2, chan60 40.0, chan61 40.8, chan62 41.1, chan63 41.8, chan64 40.9 | 0.14 | 9 | yes; yes |
| sub-B_task-powerimagined_run-3 | 347802 | 128 | ±32764 / ±8191 uV | 10: chan47 39.1, chan48 40.7, chan57 42.1, chan58 41.9, chan59 41.7, chan60 40.5, chan61 41.0, chan62 41.5, chan63 42.3, chan64 41.7 | 0.00 | 10 | yes; yes |
| sub-C_task-pinchexecuted_run-1 | 318330 | 80 | ±32764 / ±8191 uV | 35: chan49 16.4, chan50 3.0, chan51 3.0, chan52 2.9, chan53 10.6, chan54 12.9, chan55 9.2, chan56 9.0, chan57 3.3, chan58 3.1, chan61 3.1, chan62 3.2, chan63 3.2, chan64 4.0, chan69 1.4, chan73 43.8, chan74 39.5, chan75 44.9, chan76 45.4, chan113 47.5, chan114 47.3, chan115 47.5, chan116 47.4, chan117 47.4, chan118 47.6, chan119 47.3, chan120 47.6, chan121 47.1, chan122 46.8, chan123 46.9, chan124 46.3, chan125 47.0, chan126 46.9, chan127 46.9, chan128 46.9 | 0.85 | 41 | yes; yes |
| sub-C_task-pinchexecuted_run-2 | 328290 | 80 | ±32764 / ±8191 uV | 27: chan49 14.5, chan53 6.8, chan54 9.9, chan55 5.0, chan56 4.9, chan69 1.1, chan70 1.0, chan73 44.0, chan74 42.0, chan75 45.3, chan76 45.6, chan113 47.5, chan114 47.3, chan115 47.5, chan116 47.4, chan117 47.4, chan118 47.8, chan119 47.2, chan120 47.6, chan121 47.2, chan122 46.9, chan123 46.9, chan124 46.4, chan125 47.2, chan126 46.8, chan127 46.8, chan128 47.0 | 0.59 | 41 | yes; yes |
| sub-C_task-pinchexecuted_run-3 | 320770 | 80 | ±32764 / ±8191 uV | 32: chan49 16.9, chan51 1.1, chan53 15.0, chan54 16.6, chan55 13.8, chan56 12.0, chan57 4.3, chan58 2.7, chan61 4.9, chan62 4.8, chan63 3.6, chan64 7.0, chan73 43.7, chan74 42.3, chan75 45.0, chan76 45.5, chan113 47.6, chan114 47.4, chan115 47.5, chan116 47.5, chan117 47.4, chan118 48.2, chan119 47.3, chan120 47.6, chan121 47.2, chan122 47.0, chan123 46.9, chan124 46.7, chan125 47.0, chan126 47.1, chan127 47.1, chan128 47.1 | 0.28 | 41 | yes; yes |
| sub-C_task-pinchexecuted_run-4 | 328090 | 80 | ±32764 / ±8191 uV | 34: chan49 21.3, chan50 3.9, chan51 6.4, chan52 2.1, chan53 29.1, chan54 29.5, chan55 29.2, chan56 24.8, chan57 16.1, chan58 11.1, chan61 18.8, chan62 18.1, chan63 16.4, chan64 24.3, chan73 43.4, chan74 41.9, chan75 44.5, chan76 45.0, chan113 47.6, chan114 47.4, chan115 47.5, chan116 47.6, chan117 47.5, chan118 48.2, chan119 47.4, chan120 47.5, chan121 47.3, chan122 47.1, chan123 47.1, chan124 46.7, chan125 46.7, chan126 47.1, chan127 46.9, chan128 46.8 | 0.00 | 40 | yes; yes |
| sub-C_task-pinchexecuted_run-5 | 320650 | 80 | ±32764 / ±8191 uV | 32: chan49 20.0, chan51 4.0, chan53 24.7, chan54 24.6, chan55 24.7, chan56 20.5, chan57 11.8, chan58 8.5, chan61 12.6, chan62 12.3, chan63 8.6, chan64 17.8, chan73 43.4, chan74 40.9, chan75 44.6, chan76 45.1, chan113 47.6, chan114 47.3, chan115 47.4, chan116 47.5, chan117 47.4, chan118 48.0, chan119 47.2, chan120 47.5, chan121 47.3, chan122 47.0, chan123 47.0, chan124 46.6, chan125 46.7, chan126 47.1, chan127 46.9, chan128 46.8 | 0.74 | 41 | yes; yes |
| sub-C_task-powerexecuted_run-1 | 321125 | 80 | ±32764 / ±8191 uV | 33: chan49 20.3, chan50 1.7, chan51 1.3, chan53 23.6, chan54 24.0, chan55 23.7, chan56 18.7, chan57 7.7, chan58 4.1, chan61 9.1, chan62 8.5, chan63 6.2, chan64 14.8, chan73 44.1, chan74 36.5, chan75 45.7, chan76 45.7, chan113 47.6, chan114 47.5, chan115 47.5, chan116 47.5, chan117 47.5, chan118 47.7, chan119 47.4, chan120 47.5, chan121 47.0, chan122 46.8, chan123 46.9, chan124 46.3, chan125 46.8, chan126 46.8, chan127 46.7, chan128 46.6 | 0.91 | 41 | yes; yes |
| sub-C_task-powerexecuted_run-2 | 322146 | 80 | ±32764 / ±8191 uV | 34: chan49 20.1, chan50 3.0, chan51 5.3, chan52 1.0, chan53 27.7, chan54 27.7, chan55 27.9, chan56 23.4, chan57 14.8, chan58 9.7, chan61 17.0, chan62 16.7, chan63 14.4, chan64 22.4, chan73 43.9, chan74 33.6, chan75 45.7, chan76 45.7, chan113 47.7, chan114 47.5, chan115 47.5, chan116 47.5, chan117 47.5, chan118 47.9, chan119 47.4, chan120 47.5, chan121 47.1, chan122 46.9, chan123 46.9, chan124 46.4, chan125 46.8, chan126 46.9, chan127 46.7, chan128 46.5 | 0.23 | 40 | yes; yes |
| sub-C_task-powerexecuted_run-3 | 319066 | 80 | ±32764 / ±8191 uV | 35: chan49 29.0, chan50 25.0, chan51 26.1, chan52 22.2, chan53 32.6, chan54 32.6, chan55 32.4, chan56 31.7, chan57 30.1, chan58 27.4, chan60 1.1, chan61 30.9, chan62 30.3, chan63 30.9, chan64 31.2, chan73 43.2, chan74 40.8, chan75 44.1, chan76 44.2, chan113 47.7, chan114 47.6, chan115 47.4, chan116 47.7, chan117 47.5, chan118 47.6, chan119 47.5, chan120 47.4, chan121 46.7, chan122 46.1, chan123 46.4, chan124 45.9, chan125 46.6, chan126 46.4, chan127 46.3, chan128 45.8 | 0.90 | 41 | yes; yes |
| sub-D_task-pinchexecuted_run-1 | 323424 | 128 | ±32764 / ±8191 uV | 0: - | 0.00 | 0 | yes; yes |
| sub-D_task-pinchexecuted_run-2 | 322606 | 128 | ±32764 / ±8191 uV | 0: - | 0.00 | 0 | yes; yes |
| sub-D_task-pinchexecuted_run-3 | 323662 | 128 | ±32764 / ±8191 uV | 0: - | 0.00 | 0 | yes; yes |
| sub-D_task-pinchexecuted_run-4 | 322444 | 128 | ±32764 / ±8191 uV | 0: - | 0.00 | 0 | yes; yes |
| sub-D_task-powerexecuted_run-1 | 322064 | 128 | ±32764 / ±8191 uV | 0: - | 0.00 | 0 | yes; yes |
| sub-D_task-powerexecuted_run-2 | 322004 | 128 | ±32764 / ±8191 uV | 0: - | 0.00 | 0 | yes; yes |
| sub-D_task-powerexecuted_run-3 | 323284 | 128 | ±32764 / ±8191 uV | 0: - | 0.00 | 0 | yes; yes |
| sub-D_task-powerexecuted_run-4 | 360684 | 128 | ±32764 / ±8191 uV | 0: - | 0.00 | 0 | yes; yes |

46 recordings, 394 amplifier inputs with more than 1% of samples at abs count >= 32764; 99.8% of those inputs' samples at abs count >= 32764 are at -32768 or 32767.

**Coverage**: 46 of 46 recordings and 46 of 46 NSx files, all channels, all samples. The 394 flagged inputs and
percentages equal the 394 `bad` rows and `status_description` values in the 24 `channels.tsv` files changed by the PR;
no other row is `bad`. The NSx samples equal the BrainVision samples in all 46 recordings.

Reproduce: `python code/receipts/2026-10-22_rail-clipped-channels.py <nm000397 root, with the sourcedata NSx files>`
(Python 3.12.15, numpy 2.5.4; MNE not used).
