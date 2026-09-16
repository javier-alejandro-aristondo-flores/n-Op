"""the four card drivers this member's card queue needs, each named and importable but firing only by explicit call"""

import argparse
import json
import subprocess
import threading
import time

from operators.codomain_attention.masking import MaskPatternName, NAMED_MASK_PATTERNS
from operators.codomain_attention.report import (
    CARD_USABLE_MEMORY_GIGABYTES,
    Fresh_Completion_Member,
    Latest_Stage_Checkpoint,
    Load_Trained_Completion_Member,
    Loaded_Training_Population,
    PRETRAIN_HOUR_CAP,
    PRETRAIN_SEED,
    STEP_COST_PROBE_STEPS,
    Step_Cost_Probe,
    Train_Completion_Member,
    TRAINING_ARTIFACT_PATH,
)
from operators.codomain_attention.loader import CompletionBatches
from operators.codomain_attention.splits import CompletionBlock

# the pretrain's own fixed run name, so the fine-tune and k3 drivers know which checkpoint to resume from
PRETRAIN_RUN_NAME = "completion_fold0_pretrain_20260916"

PROBE_RESULT_PATH = TRAINING_ARTIFACT_PATH / "probe_result.json"

FINE_TUNE_HOUR_CAP = 1.0
K3_HOUR_CAP = 4.0
K3_LOW_DATA_RUN_NAME = "completion_fold0_k3_pretrained_lowdata_20260916"
K3_DEDICATED_RUN_NAME = "completion_fold0_k3_dedicated_lowdata_20260916"

MEBIBYTES_PER_GIGABYTE = 1024.0
MEMORY_POLL_INTERVAL_SECONDS = 0.5


def Peak_Accelerator_Memory_Mebibytes(stop: threading.Event, peak: list[float]) -> None:
    """the largest accelerator memory reading nvidia-smi reports while a driver trains, polled on its own thread"""
    while not stop.is_set():
        try:
            output = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5,
                check=True,
            )
            reading = float(output.stdout.strip().splitlines()[0])
            peak[0] = max(peak[0], reading)
        except (subprocess.SubprocessError, ValueError, OSError):
            pass
        stop.wait(MEMORY_POLL_INTERVAL_SECONDS)


def Run_Probe() -> dict[str, object]:
    """the pre-registered 300-step cost probe, seconds per step beside the accelerator's own measured peak memory"""
    block = CompletionBlock()
    training_examples, validation_examples, statistics = Loaded_Training_Population(block)
    batches = CompletionBatches(training_examples, validation_examples, statistics)
    member = Fresh_Completion_Member(statistics, seed=PRETRAIN_SEED)

    peak_mebibytes = [0.0]
    stop = threading.Event()
    watcher = threading.Thread(target=Peak_Accelerator_Memory_Mebibytes, args=(stop, peak_mebibytes), daemon=True)
    watcher.start()
    probe = Step_Cost_Probe(member, batches, step_count=STEP_COST_PROBE_STEPS)
    stop.set()
    watcher.join(timeout=5.0)

    peak_gigabytes = peak_mebibytes[0] / MEBIBYTES_PER_GIGABYTE
    result: dict[str, object] = dict(probe)
    result["peak_accelerator_memory_mebibytes"] = peak_mebibytes[0]
    result["peak_accelerator_memory_gigabytes"] = peak_gigabytes
    result["ceiling_gigabytes"] = CARD_USABLE_MEMORY_GIGABYTES
    result["within_ceiling"] = peak_gigabytes <= CARD_USABLE_MEMORY_GIGABYTES
    TRAINING_ARTIFACT_PATH.mkdir(parents=True, exist_ok=True)
    PROBE_RESULT_PATH.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    return result


def Pretrain_Step_Count(hour_cap: float) -> int:
    """the step budget an hour cap allows, from the probe's own measured seconds per step"""
    if not PROBE_RESULT_PATH.is_file():
        raise FileNotFoundError(f"no probe result at {PROBE_RESULT_PATH} -- run the probe driver first")
    seconds_per_step = json.loads(PROBE_RESULT_PATH.read_text())["seconds_per_step"]
    return max(1, int(hour_cap * 3600.0 / seconds_per_step))


def Manifest_Summary(manifest: dict[str, object]) -> dict[str, object]:
    """the json-safe slice of a training manifest, every stage's own dict kept, the live member and parameters dropped"""
    return {name: value for name, value in manifest.items() if name not in ("member", "final_parameters")}


def Run_Pretrain() -> dict[str, object]:
    """the staged six-hour pretrain over every mask pattern, checkpointed under this member's own training path"""
    step_count = Pretrain_Step_Count(PRETRAIN_HOUR_CAP)
    manifest = Train_Completion_Member(
        step_count, PRETRAIN_RUN_NAME, restrict_to_pattern=None, seed=PRETRAIN_SEED, hour_cap=PRETRAIN_HOUR_CAP
    )
    summary = Manifest_Summary(manifest)
    (TRAINING_ARTIFACT_PATH / f"{PRETRAIN_RUN_NAME}_summary.json").write_text(
        json.dumps(summary, indent=1, sort_keys=True, default=str) + "\n"
    )
    return manifest


def Run_Fine_Tune(pattern: MaskPatternName, hour_cap: float = FINE_TUNE_HOUR_CAP) -> dict[str, object]:
    """a k1 fine-tune restricted to one pairwise pattern, starting from the pretrain's own best checkpoint"""
    block = CompletionBlock()
    _, _, statistics = Loaded_Training_Population(block)
    checkpoint_path = Latest_Stage_Checkpoint(TRAINING_ARTIFACT_PATH, PRETRAIN_RUN_NAME)
    _, progress = Load_Trained_Completion_Member(checkpoint_path, statistics, seed=PRETRAIN_SEED)
    step_count = Pretrain_Step_Count(hour_cap)
    run_name = f"completion_fold0_finetune_{pattern}_20260916"
    manifest = Train_Completion_Member(
        step_count,
        run_name,
        restrict_to_pattern=pattern,
        seed=PRETRAIN_SEED,
        hour_cap=hour_cap,
        starting_parameters=progress.best_parameters,
    )
    summary = Manifest_Summary(manifest)
    (TRAINING_ARTIFACT_PATH / f"{run_name}_summary.json").write_text(
        json.dumps(summary, indent=1, sort_keys=True, default=str) + "\n"
    )
    return manifest


def Run_K3_Comparison(hour_cap: float = K3_HOUR_CAP) -> dict[str, dict[str, object]]:
    """the pretraining-advantage test: the pretrained member continued on the low-data slice against a dedicated model trained only on it, matched total steps"""
    block = CompletionBlock()
    low_data_identifiers = block.Low_Data_Defect_Identifiers()
    _, _, pretrain_statistics = Loaded_Training_Population(block)
    checkpoint_path = Latest_Stage_Checkpoint(TRAINING_ARTIFACT_PATH, PRETRAIN_RUN_NAME)
    _, progress = Load_Trained_Completion_Member(checkpoint_path, pretrain_statistics, seed=PRETRAIN_SEED)

    half_hour_cap = hour_cap / 2.0
    step_count = Pretrain_Step_Count(half_hour_cap)

    pretrained_manifest = Train_Completion_Member(
        step_count,
        K3_LOW_DATA_RUN_NAME,
        restrict_to_pattern=None,
        seed=PRETRAIN_SEED,
        hour_cap=half_hour_cap,
        starting_parameters=progress.best_parameters,
        training_identifiers=low_data_identifiers,
        statistics_override=pretrain_statistics,
    )
    dedicated_manifest = Train_Completion_Member(
        step_count,
        K3_DEDICATED_RUN_NAME,
        restrict_to_pattern=None,
        seed=PRETRAIN_SEED,
        hour_cap=half_hour_cap,
        training_identifiers=low_data_identifiers,
    )
    combined = {"pretrained_continued": pretrained_manifest, "dedicated_from_scratch": dedicated_manifest}
    summary = {name: Manifest_Summary(manifest) for name, manifest in combined.items()}
    (TRAINING_ARTIFACT_PATH / "completion_fold0_k3_comparison_summary.json").write_text(
        json.dumps(summary, indent=1, sort_keys=True, default=str) + "\n"
    )
    return combined


def Parsed_Arguments(argv: list[str] | None = None) -> argparse.Namespace:
    """the one subcommand this launch means to run, named rather than inferred"""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="driver", required=True)
    subparsers.add_parser("probe")
    subparsers.add_parser("pretrain")
    fine_tune_parser = subparsers.add_parser("fine-tune")
    fine_tune_parser.add_argument("pattern", choices=NAMED_MASK_PATTERNS)
    subparsers.add_parser("k3")
    return parser.parse_args(argv)


def Main(argv: list[str] | None = None) -> int:
    """the launch point this stream never calls itself -- every run here waits for the integrator's own word"""
    arguments = Parsed_Arguments(argv)
    started = time.time()
    if arguments.driver == "probe":
        Run_Probe()
    elif arguments.driver == "pretrain":
        Run_Pretrain()
    elif arguments.driver == "fine-tune":
        Run_Fine_Tune(arguments.pattern)
    else:
        Run_K3_Comparison()
    print(f"{arguments.driver} finished in {time.time() - started:.1f} seconds")
    return 0


if __name__ == "__main__":
    raise SystemExit(Main())
