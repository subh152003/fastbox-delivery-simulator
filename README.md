# FastBox Delivery Simulator

Python delivery simulation for Nexgensis Technologies assignment. Assigns packages to agents based on minimum Euclidean distance.

## Architecture & Assumptions
- **Flexible Data Parser:** Supports list and dictionary JSON schemas.
- **Assumptions Made:**
  - Greedy nearest-agent assignment.
  - Agent moves to package destination upon completion.
  - Efficiency is evaluated as `total_distance / packages_delivered` (lower score is better).

## Execution Instructions
Run the main script:
```bash
python solution.py
