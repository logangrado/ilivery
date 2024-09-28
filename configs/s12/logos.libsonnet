function(logo_facecolor, logo_edgecolor, spec) [{
      section: "segments.body",
      layers: [
        {
          type: 'DECAL',
          decal: {
            type: 'LOGO',
            facecolor: logo_facecolor,
            edgecolor: logo_edgecolor,
            facespec: spec,
            edgespec: spec,
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
            facecolor: logo_facecolor,
            edgecolor: logo_edgecolor,
            facespec: spec,
            edgespec: spec,
            edgeratio: 0.1,
            size: 300,
          },
          pos: [-430, -15],
          rotate: -90,
        },
      ]
    }]
