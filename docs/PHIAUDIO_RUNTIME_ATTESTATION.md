# PHIAudio Runtime Tree Attestation

WaveForgeStudio now distinguishes three provenance layers for its qualified PHIAudio runtime:

1. **Git commit identity**
2. **Git source-tree identity**
3. **Built runtime manifest identity**

## Locked source identity

The runtime lock v0.2 binds both:

- commit `2c4855ba9bf7687428347733f4ae435bbee5a934`
- Git tree `c08ac250f65a6ce0e76d989eba138386e382fde1`

The tree SHA prevents a qualification record from quietly treating a different source snapshot as equivalent merely because someone copied the commit string into metadata.

## Attestation

After PHIAudio builds, WaveForge creates:

`phiaudio-runtime-attestation.json`

It records:

- runtime-lock SHA-256,
- actual checkout commit and Git tree,
- package name/version,
- package.json SHA-256,
- tsconfig SHA-256,
- canonical source-file manifest SHA-256,
- canonical built-`dist/` manifest SHA-256,
- source and dist file counts,
- dependency-lock presence/hash,
- attestation SHA-256.

## Dependency warning

The qualified PHIAudio revision currently has no committed `package-lock.json` or `npm-shrinkwrap.json`.

The attestation therefore records:

`no_committed_dependency_lock`

rather than pretending the npm dependency graph is fully reproducible.

That limitation matters. The Git tree and built runtime are now measured precisely, but supply-chain reproducibility is not complete until dependency resolution is pinned as well.

## Upgrade path

A later PHIAudio release should commit a dependency lock or equivalent reproducible dependency manifest. Once that exists, this attestation will bind it automatically.
