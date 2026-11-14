# Transformers kernel-loader hardening

## Scope

The base revision pins `transformers==4.57.3` (the Jetson deployment pins
`4.57.6`). CVE-2026-4372 / GHSA-29pf-2h5f-8g72 / PYSEC-2026-2289 is fixed in
Transformers 5.3.0. The affected path can use a model configuration's internal
attention implementation to load a Hub kernel despite the caller's
`trust_remote_code=False` setting.

## Reachability in GR00T

`Qwen3Backbone` calls
`Qwen3VLForConditionalGeneration.from_pretrained(model_name, ...)` with a model
name and loading kwargs derived from the GR00T model configuration. The default
configuration requests `flash_attention_2`, which is an explicit caller choice,
but deployments can disable it and a checkpoint/configuration can still supply
the vulnerable internal field. The optional `kernels` package is not a GR00T
dependency, so the vulnerable path is conditional on that package being present
and on loading an attacker-controlled or tampered model configuration.

## Fix in this branch

Before any Qwen3-VL `from_pretrained` call, the loader now fails closed when
Transformers is older than 5.3.0 (or has an unparseable version) and the
optional `kernels` package is installed. The error names the CVE and the
required upgrade. Existing installations without `kernels` remain compatible
until their dependency lock can be refreshed.

The project pins and lock files are intentionally unchanged in this branch:
the aarch64 torchcodec wheel is an unresolved Git-LFS pointer in this checkout,
so an honest lock refresh cannot be completed here. The durable remediation is
to refresh every platform lock with `transformers>=5.3.0` and then remove this
compatibility guard after the minimum is enforced everywhere.

## Validation

`tests/gr00t/model/test_transformers_security.py` covers the vulnerable pair,
the fixed version, and the no-`kernels` compatibility case. The tests use a
small import seam and do not require Torch or a GPU.
