#!/usr/bin/env bash
# PreCompact hook for the daily feed routine.
# Compaction is allowed during PHASE 1 (research). Once PHASE 2 (publish)
# starts, the routine creates the marker file below and every compaction
# (auto or manual) is blocked until the marker is removed.
MARKER=/tmp/feed/PUBLISH_PHASE
if [ -f "$MARKER" ]; then
  echo "Compaction blocked: the daily feed routine is in PHASE 2 (publish). Finish publishing first." >&2
  exit 2
fi
exit 0
