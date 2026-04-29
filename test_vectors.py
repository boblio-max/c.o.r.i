from ik_solver import IKSolver
import numpy as np

solver = IKSolver(L=1.0)

# Test with a simple target
target = (1.0, 0.0, 0.5)
print(f"Target: {target}")

v1, v2, v3 = solver.update_vect(target)
print(f"\nv1: {v1}")
print(f"v2: {v2}")
print(f"v3: {v3}")
print(f"\nSum of vectors: {v1 + v2 + v3}")
print(f"Target was:    {np.array(target)}")

# Also test the angles directly
angles = solver.solve(*target)
print(f"\nAngles (degrees): {angles}")
