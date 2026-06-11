import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
from typing import Tuple, Dict, Any, List

def make_bpp1():
    k = 500
    b = 10
    weights = np.arange(1, k+1, dtype=np.float64)
    return weights, b

def make_bpp2():
    k = 500
    b = 50
    i = np.arange(1, k+1, dtype=np.float64)
    weights = (i * i) / 2.0
    return weights, b

# Compute bin sums efficiently with bincount
def fitness_from_assignment(assignment: np.ndarray, weights: np.ndarray, b: int) -> Tuple[float, float]:
    sums = np.bincount(assignment, weights=weights, minlength=b)
    d = float(sums.max() - sums.min())
    fitness = 100.0 / (1.0 + d)
    return fitness, d

# Tournament selection: returns index of selected parent
def tournament_select(fitnesses: np.ndarray, rng: np.random.Generator, t: int) -> int:
    pop_size = len(fitnesses)
    indices = rng.integers(0, pop_size, size=t)
    best_idx = indices[np.argmax(fitnesses[indices])]
    return int(best_idx)

# Uniform crossover
def uniform_crossover(p1: np.ndarray, p2: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    mask = rng.random(p1.shape[0]) < 0.5
    child = np.where(mask, p1, p2)
    return child.copy()

# Random reassignment for each gene with prob pm
def mutate(child: np.ndarray, b: int, pm: float, rng: np.random.Generator) -> None:
    if pm <= 0.0:
        return
    mut_mask = rng.random(child.shape[0]) < pm
    n_mut = int(mut_mask.sum())
    if n_mut > 0:
        child[mut_mask] = rng.integers(0, b, size=n_mut)

# One GA trial
def run_ga_trial(weights: np.ndarray,
                 b: int,
                 pop_size: int = 100,
                 pm: float = 0.01,
                 t: int = 3,
                 pc: float = 0.8,
                 max_evals: int = 10_000,
                 seed: int = 0) -> Dict[str, Any]:

    rng = np.random.default_rng(seed)
    k = weights.shape[0]

    # Initialize population: assignments in 0..b-1
    population = rng.integers(0, b, size=(pop_size, k), dtype=np.int16)

    # Evaluate initial population (counts toward evaluations)
    fitnesses = np.zeros(pop_size, dtype=np.float64)
    ds = np.zeros(pop_size, dtype=np.float64)
    evals = 0
    for i in range(pop_size):
        f, d = fitness_from_assignment(population[i], weights, b)
        fitnesses[i] = f
        ds[i] = d
        evals += 1
        if evals >= max_evals:
            break
    
    best_idx = int(np.argmax(fitnesses))
    best_f, best_d = float(fitnesses[best_idx]), float(ds[best_idx])

    generations = 0

    # Generational loop with elitism
    while evals < max_evals:
        elite_idx = int(np.argmax(fitnesses))
        elite = population[elite_idx].copy()
        elite_f = float(fitnesses[elite_idx])
        elite_d = float(ds[elite_idx])

        new_pop = [elite]
        new_fit = [elite_f]
        new_ds = [elite_d]

        # Fill the rest
        while len(new_pop) < pop_size and evals < max_evals:
            # Parent selection
            p1_idx = tournament_select(fitnesses, rng, t)
            p2_idx = tournament_select(fitnesses, rng, t)

            # Crossover
            if rng.random() < pc:
                child = uniform_crossover(population[p1_idx], population[p2_idx], rng)
            else:
                child = population[p1_idx].copy()

            # Mutation
            mutate(child, b, pm, rng)

            # Evaluate child
            f, d = fitness_from_assignment(child, weights, b)
            new_pop.append(child)
            new_fit.append(f)
            new_ds.append(d)
            evals += 1

        # Convert lists to arrays
        population = np.array(new_pop, dtype=np.int16)
        fitnesses = np.array(new_fit, dtype=np.float64)
        ds = np.array(new_ds, dtype=np.float64)

        # Track best
        idx = int(np.argmax(fitnesses))
        if fitnesses[idx] > best_f:
            best_f = float(fitnesses[idx])
            best_d = float(ds[idx])
        generations += 1

    # Final best index
    final_idx = int(np.argmax(fitnesses))
    result = {
        "best_fitness": best_f,
        "best_d": best_d,
        "generations": generations,
        "evals": evals,
        "final_pop_size": population.shape[0],
        "final_best_fitness": float(fitnesses[final_idx]),
        "final_best_d": float(ds[final_idx]),
    }
    return result

# Run all experiments
def run_experiments():
    configs = [
        {"pop_size": 100, "pm": 0.01, "t": 3},
        {"pop_size": 100, "pm": 0.05, "t": 3},
        {"pop_size": 100, "pm": 0.01, "t": 7},
        {"pop_size": 100, "pm": 0.05, "t": 7},
    ]
    pc = 0.8
    trials = 5
    max_evals = 10_000

    records = []

    # BPP1
    w1, b1 = make_bpp1()
    # BPP2
    w2, b2 = make_bpp2()

    problems = [("BPP1", w1, b1), ("BPP2", w2, b2)]

    for prob_name, weights, b in problems:
        for cfg_idx, cfg in enumerate(configs):
            for trial in range(trials):
                seed = 1000 * (cfg_idx + 1) + trial
                res = run_ga_trial(weights, b,
                                   pop_size=cfg["pop_size"],
                                   pm=cfg["pm"],
                                   t=cfg["t"],
                                   pc=pc,
                                   max_evals=max_evals,
                                   seed=seed)
                records.append({
                    "problem": prob_name,
                    "pop_size": cfg["pop_size"],
                    "pm": cfg["pm"],
                    "tournament_size": cfg["t"],
                    "pc": pc,
                    "trial": trial + 1,
                    "best_fitness": res["best_fitness"],
                    "best_d": res["best_d"],
                    "generations": res["generations"],
                    "evals": res["evals"],
                    "final_pop_size": res["final_pop_size"],
                })

    df = pd.DataFrame.from_records(records)
    return df

df_results = run_experiments()

# Show raw results
print("GA Bin-Packing Results (All Trials)", df_results)

# Build summary tables
def summarise_results(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby(["problem", "pop_size", "pm", "tournament_size", "pc"], as_index=False).agg(
        mean_best_fitness=("best_fitness", "mean"),
        std_best_fitness=("best_fitness", "std"),
        mean_best_d=("best_d", "mean"),
        std_best_d=("best_d", "std"),
        mean_generations=("generations", "mean"),
        mean_evals=("evals", "mean"),
    )
    grp["setting"] = grp.apply(lambda r: f"p=100, pm={r['pm']}, t={int(r['tournament_size'])}", axis=1)
    order = ["p=100, pm=0.01, t=3", "p=100, pm=0.05, t=3", "p=100, pm=0.01, t=7", "p=100, pm=0.05, t=7"]
    grp["setting"] = pd.Categorical(grp["setting"], categories=order, ordered=True)
    grp = grp.sort_values(["problem", "setting"]).reset_index(drop=True)
    return grp

df_summary = summarise_results(df_results)

print("GA Bin-Packing Summary (means & std)", df_summary[
    ["problem", "setting", "mean_best_fitness", "std_best_fitness", "mean_best_d", "std_best_d", "mean_generations"]
])

# Plot average best fitness
for prob in ["BPP1", "BPP2"]:
    sub = df_summary[df_summary["problem"] == prob]
    plt.figure()
    plt.title(f"{prob}: Average Best Fitness by Setting")
    plt.bar(sub["setting"].astype(str), sub["mean_best_fitness"])
    plt.xticks(rotation=20, ha="right")
    plt.ylabel("Average Best Fitness")
    plt.xlabel("Setting")
    plt.tight_layout()
    plt.show()

# Show the best single trial
df_best_trials = (df_results
                  .sort_values(["problem", "pop_size", "pm", "tournament_size", "best_fitness"], ascending=[True, True, True, True, False])
                  .groupby(["problem", "pop_size", "pm", "tournament_size"], as_index=False)
                  .first())
print("Best Trial per Setting", df_best_trials[
    ["problem", "pop_size", "pm", "tournament_size", "trial", "best_fitness", "best_d", "generations"]
])
