# Trainer RNG checkpoint hardening

## Reachability

GR00T's training entrypoint calls `Gr00tTrainer.train()` with
`resume_from_checkpoint` from the training config. The custom trainer delegates
to Hugging Face `Trainer.train()`. In the pinned Transformers 4.57.x line,
`Trainer._load_rng_state()` reads `rng_state*.pth` with unrestricted
`torch.load()`. A writer who can place a checkpoint under the configured output
directory can therefore execute pickle payloads when an operator resumes.

This is a conditional supply-chain/local High RCE, not an unauthenticated
inference-server issue: the attacker needs write access to the training
checkpoint location or a tampered artifact and the operator must resume it.

## Fix in this branch

`Gr00tTrainer._load_rng_state()` now uses `torch.load(..., weights_only=True)`
with the narrow NumPy allowlist used by Transformers 5.0+, restores Python,
NumPy, CPU, and CUDA RNG state, and fails closed on incompatible or malformed
checkpoint data. It never falls back to unrestricted pickle loading.

The durable dependency remediation remains upgrading Transformers to a release
that contains the upstream safe loader (`>=5.0.0`, and `>=5.3.0` for the
separate kernel-loader advisory). No PR is created by this branch.

## Other pip-audit findings

- `custom_generate` code-loading advisories are not reachable from GR00T's
  current model-loading calls; no `custom_generate` argument or repository is
  supplied by the project.
- LightGlue is not imported or configured by GR00T.
- `save_pretrained` path-traversal/file-write advisories apply to Transformers
  library internals; GR00T passes operator-controlled local output directories
  and does not expose those paths to network requests.
