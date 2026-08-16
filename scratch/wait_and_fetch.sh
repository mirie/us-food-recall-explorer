#!/bin/bash
# Throwaway script: poll all 3 Phase 5 batches until they end, then run
# `classify_all.py fetch` automatically. Not checked in.
set -e
cd "$(dirname "$0")/.."

while true; do
    STATUS=$(PYTHONPATH=. .venv/bin/python -c "
import anthropic, json
client = anthropic.Anthropic()
batches = json.load(open('data/batch_ids.json'))['batches']
statuses = []
for b in batches:
    batch = client.messages.batches.retrieve(b['batch_id'])
    statuses.append(batch.processing_status)
    print(f\"{b['batch_id']}: {batch.processing_status} {batch.request_counts}\")
print('ALL_ENDED' if all(s == 'ended' for s in statuses) else 'WAITING')
")
    echo "$STATUS"
    if echo "$STATUS" | grep -q "ALL_ENDED"; then
        echo "All batches ended. Running fetch..."
        PYTHONPATH=. .venv/bin/python classify_all.py fetch
        break
    fi
    sleep 90
done
