import os
import sys
import json
import glob
import traceback
import torch
from celery import Celery

from app.core.config import settings

# 1. Setup path to moonbeam-studio to support importing engine and shared libraries
current_dir = os.path.dirname(os.path.abspath(__file__))
# Check candidate directories relative to this file
candidates = [
    os.path.abspath(os.path.join(current_dir, "..", "..", "..", "..", "moonbeam-studio")),
    os.path.abspath(os.path.join(current_dir, "..", "..", "..", "moonbeam-studio")),
    os.path.abspath(os.path.join(os.getcwd(), "moonbeam-studio")),
    os.path.abspath(os.path.join(os.getcwd(), "..", "moonbeam-studio")),
]
studio_dir = None
for candidate in candidates:
    if os.path.isdir(candidate):
        studio_dir = candidate
        break

if studio_dir:
    sys.path.append(studio_dir)
else:
    print(f"⚠️ Warning: Could not locate moonbeam-studio directory. Looked in: {candidates}")

# Ensure `moonbeam-codebase` (which contains the top-level `recipes` package)
# is on the import path so modules like `recipes.inference...` can be imported.
codebase_candidates = [
    os.path.abspath(os.path.join(current_dir, "..", "..", "..", "..", "moonbeam-codebase")),
    os.path.abspath(os.path.join(current_dir, "..", "..", "..", "moonbeam-codebase")),
    os.path.abspath(os.path.join(os.getcwd(), "moonbeam-codebase")),
    os.path.abspath(os.path.join(os.getcwd(), "..", "moonbeam-codebase")),
]
codebase_dir = None
for candidate in codebase_candidates:
    if os.path.isdir(candidate):
        codebase_dir = candidate
        break

if codebase_dir:
    if codebase_dir not in sys.path:
        sys.path.append(codebase_dir)
else:
    print(f"⚠️ Warning: Could not locate moonbeam-codebase directory. Looked in: {codebase_candidates}")

# 2. Initialize Celery App
celery_app = Celery("composer_tasks", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_time_limit = settings.celery_task_time_limit
celery_app.conf.task_soft_time_limit = settings.celery_task_soft_time_limit

# Global engines loaded once per worker process
harmony_router = None
composer = None


def _resolve_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


def _update_task_state(update_state, state: str, progress: str) -> None:
    if update_state is not None:
        update_state(state=state, meta={"progress": progress})


def run_generation(task_id: str, prompt: str, use_mock_llm: bool, update_state=None):
    global harmony_router, composer

    try:
        if harmony_router is None:
            _update_task_state(update_state, "LOADING_MODELS", "Booting 839M Model & Rust TIES Core into VRAM...")

            paths = _autodiscover_checkpoints()
            from engine.HarmonyRouter import HarmonyRouter
            from engine.agentic_composer import AgenticComposer

            harmony_router = HarmonyRouter(
                base_model_path=paths["BASE_MODEL_PATH"],
                lora_checkpoint_dir=paths["LORA_DIR"],
                model_config_path=paths["CONFIG_PATH"],
                master_dict_path=paths["MASTER_DICT_PATH"],
                device=_resolve_device(),
            )
            composer = AgenticComposer(harmonyrouter=harmony_router, acceptance_threshold=0.75)
            os.makedirs(settings.composer_output_dir, exist_ok=True)

        _update_task_state(update_state, "PLANNING", "Brain is analyzing prompt & planning structure...")
        composer.llm.use_mock = use_mock_llm

        llm_intent = composer.llm.generate_intent(prompt)
        blueprint = composer.planner.plan(llm_intent)

        blueprint_path = os.path.join(settings.composer_output_dir, f"{task_id}_blueprint.json")
        with open(blueprint_path, "w") as f:
            json.dump({"llm_intent": llm_intent, "dense_blueprint": blueprint}, f, indent=2)

        _update_task_state(update_state, "COMPOSING", "Generating sections, running Critic & FAISS memory...")
        final_song_midi = composer.compose_full_song(blueprint["timeline"])

        midi_path = os.path.join(settings.composer_output_dir, f"{task_id}.mid")
        final_song_midi.write(midi_path)

        return {
            "status": "completed",
            "midi_path": midi_path,
            "blueprint_path": blueprint_path,
            "message": "Masterpiece rendered.",
        }

    except Exception as e:
        traceback.print_exc()
        if update_state is not None:
            update_state(state="FAILURE", meta={"error": str(e)})
        raise


def _autodiscover_checkpoints():
    """
    Search for model weights and configuration files.
    Order of preference:
      1. Explicit env vars (BASE_MODEL_PATH, LORA_DIR, CONFIG_PATH, MASTER_DICT_PATH)
      2. Kaggle inputs / outputs recursive search
      3. Hardcoded Kaggle fallback paths
    """
    search_roots = ["/kaggle/input", "/kaggle/working"]
    targets = {
        "BASE_MODEL_PATH": "moonbeam_839M.pt",
        "LORA_DIR": "multi_task_lora",
        "CONFIG_PATH": "model_config_multi_task.json",
        "MASTER_DICT_PATH": "indexed_tokens_dict.json",
    }
    
    resolved = {}
    for env_key, filename in targets.items():
        # 1. Explicit env var wins
        if os.environ.get(env_key):
            resolved[env_key] = os.environ[env_key]
            continue
            
        found = None
        # 2. Search Kaggle directories recursively
        for root in search_roots:
            if os.path.isdir(root):
                matches = glob.glob(os.path.join(root, "**", filename), recursive=True)
                if matches:
                    found = matches[0]
                    break
                    
        if found:
            resolved[env_key] = found
        else:
            # 3. Fallback to default hardcoded paths
            fallback_map = {
                "BASE_MODEL_PATH": "/home/aashishbishow/ProjectX/Moonbeam Pretrained Weights/moonbeam_839M.pt",
                "LORA_DIR": "/home/aashishbishow/ProjectX/moonbeam_chunk_20260716_140713",
                "CONFIG_PATH": "/home/aashishbishow/ProjectX/moonbeam-codebase/src/llama_recipes/configs/model_config_multi_task.json",
                "MASTER_DICT_PATH": "/home/aashishbishow/ProjectX/Moonbeam Multi-Task Data/ComMU/indexed_tokens_dict.json"
            }
            resolved[env_key] = fallback_map[env_key]
            
    return resolved


@celery_app.task(bind=True, name="tasks.generate_song")
def generate_song_task(self, task_id: str, prompt: str, use_mock_llm: bool):
    try:
        return run_generation(task_id, prompt, use_mock_llm, update_state=self.update_state)
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
