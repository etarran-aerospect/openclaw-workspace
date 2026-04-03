"""
Minimal local TurboQuant test script

Purpose
-------
Compare baseline Hugging Face generation vs TurboQuant KV-cache compression
on the same prompt and model.

What it measures
----------------
- generation latency
- tokens/sec
- peak GPU memory allocated (approx)
- output text sample

Requirements
------------
pip install torch transformers turboquant

Recommended first model
-----------------------
Qwen/Qwen2.5-3B-Instruct

Usage
-----
python turboquant_local_test.py

Edit MODEL_NAME and PROMPT below if needed.
"""

import time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from turboquant import TurboQuantCache

MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"
PROMPT = (
    "Summarize the practical implications of KV-cache compression for local LLM inference "
    "in 5 bullet points, then give one short recommendation for a developer with a 16 GB GPU."
)
MAX_NEW_TOKENS = 256
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.float16 if DEVICE == "cuda" else torch.float32


def gpu_mem_mb():
    if not torch.cuda.is_available():
        return 0.0
    return torch.cuda.max_memory_allocated() / (1024 ** 2)


def reset_gpu_stats():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        torch.cuda.synchronize()


def run_generation(model, tokenizer, prompt, max_new_tokens=256, use_turboquant=False, bits=4):
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    cache = None
    if use_turboquant:
        cache = TurboQuantCache(bits=bits)

    reset_gpu_stats()
    start = time.time()

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            use_cache=True,
            past_key_values=cache,
        )

    if torch.cuda.is_available():
        torch.cuda.synchronize()

    elapsed = time.time() - start
    output_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    new_tokens = outputs.shape[1] - inputs["input_ids"].shape[1]
    tps = new_tokens / elapsed if elapsed > 0 else 0.0
    mem = gpu_mem_mb()

    return {
        "elapsed_s": elapsed,
        "new_tokens": int(new_tokens),
        "tokens_per_s": tps,
        "peak_mem_mb": mem,
        "text": output_text,
    }


def print_result(label, result):
    print(f"\n=== {label} ===")
    print(f"Elapsed:        {result['elapsed_s']:.2f} s")
    print(f"New tokens:     {result['new_tokens']}")
    print(f"Tokens / sec:   {result['tokens_per_s']:.2f}")
    print(f"Peak GPU mem:   {result['peak_mem_mb']:.1f} MB")
    print("Output preview:")
    print(result["text"][:1200])


def main():
    print(f"Loading model: {MODEL_NAME}")
    print(f"Device: {DEVICE}")

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=DTYPE,
        device_map="auto" if DEVICE == "cuda" else None,
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    if tokenizer.pad_token is None and tokenizer.eos_token is not None:
        tokenizer.pad_token = tokenizer.eos_token

    baseline = run_generation(
        model,
        tokenizer,
        PROMPT,
        max_new_tokens=MAX_NEW_TOKENS,
        use_turboquant=False,
    )
    print_result("Baseline FP16 KV", baseline)

    tq4 = run_generation(
        model,
        tokenizer,
        PROMPT,
        max_new_tokens=MAX_NEW_TOKENS,
        use_turboquant=True,
        bits=4,
    )
    print_result("TurboQuant 4-bit KV", tq4)

    print("\n=== Delta ===")
    print(f"Memory saved:   {baseline['peak_mem_mb'] - tq4['peak_mem_mb']:.1f} MB")
    print(f"TPS delta:      {tq4['tokens_per_s'] - baseline['tokens_per_s']:.2f}")


if __name__ == "__main__":
    main()
