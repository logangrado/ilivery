{
  vector_add(points, offset) :: (
    if std.isArray(points[0]) then
      std.map(
        function(point)
          [point[0] + offset[0], point[1] + offset[1]],
        points
      )
    else
      [points[0] + offset[0], points[1] + offset[1]]
  ),
  vector_scale(x,a) :: (
    [std.round(i*a) for i in x]
  ),
}
