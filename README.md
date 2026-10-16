# gridPlay firmware releases

Signed pilot firmware for the Waveshare ESP32-S3 Touch AMOLED 2.16 tile.

## User manual

**[Read the gridPlay Tile User Manual →](USER-MANUAL.md)** — first setup, GPT Live, QR pairing, controls, battery status, Wi-Fi updates, and troubleshooting.

## Install

**[Install gridPlay in your browser →](https://casualware.github.io/gridPlay/)**

Connect a new Waveshare ESP32-S3 Touch AMOLED 2.16 using a USB data cable and open the installer in desktop Chrome or Edge. First-time installation erases all device settings. Then configure Wi-Fi and your API key on the tile. The first signed-update bootstrap requires USB. Configured tiles use **Settings → Device details → Updates**. Keep external power connected. The `ota-preview` release contains the current signed channel manifest; immutable application images live under `vVERSION` releases. Preview builds are for qualification, not production deployment.

## Publishing over SSH

Firmware is built and signed on the release workstation. Only the application image, signed manifest, metadata, checksum and **public** verification key enter this repository. Pushing a reviewed candidate to `main` starts GitHub Actions, which verifies the signature and hash, publishes an immutable preview release, verifies the hosted asset, and promotes the preview pointer. No private signing key or long-lived GitHub token is stored in Actions.

Do not change an existing version. Increase both firmware version and sequence for a new candidate. The workflow refuses to replace versioned release content or move the preview channel backward. Stable promotion is intentionally not enabled until interrupted-download and rollback qualification is complete.

`candidate/` is the SSH transport for the latest signed release bundle. It is retained in Git history; release publishing does not require source or device credentials. Never commit private keys, OpenAI keys, Wi-Fi credentials, or full-flash recovery backups.

## Operator commands

See [OTA-PROCESS.md](OTA-PROCESS.md) for signing, SSH publication, and recovery. Use `tools/ota/publish_ssh.py --repo casualware/gridPlay --release-dir PATH --push` from the firmware workspace after building a signed candidate. The signing key remains on that workstation.

## Browser installer

`site/` hosts the first-install page and a signed factory image. The Pages workflow verifies the offline signature, complete image hash, embedded app hash, blank NVS and flash map before deployment. Factory images are produced from build outputs, never device backups. The initial bootstrap is pinned to 0.9.2-preview; later OTA releases do not automatically replace it. Refresh it deliberately after hardware testing, using `tools/installer/package.py` in the firmware workspace. No device secrets enter this repository.
