#!/bin/bash
# Gortex Fine-Tuning Preparation Script
# Usage: ./scripts/prepare_training.sh [dataset_path]

set -e

DATASET=${1:-"logs/datasets/evolution.jsonl"}

echo "🔍 Starting Fine-Tuning Preparation..."
echo "📂 Source Dataset: $DATASET"

# Check if dataset exists
if [ ! -f "$DATASET" ]; then
    echo "❌ Error: Dataset not found at $DATASET"
    echo "💡 Hint: Run an analysis session first to generate data."
    exit 1
fi

# Execute Python logic
python3 -c "
from gortex.agents.evolution_node import EvolutionNode
import sys

node = EvolutionNode()
result = node.prepare_fine_tuning_job('$DATASET')

if result['status'] == 'success':
    print(f\"✅ Job Created: {result['job_dir']}\")
    print(f\"📊 Items: {result['item_count']}\")
    sys.exit(0)
else:
    print(f\"❌ Failed: {result.get('reason', 'Unknown error')}\")
    sys.exit(1)
"

echo "🚀 Ready to train! (Check training_jobs/ folder)"
