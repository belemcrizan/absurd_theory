# Empirical noise adapters

The simulator uses normalized units and synthetic noise by default. It can also
resample a numeric column from a local CSV:

```bash
absurd-theory --noise-csv path/to/noise.csv --noise-column strain
```

Good public sources for adversarial background traces include:

- **GWOSC** — calibrated LIGO/Virgo/KAGRA strain time series and data-quality
  flags: <https://gwosc.org/tutorials/>
- **Gravity Spy** — classified transient detector glitches and metadata:
  <https://zenodo.org/records/5649212>
- **ATLAS Open Data** — collision and simulated events, useful for future
  missing-momentum validation: <https://atlas.cern/Resources/Opendata>
- **XENON public data** — low-background rare-event data and analysis releases:
  <https://xenonexperiment.org/public-data/>

These datasets are **background and methodology references**, not evidence for
WIOS. Their role is to make the null model harder to beat. Large third-party
datasets are intentionally not vendored into this repository.
