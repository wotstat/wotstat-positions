const express = require('express')

const app = express()
const port = process.env.PORT || 8000

app.use(express.json());

app.post('/api/v1/positions', (req, res) => {
  const {
    id,
    language,
    token,
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
    allyFrags,
    enemyFrags,
    allyHealth,
    enemyHealth,
    allyMaxHealth,
    enemyMaxHealth,
  } = req.body

  console.log({
    id, language, token,
    region, mode, gameplay, arena, team, tank, level, type, role, health, position,
    time, allyFrags, enemyFrags, allyHealth, enemyHealth, allyMaxHealth, enemyMaxHealth
  })

  return res.json({
    status: "ok",
    message: {
      type: "info",
      value: "Позиции обновлены. 1234 значений"
    },
    token: new Date().getTime().toString(),
    statistics: {
      tag: tank,
      role,
      type,
      level,
      health: Math.round(health * 10) / 10,
      time: Math.round(time / 30) * 30,
      position: true,
      allyFrags,
      enemyFrags,
      count: 5000
    },
    positions: {
      polygons: [
        {
          efficiency: .3,
          area: [[-250, -250], [-250, -100], [-200, -100], [-200, -250]]
        },
        {
          efficiency: .6,
          area: [[0, 0], [0, 300], [200, 300], [300, 0]]
        },
        {
          efficiency: 1,
          area: [[-350, -350], [-350, -100], [-300, -100], [-300, -350]]
        }
      ],
      points: [
        {
          efficiency: 1,
          position: [100, 100]
        },
        {
          efficiency: 0.5,
          position: [0, 120]
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
          efficiency: 1,
          position: [0, 0]
        },
        {
          efficiency: 0.7,
          position: [200, -200]
        },
        {
          efficiency: 0.7,
          position: [200, 300]
        },
        // ...Array.from({ length: 1 }, (_, i) => ({
        //   efficiency: 1,
        //   position: [Math.random() * 900 - 450, Math.random() * 900 - 450]
        // }))
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