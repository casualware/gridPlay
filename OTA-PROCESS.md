# gridPlay signed OTA releases

Status: implementation and host tests in progress; deployment requires the public GitHub repository and a USB bootstrap. The existing tile remains on 0.8.5 until bootstrap is deliberately installed. Do not label the channel production-qualified until the hardware checklist below passes.

## Operator workflow

1. Choose a **public** GitHub repository dedicated to firmware releases. Devices receive no GitHub token. Keep source private separately if needed.
2. Create a dedicated signing key on the release workstation, outside tracked source:
   ```sh
   python3 tools/ota/release.py init-key --private .secrets/ota-signing-key.pem
   ```
   The key is RSA-3072, created with owner-only permissions. Back it up in your organization's secret store/offline recovery storage. Never attach it to a release or put it in source control. This local file is not a managed HSM or encrypted-at-rest key vault. Use an isolated signer for production operations. Lost keys require a USB trust bootstrap unless an old trusted firmware first installs a replacement public key.
3. Set the version and strictly increasing sequence in `firmware/GridPlay/FirmwareVersion.h`. Use preview versions until hardware qualification passes. The board/layout identifiers must reflect the actual hardware and partition map.
4. Build from a reviewed, frozen source snapshot:
   ```sh
   python3 tools/ota/release.py build --repo OWNER/REPO --private .secrets/ota-signing-key.pem --channel preview --out firmware/releases/0.9.0-preview --notes 'Signed Wi-Fi updates with startup health checks.'
   ```
   This configures the public verification key and channel URL, runs the pinned Arduino build, creates an immutable local release directory, signs the exact manifest payload, and verifies the image digest/signature. No upload occurs. Rebuilding a published version is prohibited: use a new version and sequence. Archive source revision/snapshot, build logs, test results and the release directory together.
5. USB-bootstrap the first signed-update-capable firmware onto pilot tiles. Existing 0.8.x firmware does not have this updater/trust anchor. This application update does not change partition layout or burn eFuses.
6. Create a draft release:
   ```sh
   python3 tools/ota/publish.py draft --repo OWNER/REPO --release-dir firmware/releases/0.9.0-preview
   ```
7. Complete the pilot checklist. Publish the qualified version draft through GitHub. Then explicitly promote its signed manifest:
   ```sh
   python3 tools/ota/publish.py promote --repo OWNER/REPO --release-dir firmware/releases/0.9.0-preview
   ```
   Promotion downloads and verifies the hosted firmware, then updates only `manifest.json` in the `ota-preview` release. Immutable version assets stay under `vVERSION`. Stable is a separate channel/trust configuration; preview firmware cannot be packaged as stable.
8. On a tile: **Settings → Device details → Updates → Check again → Install update**. Stop GPT Live first and keep external power connected. The updater never silently installs in the background.

## Trust and failure behavior

The envelope contains a base64 payload and RSA/SHA-256 signature. The tile verifies the exact decoded bytes with its compiled public key before accepting update metadata. The signed fields bind board, partition layout, channel, version, monotonic sequence, application size, SHA-256, immutable GitHub URL, release notes, issue time and expiry. Manifest validity is 90 days. Renew a stale channel with a new signed release/sequence; do not disable expiry checks.

HTTPS is certificate-verified for the manifest and firmware, including every redirect. HTTP redirects are rejected. Neither the signing key, OpenAI key, Wi-Fi password nor GitHub credentials are sent to the update host. The only firmware destination accepted is the configured repository's versioned release URL.

The client downloads into the inactive app partition. It checks signed size and SHA-256, validates the ESP image, and only then changes the boot partition. Interrupted downloads retain the current boot image. Both slots are 6 MiB. Release packaging rejects merged flash images, wrong chips and oversized applications. The device rejects older/equal sequences, wrong board/layout/channel, expired manifests and invalid signatures. Sequence protection is application/NVS-based, not hardware eFuse anti-rollback.

The ESP32 3.3.11 ESP32-S3 core enables bootloader rollback. Its default immediate acceptance is overridden. A pending image is confirmed after at least 15 seconds with display flushes, touch polling, the application loop and sufficient internal memory working. A 60-second independent timer restarts an unconfirmed image, allowing bootloader rollback. Wi-Fi or cloud outages are not grounds for rejecting an otherwise healthy boot. These checks do not prove acoustic quality, touch accuracy or every application feature; the pilot checklist does that.

Legacy ArduinoOTA network uploads are removed from this build so they cannot bypass signed releases. USB remains the recovery route. Secure Boot and flash encryption are not enabled; application-level signatures do not prevent a person with physical flash access from replacing the verifier. Moving to hardware-backed boot verification and key storage requires a separately qualified manufacturing/provisioning process. Do not burn security eFuses during ordinary releases.

## Release qualification (record evidence per version)

- Host tests: signed manifest/image succeeds; changed image, modified signed metadata, wrong repository/chip, stale sequence, expiry and wrong board/layout/channel fail.
- Firmware builds with the selected public key/channel; all existing bridge tests and native asset/manifest checks pass.
- Pilot boot shows the expected version, Wi-Fi/touch/display/audio and GPT Live work.
- Valid OTA downloads into the other slot, restarts, enters pending verification, then confirms healthy after 15 seconds.
- Interrupt Wi-Fi during transfer: current firmware remains bootable and retry succeeds.
- Remove power during download/write: current firmware boots. Perform only on a USB-recoverable pilot device.
- A deliberately unconfirmed test image reboots and rolls back; verify both version and selected partition. Never promote that test image to a real channel.
- A corrupted download and a manifest signed by an untrusted key are rejected before boot selection.
- Verify settings, Wi-Fi credentials, API-key policy, last inst and scene survive upgrade/rollback. New settings migrations must be backward-compatible while the previous slot remains a rollback candidate.
- Promote preview to a small pilot cohort before building a stable release. No automatic fleet rollout, telemetry collection, or unattended key rotation is implemented here.

## Recovery

Keep a known-good application plus its matching bootloader/partition bundle offline. A normal OTA failure must not require erasing NVS. If the UI cannot boot and automatic rollback does not recover it, use USB to install the known-good bundle; do not erase all flash or restore another tile's NVS. For a bad release already confirmed healthy, publish a corrected build with a **higher sequence**; do not lower the channel sequence. Record rollback results and keep the faulty version out of active channels.

References: https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/system/ota.html and the pinned Arduino core's `verifyRollbackLater()` hook.
