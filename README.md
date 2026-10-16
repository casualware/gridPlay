# gridPlay firmware releases

Signed pilot firmware for the Waveshare ESP32-S3 Touch AMOLED 2.16 tile.

## Install

The first signed-update bootstrap requires USB. Configured tiles use **Settings → Device details → Updates**. Keep external power connected. The `ota-preview` release contains the current signed channel manifest; immutable application images live under `vVERSION` releases. Preview builds are for qualification, not production deployment.

## Publishing over SSH

Firmware is built and signed on the release workstation. Only the application image, signed manifest, metadata, checksum and **public** verification key enter this repository. Pushing a reviewed candidate to `main` starts GitHub Actions, which verifies the signature and hash, publishes an immutable preview release, verifies the hosted asset, and promotes the preview pointer. No private signing key or long-lived GitHub token is stored in Actions.

Do not change an existing version. Increase both firmware version and sequence for a new candidate. The workflow refuses to replace versioned release content or move the preview channel backward. Stable promotion is intentionally not enabled until interrupted-download and rollback qualification is complete.

`candidate/` is the SSH transport for the latest signed release bundle. It is retained in Git history; release publishing does not require source or device credentials. Never commit private keys, OpenAI keys, Wi-Fi credentials, or full-flash recovery backups.
