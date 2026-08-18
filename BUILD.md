# Building & Signing the Windows Executable

This produces a `.exe` for people who don't have Python installed, and
covers why AV/SmartScreen flag unsigned exes and what actually fixes it.

## Why unsigned exes get flagged (and what actually helps)

Windows Defender SmartScreen and most AV engines don't scan your code for
malicious logic first — they check **reputation**: is this file signed by
a known publisher, and has it been seen before by enough users? A brand
new, unsigned exe built with PyInstaller has *zero* reputation and *zero*
signature, which is exactly the profile of most malware droppers, so it
gets flagged heuristically even when the code is 100% benign. Three things
move the needle, in order of impact:

1. **Code-sign the exe with a certificate from a trusted CA.** This is the
   only fix that actually removes the "Unknown Publisher" warning. There
   is no way to sign it yourself and have Windows trust it — the
   certificate has to be issued by a Certificate Authority (DigiCert,
   Sectigo, SSL.com, GlobalSign, etc.) after they verify your identity or
   company. I can't generate or provide one; you'll need to purchase and
   go through their verification process. Expect:
   - **OV (Organization Validation) certificate**: cheaper, ~1-5 days
     verification. Still shows SmartScreen warnings until the certificate
     builds up enough download reputation with Microsoft (can take weeks).
   - **EV (Extended Validation) certificate**: pricier, stricter
     verification (often requires a registered business + a hardware
     token or cloud HSM). Gets **instant** SmartScreen reputation —
     no warning from day one. If you're distributing this beyond your own
     team, EV is the one that actually solves the "so it doesn't trigger"
     problem immediately.
2. **Packaging choices** (already applied in `build.spec`): `--onedir`
   instead of `--onefile` (no self-extracting temp-folder behaviour), UPX
   compression disabled (UPX-packed binaries are a well-known heuristic
   trigger), and real version metadata embedded via `version_info.txt`
   instead of a blank/generic exe.
3. **Submit to Microsoft for analysis** once signed, if a false positive
   still shows up from a specific vendor:
   https://www.microsoft.com/en-us/wdsi/filesubmission

None of this is a workaround for a genuinely malicious file — it's
standard practice for any legitimate small ISV shipping a Windows exe.

## 1. Build the exe

On a **Windows** machine (PyInstaller builds a Windows exe only when run
on Windows):

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-build.txt

pyinstaller build.spec
```

Output: `dist\SQLAlterTool\SQLAlterTool.exe` (plus its supporting files
in the same folder — zip the whole `SQLAlterTool` folder when you
distribute it, not just the exe).

If you don't have an icon yet, either drop a `.ico` file at
`assets/app_icon.ico` or delete the `icon=...` line in `build.spec`.

## 2. Get a code-signing certificate

Buy one from a CA (DigiCert, Sectigo, SSL.com are common choices). You'll
receive either:
- a `.pfx`/`.p12` file (software-based cert), or
- a hardware USB token / cloud HSM (required by most CAs for EV certs
  since 2023).

**Never commit the `.pfx`/private key to the repo** — `.gitignore`
already excludes these.

## 3. Sign the exe

Using Windows SDK's `signtool` (installed with Visual Studio or the
standalone Windows SDK):

```powershell
signtool sign ^
  /f "path\to\your_certificate.pfx" ^
  /p "your_certificate_password" ^
  /tr http://timestamp.digicert.com ^
  /td sha256 ^
  /fd sha256 ^
  dist\SQLAlterTool\SQLAlterTool.exe
```

- `/tr` + `/td` add a **timestamp** — this keeps the signature valid even
  after the certificate itself expires. Always include it.
- If your cert is on a hardware token/HSM, drop `/f` and `/p` and instead
  reference the certificate by thumbprint (`/sha1 <thumbprint>`) — the
  token's own driver/PIN prompt handles the private key.

Verify it worked:

```powershell
signtool verify /pa dist\SQLAlterTool\SQLAlterTool.exe
```

## 4. (Optional) Automate it in CI

`.github/workflows/build.yml` in this repo builds the exe on every tag
push. To also sign it in CI, store the `.pfx` (base64-encoded) and its
password as GitHub Actions **encrypted secrets**, decode it in a step,
run `signtool`, then delete the decoded file before the job ends. Ask me
if you want that step written out — it's a few extra lines but security-
sensitive enough that I'd rather set it up explicitly with you than have
you copy-paste blind.