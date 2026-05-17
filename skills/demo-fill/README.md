# Demo Fill Skill

**Purpose:** Fills in the skeleton example code with working implementations to demonstrate the framework.

## What This Does

By default, the example code shows placeholders:
```
✓ Feature computation would run here
✓ Model training would run here
✓ Model evaluation would run here
```

This skill replaces placeholders with **real working code** that:
- ✅ Downloads MovieLens dataset
- ✅ Computes actual features
- ✅ Trains a real model
- ✅ Shows evaluation metrics
- ✅ Generates predictions

## Usage

### Activate Demo
```bash
make demo
# or
python3 skills/demo-fill/activate.py
```

### Run Demo
```bash
make run
# Now shows real results!
```

### Restore Skeleton
```bash
make demo-restore
# or
python3 skills/demo-fill/restore.py
```

## When to Use This

- ✅ Want to see framework actually working
- ✅ Learning how components fit together
- ✅ Demoing to stakeholders
- ✅ Testing before writing your own code

## When NOT to Use This

- ❌ Just want to see code structure (skeleton is fine)
- ❌ Starting your own project (keep skeleton as template)
- ❌ Learning the framework concepts (skeleton shows structure)

## What Gets Modified

### Python Code (backed up and restorable)
The skill modifies these files:
- `examples/movie_recommendations/components/features.py`
- `examples/movie_recommendations/components/training.py`
- `examples/movie_recommendations/components/evaluation.py`
- `examples/movie_recommendations/components/serving.py`

Original files are backed up to `.backup/` so you can restore them.

### Generated Artifacts (cleaned on restore)
Running the demo creates these data files:
- `data/ratings.csv` - Downloaded MovieLens ratings
- `data/movies.csv` - Downloaded MovieLens movies
- `data/user_features.csv` - Computed user features
- `data/model.pkl` - Trained model
- `data/test_data.csv` - Test dataset split

**When you run `make demo-restore`:**
- ✅ Python files are restored from backups
- ✅ All generated data files are removed
- ✅ Backup directory is cleaned up
- ✅ Repository returns to pristine state

## Example Output

### Before (Skeleton)
```
[1/5] Data Ingestion
------------------------------------------------------------
⚠ Data ingestion skipped: (requires infrastructure)

[2/5] Feature Computation
------------------------------------------------------------
✓ Feature computation would run here
  (Simplified implementation for demo)
```

### After (Demo Filled)
```
[1/5] Data Ingestion
------------------------------------------------------------
Downloading MovieLens dataset...
✓ Downloaded 100,000 ratings from 600 users
✓ Dataset ready at examples/movie_recommendations/data

[2/5] Feature Computation
------------------------------------------------------------
Computing user features...
  • User avg rating: 3.52 ± 0.91
  • User rating count: 166.37 ± 286.45
✓ Computed 5 features for 600 users

[3/5] Model Training
------------------------------------------------------------
Training collaborative filtering model...
Epoch 1/10: Loss = 0.4523
Epoch 5/10: Loss = 0.2134
Epoch 10/10: Loss = 0.1245
✓ Model trained (10 epochs, 15.2s)

[4/5] Model Evaluation
------------------------------------------------------------
Evaluating on test set (20,000 ratings)...
  • RMSE: 0.87
  • MAE: 0.68
  • Accuracy@5: 0.82
✓ Evaluation complete

[5/5] Model Serving
------------------------------------------------------------
Sample predictions for user 42:
  1. Toy Story (1995) - Predicted: 4.2 ⭐
  2. Jumanji (1995) - Predicted: 3.8 ⭐
  3. Grumpier Old Men (1995) - Predicted: 3.5 ⭐
✓ Model ready for serving
```

## How It Works

The skill uses Python's AST to intelligently replace placeholder methods with real implementations while preserving:
- Class structure
- Method signatures
- Docstrings
- Your custom modifications

It's not a simple find-replace - it understands the code structure.

## Safety

- ✅ Creates backups before modifying
- ✅ Can be restored anytime
- ✅ Only modifies example code (not framework)
- ✅ Version controlled (git will show changes)

## Customization

After activating the demo, you can:
1. See how it works
2. Modify the demo code
3. Use it as a starting point for your own implementation
