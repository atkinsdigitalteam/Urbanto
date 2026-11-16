"""C9: cost of a microscopic agent-based run (JuPedSim 1.4.2, LGPL-3.0+, C++ core, Python API).

Walkable area = a G x G street grid at 100 m pitch with 12 m wide streets (88 m blocks are holes).
N agents start at random street positions and walk to one of 9 exit polygons (routing on
JuPedSim's own navigation mesh). Collision Free Speed Model, dt = 0.01 s (the default).
Times `steps` iterations and reports seconds per simulated second and per agent-step.
Usage: PYTHONPATH=<pylib> python3 bench_jupedsim.py --grid 10 --agents 10000 --steps 1000
"""
import argparse, json, os, resource, time
import numpy as np
import shapely
from shapely.geometry import box
import jupedsim as jps

ap = argparse.ArgumentParser()
ap.add_argument("--grid", type=int, default=10)      # blocks per side
ap.add_argument("--agents", type=int, default=10000)
ap.add_argument("--steps", type=int, default=1000)
a = ap.parse_args()
P, W = 100.0, 12.0
L = a.grid * P + W
outer = box(0, 0, L, L)
blocks = [box(W + i * P, W + j * P, (i + 1) * P, (j + 1) * P) for i in range(a.grid) for j in range(a.grid)]
area = outer.difference(shapely.union_all(blocks))

t0 = time.perf_counter()
sim = jps.Simulation(model=jps.CollisionFreeSpeedModel(), geometry=area)
exits = []
for i in (1, a.grid // 2, a.grid - 1):
    for j in (1, a.grid // 2, a.grid - 1):
        x, y = i * P + W / 2, j * P + W / 2          # an intersection centre
        exits.append(sim.add_exit_stage(box(x - 3, y - 3, x + 3, y + 3)))
journeys = [sim.add_journey(jps.JourneyDescription([e])) for e in exits]
# candidate start points: 1 m lattice along street centre lines, 5 lanes across, no intersections
rng = np.random.default_rng(3)
cand = []
for k in range(a.grid + 1):
    c = k * P + W / 2
    for s in np.arange(W + 1, L - W, 1.0):
        if (s % P) < W + 1:                            # skip intersection squares
            continue
        for off in (-4, -2, 0, 2, 4):
            cand.append((s, c + off)); cand.append((c + off, s))
cand = np.array(cand)
pick = cand[rng.choice(len(cand), a.agents, replace=False)]
for n, (x, y) in enumerate(pick):
    jid = int(rng.integers(len(exits)))
    sim.add_agent(jps.CollisionFreeSpeedModelAgentParameters(
        position=(float(x), float(y)), journey_id=journeys[jid], stage_id=exits[jid]))
t_setup = time.perf_counter() - t0
t = time.perf_counter()
sim.iterate(a.steps)
dt_run = time.perf_counter() - t
sim_s = a.steps * sim.delta_time()
print(json.dumps(dict(tool="jupedsim " + jps.__version__, grid_blocks=a.grid, area_km2=round(L * L / 1e6, 2),
                      agents=a.agents, steps=a.steps, simulated_s=sim_s, setup_s=round(t_setup, 2),
                      run_s=round(dt_run, 2), wall_per_simulated_s=round(dt_run / sim_s, 2),
                      us_per_agent_step=round(dt_run / a.steps / a.agents * 1e6, 3),
                      agents_left=sim.agent_count(),
                      peak_rss_mb=round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024),
                      loadavg_1m=round(os.getloadavg()[0], 2))))
