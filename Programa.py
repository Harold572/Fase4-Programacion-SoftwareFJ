from abc import ABC, abstractmethod
from datetime import datetime

# --- 1. EXCEPCIONES PERSONALIZADAS (Para controlar errores sin que el programa se cierre) ---
class ErrorSistemaFJ(Exception):
    pass

class DatoInvalidoError(ErrorSistemaFJ):
    pass

class ServicioNoDisponibleError(ErrorSistemaFJ):
    pass

class ReservaError(ErrorSistemaFJ):
    pass

# --- 2. ARCHIVO DE LOGS (Guarda un historial de errores en un bloc de notas automático) ---
class Logger:
    def __init__(self, archivo="sistema_fj.log"):
        self.archivo = archivo

    def registrar(self, nivel: str, mensaje: str):
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.archivo, "a", encoding="utf-8") as f:
            f.write(f"[{fecha}] [{nivel}] {mensaje}\n")

# --- 3. CLASES DEL SISTEMA (POO: Abstracción, Herencia, Polimorfismo y Encapsulación) ---
class EntidadSistema(ABC):
    def __init__(self, id_entidad: str):
        if not id_entidad.strip():
            raise DatoInvalidoError("El ID no puede estar vacío.")
        self._id = id_entidad

    @property
    def id(self):
        return self._id

    @abstractmethod
    def obtener_resumen(self) -> str:
        pass

class Cliente(EntidadSistema):
    def __init__(self, id_cliente: str, nombre: str, correo: str):
        super().__init__(id_cliente)
        if len(nombre.strip()) < 3:
            raise DatoInvalidoError("Nombre muy corto.")
        if "@" not in correo:
            raise DatoInvalidoError(f"Correo inválido: {correo}")
        self._nombre = nombre
        self._correo = correo

    @property
    def nombre(self):
        return self._nombre

    def obtener_resumen(self) -> str:
        return f"Cliente {self.id}: {self._nombre} ({self._correo})"

class Servicio(EntidadSistema, ABC):
    def __init__(self, id_servicio: str, nombre: str, tarifa: float):
        super().__init__(id_servicio)
        if tarifa <= 0:
            raise DatoInvalidoError("La tarifa debe ser mayor a cero.")
        self._nombre = nombre
        self._tarifa = tarifa
        self.disponible = True

    @abstractmethod
    def validar_horas(self, horas: int):
        pass

    # Método sobrecargado (permite calcular con o sin descuento/impuesto)
    def calcular_costo(self, horas: int, descuento: float = 0.0, iva: float = 0.19) -> float:
        self.validar_horas(horas)
        subtotal = (self._tarifa * horas) * (1 - descuento)
        return round(subtotal * (1 + iva), 2)

    def obtener_resumen(self) -> str:
        return f"Servicio {self.id}: {self._nombre} (${self._tarifa}/h)"

# Tres servicios especializados (Herencia y Polimorfismo)
class ReservaSala(Servicio):
    def validar_horas(self, horas: int):
        if horas < 1 or horas > 12:
            raise DatoInvalidoError("Las salas se reservan entre 1 y 12 horas.")

class AlquilerEquipo(Servicio):
    def validar_horas(self, horas: int):
        if horas < 2:
            raise DatoInvalidoError("Los equipos se alquilan mínimo por 2 horas.")

class AsesoriaEspecializada(Servicio):
    def validar_horas(self, horas: int):
        if horas <= 0:
            raise DatoInvalidoError("La asesoría debe durar mínimo 1 hora.")

class Reserva(EntidadSistema):
    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, horas: int):
        super().__init__(id_reserva)
        self.cliente = cliente
        self.servicio = servicio
        self.horas = horas
        self.estado = "PENDIENTE"
        self.total = 0.0

    def confirmar(self, descuento: float = 0.0):
        try:
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio {self.servicio.id} ya está ocupado.")
            self.total = self.servicio.calcular_costo(self.horas, descuento)
        except Exception as e:
            # Encadenamiento de excepciones
            raise ReservaError(f"Fallo al procesar reserva {self.id}") from e
        else:
            self.servicio.disponible = False
            self.estado = "CONFIRMADA"

    def cancelar(self):
        self.estado = "CANCELADA"
        self.servicio.disponible = True

    def obtener_resumen(self) -> str:
        return f"Reserva {self.id} | {self.cliente.nombre} | {self.servicio._nombre} | Total: ${self.total} | {self.estado}"

# --- 4. SIMULACIÓN DE 10 OPERACIONES ---
log = Logger()
clientes = []
servicios = []
reservas = []

print("=== INICIANDO PRUEBAS DE SOFTWARE FJ ===\n")

# Operación 1 y 2: Crear clientes válidos
c1 = Cliente("C01", "Ana Gómez", "ana@gmail.com")
c2 = Cliente("C02", "Luis Pérez", "luis@gmail.com")
clientes.extend([c1, c2])
log.registrar("INFO", f"Registrado: {c1.obtener_resumen()}")
print("1 y 2. [OK] Clientes creados correctamente.")

# Operación 3: Crear cliente inválido (error controlado)
try:
    c_malo = Cliente("C03", "Pedro", "correo_sin_arroba.com")
except DatoInvalidoError as e:
    log.registrar("ERROR", str(e))
    print(f"3. [ERROR CONTROLADO] {e}")

# Operación 4, 5 y 6: Crear los 3 tipos de servicios
sala = ReservaSala("S01", "Sala Ejecutiva", 50000)
equipo = AlquilerEquipo("E01", "Portátil Gamer", 25000)
asesoria = AsesoriaEspecializada("A01", "Asesoría Python", 80000)
servicios.extend([sala, equipo, asesoria])
print("4, 5 y 6. [OK] Sala, Equipo y Asesoría creados.")

# Operación 7: Crear servicio con precio negativo (error controlado)
try:
    sala_mala = ReservaSala("S02", "Sala Error", -10000)
except DatoInvalidoError as e:
    log.registrar("ERROR", str(e))
    print(f"7. [ERROR CONTROLADO] {e}")

# Operación 8: Reserva exitosa con 10% de descuento
try:
    r1 = Reserva("R01", c1, sala, 3)
    r1.confirmar(descuento=0.10)
    reservas.append(r1)
    log.registrar("INFO", r1.obtener_resumen())
    print(f"8. [OK] {r1.obtener_resumen()}")
except ReservaError as e:
    log.registrar("ERROR", str(e))

# Operación 9: Intentar reservar la misma sala ocupada (error controlado)
try:
    r2 = Reserva("R02", c2, sala, 2)
    r2.confirmar()
except ReservaError as e:
    log.registrar("ERROR", f"{e} -> Causa: {e.__cause__}")
    print(f"9. [ERROR CONTROLADO] {e} -> Causa: {e.__cause__}")

# Operación 10: Intentar alquilar equipo por 1 hora (mínimo son 2 horas)
try:
    r3 = Reserva("R03", c2, equipo, 1)
    r3.confirmar()
except ReservaError as e:
    log.registrar("ERROR", f"{e} -> Causa: {e.__cause__}")
    print(f"10. [ERROR CONTROLADO] {e} -> Causa: {e.__cause__}")
finally:
    print("\n=== PROGRAMA TERMINADO SIN CAERSE ===")
