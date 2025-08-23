# GPT-4.1 Upgrade Notice

## Important: Model Update
As of April 2025, all scripts in this project should use GPT-4.1 models instead of GPT-3.5-turbo or older GPT-4 versions.

## GPT-4.1 Model Family
- **gpt-4.1**: Flagship model with highest performance (1M token context)
- **gpt-4.1-mini**: Balanced performance and cost (beats GPT-4o, 83% cheaper)
- **gpt-4.1-nano**: Fastest and cheapest for simple tasks

## Configuration Changes

### Environment Variables (.env)
```bash
DEFAULT_MODEL=gpt-4.1-mini
FALLBACK_MODEL=gpt-4.1-nano
PREMIUM_MODEL=gpt-4.1
```

### Model Selection by Task
1. **Episode Generation**: `gpt-4.1-mini` (best balance)
2. **Complex Scenes**: `gpt-4.1` (when quality matters most)
3. **Quick Iterations**: `gpt-4.1-nano` (for drafts/testing)
4. ~~`gpt-3.5-turbo`~~ - DEPRECATED, do not use

## Script Updates Required
All scripts should replace:
- `model="gpt-3.5-turbo"` → `model="gpt-4.1-mini"`
- Or use `os.getenv("DEFAULT_MODEL", "gpt-4.1-mini")`

## Key Improvements over GPT-4o
- **54.6%** task completion on SWE-bench (vs 33.2% for GPT-4o)
- **1M token** context window
- **32,768** output tokens (2x more than GPT-4o)
- **83% cheaper** (mini version)
- Better at following formats and instructions

## Pricing
- **gpt-4.1**: $2/1M input, $8/1M output tokens
- **gpt-4.1-mini**: $0.40/1M input, $1.60/1M output tokens
- **gpt-4.1-nano**: $0.10/1M input, $0.40/1M output tokens