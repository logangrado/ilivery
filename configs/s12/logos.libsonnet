function(logo_facecolor, logo_edgecolor, spec, edgespec, edgeratio=0.1) [{
      section: "segments.body",
      layers: [
        {
          type: 'DECAL',
          decal: {
            type: 'LOGO',
            facecolor: logo_facecolor,
            edgecolor: logo_edgecolor,
            facespec: spec,
            edgespec: edgespec,
            edgeratio: edgeratio,
            size: 350,
          },
          pos: [170, -500],
          mirror: {
            axis: 'x',
            rotate: true,
          },
        },
        {
          type: 'DECAL',
          decal: {
            type: 'LOGO',
            facecolor: logo_facecolor,
            edgecolor: logo_edgecolor,
            facespec: spec,
            edgespec: edgespec,
            edgeratio: edgeratio,
            size: 300,
          },
          pos: [-430, 0],
          rotate: -90,
        },
      ]
    }]
