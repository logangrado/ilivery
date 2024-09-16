local vector_add(points, offset) =
  std.map(
    function(point)
      [point[0] + offset[0], point[1] + offset[1]],
    points
  );
{
  local colors = [
    '#202020',
    '#1da0e0',
    '#dc261f',
  ],
  local accent_colors = [
    '#EB9300',
    '#101010',
    '#FFFFFF',
  ],
  local decal_colors = [
    accent_colors[1],
    accent_colors[2],
  ],
  local body_spec = 'METALLIC',
  local section_spec = 'MATTE',
  local section_edgespec = 'CHROME',
  local edgewidth = 5,
  local decal_spec = 'MATTE',
  local logo_spec = 'MATTE',

  local body_decals = [
    {
      name: 'maasr',
      size: [null, 40],
      pos: [-60, -580],
      color: decal_colors[1],
    },
    {
      name: 'fanatec',
      size: [null, 20],
      pos: [-70, -640],
      color: decal_colors[0],
    },
    {
      name: 'LT/lt_long',
      size: [null, 30],
      pos: [150, -635],
      color: decal_colors[0],
    },
    {
      name: 'podium',
      size: [null, 30],
      pos: [320, -630],
      color: decal_colors[0],
    },
  ],

  local pattern_layer = {
    type: 'PATTERN',
    pattern: {
      type: 'TRIANGLES',
      triangle_size: 100,
      face_cmap: {
        type: 'LINEAR_SEGMENTED',
        colors: [
          {
            color: colors[0],
            spread: 0.2,
          },
          {
            color: colors[1],
            spread: 0.3,
          },
        ],
        n_levels: 8,
        segments: std.makeArray(2, function(_) 0.5),
      },
      face_cfunc: {
        type: 'RANDOM_UNIFORM',
        seed: 0,
      },
      edgespec: body_spec,
      facespec: body_spec,
      spacing: -2,
    },
  },


  iracing_output: {
    car_number: 622340,
    paint_path: '/mnt/c/Users/Logan Grado/Documents/iracing/paint/porsche992cup',
  },
  template: 'porsche992cup',
  final_mask: '~segments.mask & ~segments.glass',
  sections: [
    {
      layers: [{
        type: 'TEXTURE',
        texture: 'CARBON_FIBER',
      }],
    },
    // PATTERNS AND BASE LAYERS
    // ========================
    {
      section: 'segments.body',
      layers: [
        {
          type: 'SOLID',
          color: colors[0],
          spec: body_spec,
        },
        pattern_layer {
          pattern: pattern_layer.pattern { angle: 90 },
        },
      ],
    },
    {
      section: 'segments.rear_0 | segments.rear_1',
      layers: [
        pattern_layer,
      ],
    },
    {
      section: 'segments.mirrors | segments.wing_endplate | segments.wing_supports',
      layers: [{
        type: 'SOLID',
        color: accent_colors[0],
        spec: section_spec,
      }],
    },
    {
      section: 'segments.rear_accent_2',
      layers: [{
        type: 'SOLID',
        color: accent_colors[0],
        spec: section_spec,
      }],
    },
    {
      section: 'segments.windshield_outside',
      layers: [{
        type: 'SOLID',
        color: colors[0],
        spec: section_spec,
      }],
    },
    // PATCHES
    // =======
    {
      section: 'segments.body',
      layers: [
        {
          local w = 800,
          local h = 100,
          type: 'PATCH',
          vertices: vector_add([
            [0, -23],
            [w * 0.6, -10],
            [w, 50],
            [w, -h],
            [0, -h],
          ], [-240, -600]),
          facecolor: accent_colors[0],
          edgecolor: accent_colors[1],
          facespec: section_spec,
          edgespec: section_edgespec,
          edgewidth: edgewidth,
          mirror_patch: {
            axis: 'x',
          },
        },
        {
          type: 'PATCH',
          vertices: vector_add([
            [-20, -328],
            [0, -323],
            [0, -500],
            [-80, -500],
          ], [-930, 0]),
          facecolor: accent_colors[0],
          edgecolor: accent_colors[1],
          facespec: section_spec,
          edgespec: section_edgespec,
          edgewidth: edgewidth,
          mirror_vertices: {
            axis: 'x',
          },
        },
      ],
    },
    {
      section: 'segments.rear_0',
      layers: [
        {
          type: 'PATCH',
          vertices: vector_add([
            [400, 0],
            [450, -300],
          ], [0, 30]),
          facecolor: colors[0],
          edgecolor: colors[0],
          facespec: section_spec,
          edgespec: section_edgespec,
          edgewidth: 0,
          mirror_vertices: { axis: 'y' },
        },
        {
          type: 'PATCH',
          vertices: vector_add([
            [0, -20],
            [370, -25],
            [580, -70],
            [580, -300],
            [420, -250],
            [320, -88],
            [10, -70],
          ], [0, 100]),
          radii: [300, 300, 0, 0, 0, 0, 0],
          facecolor: accent_colors[0],
          edgecolor: accent_colors[1],
          facespec: section_spec,
          edgespec: section_edgespec,
          edgewidth: edgewidth,
          mirror_vertices: { axis: 'y' },
        },
      ],
    },

    // DECALS
    // ===================================
    // Body decals
    {
      section: 'segments.body',
      layers: [
        {
          type: 'DECAL',
          decal: {
            type: 'NAMED',
            name: decal.name,
            color: decal.color,
            spec: decal_spec,
            size: decal.size,
          },
          pos: decal.pos,
          mirror: {
            axis: 'x',
            rotate: true,
          },
        }
        for decal in body_decals
      ] + [
        {
          type: 'DECAL',
          decal: {
            type: 'LOGO',
            facecolor: accent_colors[0],
            edgecolor: accent_colors[1],
            facespec: logo_spec,
            edgespec: logo_spec,
            edgeratio: 0.1,
            size: 250,
          },
          pos: [160, -500],
          mirror: {
            axis: 'x',
            rotate: true,
          },
        },
        {
          type: 'DECAL',
          decal: {
            type: 'LOGO',
            facecolor: accent_colors[0],
            edgecolor: accent_colors[1],
            facespec: logo_spec,
            edgespec: logo_spec,
            edgeratio: 0.1,
            size: 300,
          },
          pos: [-430, -15],
          rotate: -90,
        },

      ],
    },
    // Rear decals
    {
      section: 'segments.rear_0',
      layers: [
        {
          type: 'DECAL',
          decal: {
            type: 'NAMED',
            name: 'maasr',
            color: decal_colors[1],
            spec: decal_spec,
            size: [null, 45],
          },
          pos: [0, -10],
        },
        {
          type: 'DECAL',
          decal: {
            type: 'NAMED',
            name: 'LT/lt',
            color: decal_colors[0],
            spec: decal_spec,
            size: [100, 100],
          },
          rotate: -5,
          pos: [440, -20],
        },
        {
          type: 'DECAL',
          decal: {
            type: 'NAMED',
            name: 'LT/lt',
            color: decal_colors[0],
            spec: decal_spec,
            size: [100, 100],
          },
          rotate: 5,
          pos: [-440, -20],
        },
        {
          type: 'DECAL',
          decal: {
            type: 'LOGO',
            facecolor: decal_colors[1],
            edgecolor: decal_colors[0],
            facespec: logo_spec,
            edgespec: logo_spec,
            edgeratio: 0.1,
            size: 85,
          },
          pos: [-200, -15],
        },
      ],
    },
    {
      section: 'segments.windshield_outside',
      layers: [
        {
          type: 'DECAL',
          decal: {
            type: 'NAMED',
            name: 'porsche',
            color: decal_colors[1],
            spec: decal_spec,
            size: [400, 70],
          },
          pos: [0, 0],
          rotate: 270,
        },
      ],
    },
    // Wing decals
    {
      layers: [
        {
          type: 'CLASS_DECAL',
          class_name: 's12/pro',
          spec: 'MATTE',
        },
      ],
    },
    {
      section: 'segments.wing',
      layers: [
        {
          type: 'DECAL',
          decal: {
            type: 'NAMED',
            name: 'text_grado_porsche',
            color: decal_colors[1],
            spec: decal_spec,
            size: [null, 70],
          },
          pos: [0, -100],
          rotate: 180,
        },
        {
          type: 'DECAL',
          decal: {
            type: 'NAMED',
            name: 'text_grado_porsche',
            color: decal_colors[1],
            spec: decal_spec,
            size: [null, 70],
          },
          pos: [0, 55],
        },
      ],
    },
  ],
}
