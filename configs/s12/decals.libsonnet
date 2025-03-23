function(decal_colors, decal_spec) [
  {
    local body_decals = [
    // {
    //     name: 'maasr',
    //     size: [null, 40],
    //     pos: [-60, -580],
    //     color: decal_colors[1],
    // },
    // {
    //     name: 'fanatec',
    //     size: [null, 20],
    //     pos: [-70, -640],
    //     color: decal_colors[0],
    // },
    // {
    //     name: 'LT/lt_long',
    //     size: [null, 30],
    //     pos: [150, -635],
    //     color: decal_colors[0],
    // },
    // {
    //     name: 'podium',
    //     size: [null, 30],
    //     pos: [320, -630],
    //     color: decal_colors[0],
    // },
    ],
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
    ]
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
    ]
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
]
