# oura-dashboard

A personal, subscription-free dashboard for your **own** Oura Ring (3/4/5), built on top of
[open_oura](https://github.com/Th0rgal/open_oura) — a reverse-engineered Bluetooth client that
pairs directly with the ring and pulls its raw sensor history into a local SQLite database.

open_oura ships as a Rust CLI with no UI and no export — just `oura` commands and raw SQL tables.
This repo adds the missing piece: a local web dashboard and a CSV/JSON export tool that read that
SQLite database.

This is **not** affiliated with Oura, and it can't reproduce Oura's cloud-computed scores
(Readiness, Sleep, Activity, Stress) — those algorithms are proprietary and never reverse-engineered.
What you do get locally: live/latest heart rate, SpO2, battery, on-device sleep stages, and activity
METs.

## Easiest path: NOOP app (beta)

If you just want to see your readings on your phone, try [NOOP](https://github.com/NoopApp/noop)
first. It's a free, ready-made app. Since
[v7.5.0](https://github.com/NoopApp/noop/releases/tag/v7.5.0) it reads Oura Ring 3/4/5 directly over
Bluetooth, with no Oura app, account, or cloud. It shows heart rate, R-R/HRV, SpO2, skin
temperature, and sleep stages, plus its own Charge/Effort/Rest scores. Those are NOOP's own scores,
not copies of Oura's Readiness or Sleep scores.

Download it from the **Assets** section of the
[latest release](https://github.com/NoopApp/noop/releases):

- **macOS**: universal zip (Intel + Apple Silicon)
- **iPhone**: unsigned `.ipa`. Install it with [AltStore](https://altstore.io) or
  [SideStore](https://sidestore.io).
- **Android**: `.apk` (allow installs from unknown sources)

Setup options inside the app:

- **Factory-reset + adopt**: the easiest option. It wipes the ring's pairing with the Oura app. It's
  recoverable, because re-pairing in the Oura app brings the ring back.
- **Bring-your-own-key**: doesn't reset anything. Use a key you extracted yourself (see below).
- **File import**

### Mac quickstart

1. **Check your macOS version.** Go to Apple menu → About This Mac. NOOP needs macOS 13 (Ventura)
   or newer.
2. **Download.** Open the newest [release](https://github.com/NoopApp/noop/releases), scroll to
   **Assets**, and download the macOS universal `.zip`. Unzip it and drag **NOOP** into
   **Applications**. NOOP's own README also documents a Homebrew install.
3. **First launch.** The app is unsigned, so right-click NOOP → **Open** → **Open**. If macOS still
   blocks it, go to System Settings → **Privacy & Security** → **Open Anyway**. When the app asks for
   Bluetooth access, click **Allow**.
4. **Prepare the ring.** Charge it and keep it next to the Mac. Quit the Oura app on your phone, or
   turn the phone's Bluetooth off for a minute, so the phone doesn't grab the ring.
5. **Add the ring.** In NOOP, add a device → **Oura** → **factory-reset + adopt**. If it fails,
   re-pair the ring in the Oura app. Nothing gets bricked.
6. **Use it.** The ring syncs whenever it's in Bluetooth range of the Mac, so keep the Mac nearby
   (at your desk, or by the bed overnight). You'll see HR, HRV, SpO2, skin temperature, sleep
   stages, and NOOP's Charge/Effort/Rest scores. With only a Mac, there's no phone view.

> ⚠️ NOOP's Oura support is **early beta and not yet verified on real hardware**, so it may not
> work on every ring or firmware. If it doesn't work for your ring, or if you want raw data with
> CSV/JSON export, use the open_oura + dashboard path below.

---

> Everything below runs on **your own computer**, not in this repo's CI/cloud session. Talking to
> your ring over Bluetooth requires being physically near it.

## 1. Build open_oura and pair your ring

On a Bluetooth-capable Linux, macOS, or Windows machine. On macOS, first enable your terminal app
under System Settings → Privacy & Security → **Bluetooth** (Terminal or iTerm), or `oura` won't find
the ring.

```bash
git clone https://github.com/Th0rgal/open_oura
cd open_oura
cargo build --release
./target/release/oura scan          # confirm your ring shows up
```

### Get your ring's auth key (one-time, manual)

The ring authenticates every BLE connection with a 16-byte key. There are two ways to get one.

**Option A (easiest): factory-reset and self-pair.** Factory-reset the ring, then run:

```bash
./target/release/oura pair --key-file key.hex
```

open_oura generates a fresh random key, installs it on the ring, and saves it to `key.hex`. The
tradeoff: the official Oura app loses its pairing. To go back, re-pair the ring in the Oura app. That
gives the ring a new key, so you'd need Option B afterwards to keep using open_oura.

**Option B (non-destructive): recover the key the Oura app already set.** Do this once from your
own phone:

- **Android:** pull the Oura app's local Realm database (e.g. via `adb backup` on a debuggable
  device, or any Android app-data backup tool) and open it in [Realm
  Studio](https://github.com/realm/realm-studio). Look for `DbRingConfiguration.auth_key`.
- **iOS:** create a local, unencrypted Finder/iTunes backup of your phone, extract the Oura app's
  container from it, and locate the same Realm file inside.

Save the key as hex in a `key.hex` file next to the `oura` binary. **Never commit this file** —
it's your ring's permanent credential.

```bash
./target/release/oura --key-file key.hex info     # should print firmware, serial, battery
./target/release/oura --key-file key.hex sync --db oura.db
```

Re-run `sync` any time to pull new history into `oura.db`.

## 2. Run the dashboard (this repo)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
OURA_DB_PATH=/path/to/oura.db .venv/bin/python -m oura_dashboard.app
```

Open `http://localhost:5000` in a browser. To check it from your phone, open
`http://<this-machine's-LAN-IP>:5000` while on the same WiFi network. For access away from home
WiFi, install [Tailscale](https://tailscale.com) on the host machine and your phone instead of
exposing a public port.

## 3. Export readings to CSV/JSON

```bash
.venv/bin/python -m oura_dashboard.export --db oura.db --format csv --out readings.csv
.venv/bin/python -m oura_dashboard.export --db oura.db --format json --out readings.json --kind hr --since 1700000000
```

## Try it without a ring

A synthetic database generator and test suite let you try the dashboard/export tools without any
hardware:

```bash
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m oura_dashboard.sample_data --db sample_oura.db --hours 72
OURA_DB_PATH=sample_oura.db .venv/bin/python -m oura_dashboard.app
```

Run the test suite with `.venv/bin/python -m pytest tests/ -v` (also installs `pytest`).

## Security note

`oura.db` and `key.hex` contain personal biometric data and your ring's permanent auth secret.
Both are already covered by `.gitignore` — don't commit or share them.
