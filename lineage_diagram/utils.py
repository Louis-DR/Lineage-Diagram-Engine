import svgpathtools as svg

def smootherstep(x: float) -> float:
  """
  Compute the smootherstep function for a value between 0 and 1.
  This function provides a smooth transition with zero 1st and 2nd derivatives at endpoints.
  Equation: 6x^5 - 15x^4 + 10x^3
  """
  return 6 * x**5 - 15 * x**4 + 10 * x**3

def find_t_at_x(path: svg.Path, x: float, tolerance: float = 1e-6) -> float:
  """
  Find the parameter t (0 to 1) on the path such that path.point(t).real is close to x.
  Assumes the path is monotonic in X.
  Uses binary search.
  """
  t_min = 0.0
  t_max = 1.0

  # Check boundaries
  if x <= path.point(t_min).real: return t_min
  if x >= path.point(t_max).real: return t_max

  # Binary search
  for _ in range(100):
    t_mid = (t_min + t_max) / 2
    p_mid = path.point(t_mid)

    if abs(p_mid.real - x) < tolerance:
      return t_mid

    if p_mid.real < x:
      t_min = t_mid
    else:
      t_max = t_mid

  return (t_min + t_max) / 2
