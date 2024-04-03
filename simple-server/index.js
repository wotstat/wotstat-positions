const express = require('express')

const app = express()
const port = 8000

app.use(express.json());

app.get('/api/v1/positions', (req, res) => {
  const {
    region,
    mode,
    gameplay,
    arena,
    team,
    tank,
    level,
    type,
    role,
    health,
    position,
    time,
    allyfrags,
    enemyfrags
  } = req.query

  console.log({ region, mode, gameplay, arena, team, tank, level, type, role, health, position, time, allyfrags, enemyfrags })

  return res.json({
    status: "ok",
    message: {
      RU: "Всё работает",
      EN: "Works fine"
    },
    statistics: {
      tag: tank,
      role,
      type,
      level,
      health: Math.round(health * 10) / 10,
      time: Math.round(time / 30) * 30,
      position: true,
      allyFrags: allyfrags,
      enemyFrags: enemyfrags,
      count: 5000
    },
    positions: {
      polygons: [
        {
          efficiency: 0.3,
          area: [[0, 0], [0, 300], [200, 300], [300, 0]]
        },
        {
          efficiency: 0.5,
          area: [[-350, -350], [-350, -100], [-300, -100], [-300, -350]]
        }
      ],
      points: [
        {
          efficiency: 0.5,
          position: [0, 350]
        },
        {
          efficiency: 0.5,
          position: [0, -350]
        },
        {
          efficiency: 1,
          position: [200, -350]
        },
        // ...Array.from({ length: 1000 }, (_, i) => ({
        //   efficiency: 1,
        //   position: [Math.random() * 900 - 450, Math.random() * 900 - 450]
        // }))
      ],
      idealPoints: [
        {
          efficiency: 0.5,
          position: [-200, 200]
        },
        {
          efficiency: 0.7,
          position: [200, -200]
        },
        // {
        //   efficiency: 0.7,
        //   position: [200, 300]
        // },
...Array.from({ length: 20 }, (_, i) => ({
          efficiency: 1,
          position: [Math.random() * 900 - 450, Math.random() * 900 - 450]
        }))
      ]
    }
  })
})


app.get('/api', (req, res) => {
  res.send({ status: 'ok' }).end()
})

app.listen(port, () => {
  console.log(`Simple server start at http://localhost:${port}`)
})