import RPi.GPIO as GPIO # type: ignore
import time
import socketio

# Configurar el modo de numeración de los pines
GPIO.setmode(GPIO.BCM)

# Definir los pines conectados al receptor RF
D0 = 17  # Pin GPIO para D0
D1 = 27  # Pin GPIO para D1
D2 = 22  # Pin GPIO para D2
D3 = 23  # Pin GPIO para D3

# Configurar los pines como entradas con pull-down resistors
GPIO.setup(D0, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(D1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(D2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(D3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

estado_anterior = (0, 0, 0, 0)
time_stamp = time.time()

GPIO.add_event_detect(D0, GPIO.BOTH)
GPIO.add_event_detect(D1, GPIO.BOTH)
GPIO.add_event_detect(D2, GPIO.BOTH)
GPIO.add_event_detect(D3, GPIO.BOTH)

D0_val = 0
D1_val = 0
D2_val = 0
D3_val = 0

# Configurar el servidor Socket.IO
sio = socketio.Server()
app = socketio.WSGIApp(sio)

def leer_mando_rf():
    global estado_anterior
    
    # Leer el estado de los pines
    estado_actual = (
        GPIO.input(D0),
        GPIO.input(D1),
        GPIO.input(D2),
        GPIO.input(D3)
    )
    
    if estado_actual != estado_anterior:
        estado_anterior = estado_actual
        
        if estado_actual == (1, 1, 1, 1):
            print("Botón 8 presionado")
        elif estado_actual == (1, 1, 1, 0):
            print("Botón 7 presionado")
        elif estado_actual == (0, 1, 1, 0):
            print("Botón 6 presionado")
            # Incrementar heading 10
            sio.emit('increment_heading_large', {'value': 10})
        elif estado_actual == (0, 1, 0, 1):
            print("Botón 5 presionado")
            # Decrementar heading 10
            sio.emit('decrement_heading_large', {'value': 10})
        elif estado_actual == (0, 1, 0, 0):
            print("Botón 4 presionado")
            # Incrementar heading 1
            sio.emit('increment_heading', {'value': 1})
        elif estado_actual == (0, 0, 1, 1):
            print("Botón 3 presionado")
            # Decrementar heading 1
            sio.emit('decrement_heading', {'value': 1})
        elif estado_actual == (0, 0, 1, 0):
            print("Botón 2 presionado")
            # Desactivar autopilot
            sio.emit('deactivate_autopilot')
        elif estado_actual == (0, 0, 0, 1):
            print("Botón 1 presionado")
            # Activar autopilot
            sio.emit('activate_autopilot')

try:
    import eventlet
    import eventlet.wsgi
    eventlet.monkey_patch()
    eventlet.spawn_n(lambda: eventlet.wsgi.server(eventlet.listen(('', 5000)), app))
    
    while True:
        leer_mando_rf()
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Saliendo...")

finally:
    GPIO.cleanup()