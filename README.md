Repositorio Códigos para el proyecto final de programación 2026-1

REGLAS BÁSICAS DE JUEGO
1. Inicio del juego
- Cada jugador tiene 4 fichas; como son máximo 2 jugadores, habrá hasta 8 fichas en total.
- Cada ficha debe tener un nombre o identificador único para facilitar su manejo en el código.
- Todas las fichas empiezan en cárcel/base.
- Se define un turno inicial.
- Cada jugador recorre 72 casillas antes de llegar a meta.
- Las casillas 1, 8, 13, 18, 25, 30, 35, 42, 47, 52, 59 y 64 son casillas seguras.
- Las casillas 1 y 35 son casillas de salida.
2. Lanzamiento de dado
- Solo el jugador en turno puede lanzar.
- El dado genera un número aleatorio usando: random.randint(1,6)
- Como se usan dos dados, se deben generar dos valores independientes.
3. Salir de cárcel
- Una ficha sale de cárcel solo si los dados sacan presada (doble).
- Si no hay presada, la ficha permanece en cárcel.
4. Movimiento de ficha
- Las fichas avanzan exactamente la suma de los dados.
- El jugador puede escoger qué ficha mover.
- Solo puede moverse si la jugada es válida.
5. Validación de casilla
Antes de mover:
- Verificar que la ficha exista.
- Verificar que pertenezca al jugador en turno.
- Verificar que el movimiento no exceda la meta.
6. Cambio de turno
- Si no hay jugada extra, pasa al siguiente jugador.
- Si el jugador saca presada, puede repetir turno.
7. Comer ficha
- Si una ficha cae en una casilla ocupada por una ficha rival, la ficha rival vuelve a cárcel.
- Si un jugador sale de cárcel y en su casilla de salida hay ficha(s) rival(es), esa(s) ficha(s) vuelven a cárcel.
8. Casillas seguras
- En casillas seguras no se puede comer ficha rival.
9. Entrada a meta
- Solo se entra con número exacto.
- Si al jugador solo le queda 1 ficha y la distancia restante a meta es menor o igual a 6, solo puede lanzar 1 dado.
10. Ganador
- Gana quien logre meter sus 4 fichas en meta 🏁
