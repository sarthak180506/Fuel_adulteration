# Contributing to FuelGuard

## Branch Strategy

```
main                    ← stable, tested, paper-ready snapshots only
 └── dev                ← integration branch (all PRs merge here first)
      ├── feature/ml-pipeline          ← Sarthak (ML Engineer)
      ├── feature/firmware-esp32       ← [Firmware Engineer]
      ├── feature/dashboard-supabase   ← [Full-Stack Engineer]
      └── feature/research-paper       ← [Research Lead]
```

### Rules
1. **Never push directly to `main` or `dev`**. Always open a PR.
2. All PRs target **`dev`** (not `main`).
3. `main` is updated only when a milestone is complete (e.g., Experiment A done, Phase 2 fusion working).
4. Each person works exclusively on their own branch. Cross-cutting changes are discussed in an issue first.

## Commit Message Format

```
<type>(<scope>): <short description>

Types: feat | fix | data | model | refactor | test | docs | chore
Scope: ml | firmware | dashboard | research | ci

Examples:
  feat(ml): add XGBoost regressor with early stopping
  fix(firmware): correct FDC1004 I2C address from 0x50 to 0x50 → 0x2A
  data(ml): add 40°C replicate measurements for kerosene series
  model(ml): MLP achieves 94.2% accuracy — update summary.json
  docs(research): add related works section for IEEE paper
```

## Code Review Process

1. Open PR from `feature/*` → `dev`
2. Assign at least **one reviewer** (ideally the person whose module interfaces with yours)
3. Fill out the PR template — **mandatory for ML changes**: report accuracy/RMSE before vs. after
4. CI must pass (green) before merge
5. Squash-merge to keep `dev` history clean

## Secrets & Safety

- **Never commit** `config_local.h`, `.env.local`, Wi-Fi passwords, or Supabase keys
- Calibration JSON (`firmware/data/calibration.json`) contains only safe numerical constants — OK to commit
- All fuel sample handling follows the lab safety checklist in `docs/safety_checklist.md`
