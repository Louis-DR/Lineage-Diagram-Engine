import svgpathtools as svg
import numpy        as np

def smootherstep(linear: float) -> float:
  """Smooth step function implementing quintic smoothing."""
  if linear <= 0: return 0
  if linear >= 1: return 1
  squared = linear * linear
  cubed   = linear * squared
  return cubed * (6.0 * squared - 15.0 * linear + 10.0)

def find_t_at_x(
    path:       svg.Path,
    target_x:   float,
    resolution: int = 100
  ) -> float:
  """Get the T position along the path corresponding to the X position."""
  # ToDo replace with binary search + align to expected resolution for perfect match
  # Quick coarse search
  best_t   = 0.0
  min_dist = float('inf')
  for t in np.linspace(0, 1, resolution):
    point = path.point(t)
    dist = abs(point.real - target_x)
    if dist < min_dist:
      min_dist = dist
      best_t = t
  # Refine with binary search around the best coarse t
  low  = max(0, best_t - 0.01)
  high = min(1, best_t + 0.01)
  for _ in range(10):
    mid   = (low + high) / 2
    point = path.point(mid)
    if point.real < target_x:
      low = mid
    else:
      high = mid
  return (low + high) / 2
