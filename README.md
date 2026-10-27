# Simulation-Bogobots


Existe el paquete `bogobot_rviz` tiene un URDF del robot y un nodo, `joint_publisher`, que publica los ángulos de las 18 articulaciones (`q1`–`q18`) en el tópico `/joint_states`. Con esos ángulos, `robot_state_publisher` calcula dónde queda cada pieza del robot y RViz2 lo dibuja.

## Requirments

- Ubuntu 24.04
- ROS 2 Jazzy

Primero hay que ejecutar estos comandos en una terminal, uno por uno:
```
sudo apt update
sudo apt install ros-jazzy-desktop ros-jazzy-robot-state-publisher ros-jazzy-xacro python3-colcon-common-extensions python3-rosdep
source /opt/ros/jazzy/setup.bash
```

## Instalation
tenemos que instalar varias cosas para que funcione de manera correcta

Oviamente si no tienes el repo lo instalas:
```
git clone https://github.com/Humanoid-bogobot-cem/Simulation-Bogobots.git
cd Simulation-Bogobots
```
Instala las dependencias que falten:
```
sudo rosdep init   # solo la primera vez
rosdep update
rosdep install --from-paths bogobot_rviz --ignore-src -y
```
Por último, compila y carga el paquete:
```
colcon build --symlink-install
source install/setup.bash
```

Solo que recuerda que  `source install/setup.bash` se tiene que correr en **cada terminal nueva** porque si no no va a encotrar nada

## Run Instructions for First Demo

En una terminal, corre el launch del paquete ```bogobot_rviz```:
```
ros2 launch bogobot_rviz simulation_launch.py use_sim_time:=false
```
Se abre RViz2 con el robot y el brazo izquierdo (`q3`) moviéndose. Si RViz2 no se abre solo, ábrelo en otra terminal:
```
rviz2 -d bogobot_rviz/urdf/rviz_conf.rviz
```

### Cómo funciona

Hay tres nodos que se pasan información por tópicos:

```
joint_publisher ──/joint_states──► robot_state_publisher ──/tf──► RViz2
```

1. **`joint_publisher`** se dedica a decir cuántos radianes tiene girado cada motor.
2. **`robot_state_publisher`** tiene el URDF, así que sabe qué pieza va unida a cuál. Con los ángulos calcula dónde queda cada pieza y lo publica en `/tf`.
3. **RViz2** lee `/tf` y dibuja el robot.

`joint_publisher` manda ángulos nuevos 30 veces por segundo. Si los ángulos cambian con el tiempo, el robot se ve moviéndose.

### Cómo funciona el código de `joint_publisher`

El archivo es `bogobot_rviz/bogobot_rviz/joint_publisher.py`. Cada 1/30 de segundo pasa esto se supone que: calcula `t`, es los segundos que han pasado desde que arrancó el nodo despues llama a `calcular_posiciones(t)`, que regresa un diccionario con el ángulo de cada joint, `{'q3': 0.4, 'q7': -0.2}`, si por alguna razon no mandas un joint en el diccionario pues simplemente es 0 y por ultimo arma el mensaje con los 18 nombres y sus ángulos y lo publica en `/joint_states`.





### Cómo poner tu propio movimiento o cinemática

Solo tienes que cambiar lo que regresa `calcular_posiciones(t)`. Algunos ejemplos:

**Una pose fija** (el robot se queda quieto en esa posición):
```python
return {'q1': -1.0, 'q3': 0.5}
```

**Tu propia secuencia de poses:** edita la lista `POSES` y `DURACION` al inicio del archivo y usa el modo `secuencia`.

**Una cinemática:** la cinemática es una función que recibe dónde quieres el pie o la mano y regresa los ángulos. Para que el robot se mueva, pide una posición distinta según `t`:
```python
def calcular_posiciones(self, t):
    altura_pie = 0.05 * math.sin(t)          # el pie sube y baja
    return mi_cinematica_inversa(altura_pie)  # regresa {'q7': ..., 'q9': ..., ...}
```
Después de editar el código, vuelve a compilar y relanza:
```
colcon build --symlink-install
source install/setup.bash
ros2 launch bogobot_rviz simulation_launch.py use_sim_time:=false
```


## References

1. Open Robotics. (2024). *robot_state_publisher* [Software]. GitHub. https://github.com/ros/robot_state_publisher

