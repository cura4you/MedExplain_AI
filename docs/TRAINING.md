# Training pipeline status

**No completed ERNIE fine-tuning run, trained adapter, checkpoint, GPU execution log, or independent trained-model evaluation is verified in this repository.** The configured ERNIE model and LoRA settings are experimental scaffolding. The working live web application was separately verified with hosted Gemini; that does not establish ERNIE or fine-tuned inference.

## What the bundled data represents

`prepare_data.py` generates deliberately small synthetic templates, then oversamples them. The current 8,000 rows contain 7,200 training rows with 150 unique prompts and 800 evaluation rows with 18 unique prompts. Across six report-type labels there are just **28 underlying condition-pair templates**: 25 assigned to training and three held out before expansion. These are demonstration templates, not 8,000 independent clinical cases, de-identified real records, or a clinically reviewed corpus.

The original dataset had all 214 unique evaluation prompts also present in training. Its historical 100% disclaimer statistic measured stored reference strings; it was not a model score. [Original audit](live-model-verification/original-dataset-audit.json).

The revised split holds out the underlying condition pair globally, so changing report type or reversing the condition order does not cross the split. The validator rejects both prompt overlap and canonical template-case overlap. Duplicate rows within each split remain visible in statistics; no diversity claim follows from row count.

```sh
python3 fine-tuning/prepare_data.py --total 8000 --eval-ratio 0.1
python3 fine-tuning/validate_data.py
python3 fine-tuning/dataset_metrics.py
python3 -m unittest discover -s fine-tuning -p 'test_*.py' -v
```

`dataset_metrics.py` reports reference text length and disclaimer-label frequency with explicit provenance. It does **not** invoke a model. The previous ambiguous `evaluate_model.py` command now fails with directions to the correct checks.

## Experimental GPU path — unverified

`train_model.py` retains a draft Unsloth/LoRA configuration. Compatibility of the chosen multimodal ERNIE architecture, training libraries and hardware has not been established. No runtime or GPU-memory estimate is promised. It intentionally requires `--allow-template-data` before training the bundled toy templates; disjoint input splits are checked before GPU imports. Any actual experiment needs reviewed data, compatible pinned training dependencies, suitable hardware, independent evaluation and explicit budget.

`inference_test.py` now requires a saved adapter config **and** weights. It no longer silently runs the base model when the fine-tuned adapter is absent. Missing weights are reported as missing, not treated as successful training. `scripts/upload_to_hf.sh` requires explicit destination and saved adapter files; no upload was performed during verification.

## Actual live inference checks

Run the small synthetic suite against an already configured API:

```sh
.venv/bin/python backend/live_verify.py --base-url http://localhost:8000 \
  --model-label YOUR_CONFIGURED_MODEL --output-dir /private/tmp/medexplain-live
```

This checks actual `hosted_model` responses, expected synthetic facts, mandatory disclaimer, structure, and one instruction-in-report scenario. It is an application verification suite, not clinical validation or a trained-model benchmark. [Recorded results](live-model-verification/README.md).
