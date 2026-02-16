# Denso Robot - Docker

Ambiente Docker para robôs da DENSO com ROS2 Humble com suporte para RViz2 e Gazebo Fortress.

## Pré-requisitos

### Testar X11

```bash
xeyes
```

Se aparecer uma janela com dois olhos que seguem o cursor, o X11 está funcionando. **Pule para "Primeira execução"**.

### Se xeyes não funcionar

Instale o X11:

```bash
sudo apt-get update
sudo apt-get install -y x11-apps
xeyes  # Testar novamente
```

## Uso do Docker

### 1. Iniciar o Ambiente

O comando `make up` configura automaticamente as permissões do X11(`xhost`), constrói a imagem (se necessário) e inicia o container em segundo plano.

```bash
make up
```

### 2. Entrar no Container

Para acessar o terminal do container que já está rodando:

```bash
make attach
```

### 3. Parar o Ambiente

Para remover o container:
```bash
make down
```

## Dentro do Container

Dentro do container execute:
```bash
source install/setup.bash
```

### Ferramentas disponíveis

* **Terminator**: Terminal com suporte a múltiplas abas e divisão de tela.
```bash
terminator -u
```

* **Nano**: Editor de texto via terminal.
```bash
nano src/denso_robot_ros2/your_file.py
```

## Para rodar o ROS2 no DENSO

```bash
ros2 launch denso_robot_bringup denso_robot_bringup.launch.py model:=<robot_model> sim:=<boolean> basic_camera:=<boolean> ip_address:=<robot_ip_address>
```

- `model` (**obrigatório**) - o modelo do robô DENSO ("cobotta", "vs060", "vs050").
- `ip_address` (se `sim:=false`) - endereço IP do robô.
- `sim` (default: _true_) - se o robô está simulado (Gazebo) ou se um controlador RC8 está conectado
- `basic_camera` (default: _false_) - se o robô simulado (Gazebo) tem uma câmera anexada à sua Junta 6

Exemplo de execução:

```bash
ros2 launch denso_robot_bringup denso_robot_bringup.launch.py model:="vs050" sim:=true basic_camera:=true
```

Para mais informações, consulte:
- [slaveMode robot control](https://github.com/Curso-de-Robotica-e-IA/denso_robot_ros2/blob/vs050_descriptions_gz_fortress/README.md)

