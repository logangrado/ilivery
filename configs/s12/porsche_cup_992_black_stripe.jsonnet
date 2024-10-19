local decal_function = import 'decals.libsonnet';
local logo_function = import 'logos.libsonnet';

local vector_add(points, offset) =
  std.map(
    function(point)
      [point[0] + offset[0], point[1] + offset[1]],
    points
  );
{
  local colors = [
    // "#444444",
    "#202025",
    // '#101030',
    // '#0070ff',
    // '#aa3030',
    '#841617',
    '#cccccc',
  ],
  local accent_colors = [
    '#000000',
    '#000000',
    '#000000',
  ],
  local decal_colors = [
    colors[2],
    colors[2],
    // accent_colors[1],
    // accent_colors[2],
  ],

  local logo_colors = [
    "#000000",
    // colors[0],
    colors[1],
  ],
  local body_spec = 'METALLIC',
  local logo_spec = 'MATTE',
  local logo_edgespec = "MATTE",
  local decal_spec = 'MATTE',
  local accent_spec = "MATTE",

  local section_spec = 'MATTE',
  local section_edgespec = 'CHROME',
  local edgewidth = 5,
  local stripe_width = 20,
  local stripe_offset = 0,

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
      triangle_size: 50,
      face_cmap: {
        type: 'LINEAR_SEGMENTED',
        colors: [
          {
            color: colors[0],
            spread: 0.1,
          },
          // {
          //   color: colors[1],
          //   spread: 0.3,
          // },
        ],
        n_levels: 3,
        // segments: std.makeArray(2, function(_) 0.5),
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
    // BASE LAYER: CF ON EVERYTHING
    {
      layers: [{
        type: 'TEXTURE',
        texture: 'CARBON_FIBER',
      }],
    },
    // BASE COLOR ON ALL COMPONENTS
    {
      section: 'segments.body | segments.rear_0 | segments.rear_1',
      layers: [{
        type: 'SOLID',
        color: colors[0],
        spec: body_spec,
      }],
    },
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
    // SECTIONS
    {
      section: 'segments.mirrors | segments.wing_endplate | segments.wing_supports | segments.rear_accent',
      layers: [{
        type: 'SOLID',
        color: colors[1],
        spec: accent_spec,
      }],
    },
    {
      local paths = [
        [
            [0,stripe_offset],
            [1000,stripe_offset],
        ],
        [
          [-870,stripe_offset],
          [-570,stripe_offset],
        ],
      ],
      section: 'segments.body',
      layers: [
        {
          type: 'STRIPE',
          facecolor: colors[1],
          facespec: accent_spec,
          edgecolor: "#ffffff",
          edgespec: "#ffffff",
          edgewidth: 0,
          path: path,
          width: stripe_width,
        }
        for path in paths
      ],
    },
    {
      section: 'segments.rear_0',
      layers: [
        {
          type: 'STRIPE',
          facecolor: colors[1],
          facespec: accent_spec,
          edgecolor: "#ffffff",
          edgespec: "#ffffff",
          edgewidth: 0,
          path: [
            [stripe_offset,-500],
            [stripe_offset,500],
          ],
          width: stripe_width,
        }
      ],
    },
    {
      section: 'segments.windshield_outside',
      layers: [{
        type: 'SOLID',
        color: "#000000",
        spec: "MATTE",
      }],
    },
    {
      section: 'segments.rear_bumper',
      layers: [
        {
          type: 'SOLID',
          color: colors[0],
          spec: body_spec,
        },
      ],
    },
    {
      section: 'segments.body',
      layers: [
        // Main sideskirt patch
        {
          local w = 800,
          local h = 100,
          type: 'PATCH',
          vertices: vector_add([
            [0, 0],
            [1000, 0],
            [1000, -100],
            [0, -100],
          ], [-240, -650]),
          facecolor: colors[1],
          edgecolor: colors[1],
          facespec: section_spec,
          edgespec: section_edgespec,
          edgewidth: 0, #edgewidth,
          mirror_patch: {
            axis: 'x',
          },
        },
        // Front patch
        {
          type: 'PATCH',
          vertices: vector_add([
            [0, -328],
            [0, -323],
            [0, -500],
            [-80, -500],
          ], [-960, 0]),
          facecolor: colors[1],
          edgecolor: colors[1],
          facespec: section_spec,
          edgespec: section_edgespec,
          edgewidth: 0, #edgewidth,
          mirror_vertices: {
            axis: 'x',
          },
        },
      ],
    },
    // {
    //   section: 'segments.rear_0',
    //   layers: [
    //     {
    //       type: 'STRIPE',
    //       facecolor: colors[1],
    //       facespec: accent_spec,
    //       edgecolor: "#ffffff",
    //       edgespec: "#ffffff",
    //       edgewidth: 0,
    //       path: [
    //         [280, -140],
    //         [500, -140],
    //       ],
    //       width: 30,
    //       mirror_patch: {
    //         axis: 'y',
    //       },
    //     }
    //   ],
    // },
    {
      section: 'segments.rear_0',
      layers: [
        // Main sideskirt patch
        {
          type: 'PATCH',
          vertices: vector_add([
            [250, 0],
            [500, -5],
            [500, -40],
            [285, -40],
          ], [0, -105]),
          facecolor: colors[1],
          edgecolor: colors[1],
          facespec: section_spec,
          edgespec: section_edgespec,
          edgewidth: 0, #edgewidth,
          mirror_patch: {
            axis: 'y',
          },
        },
      ]
    },
    {
      section: 'segments.rear_0',
      layers: [
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
  ]
  + decal_function(decal_colors, decal_spec)
  + logo_function(logo_colors[0], logo_colors[1], logo_spec, logo_edgespec, edgeratio=0.12)
}
