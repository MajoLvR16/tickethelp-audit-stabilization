**Estructura de la Ficha Técnica del Software**

**1\. Identificación del Proyecto y Producto**

- **Nombre Oficial del Software:** Ticket-Help
- **Sigla del Software:** Ticket-Help.TH
- **Versión Actual:** 1.0
- **Fecha de Lanzamiento (entrega final):** 20 Noviembre de 2025
- **Integrantes del Equipo de Desarrollo:**
- Código: 1152249 Nombre: Andres Julian Ortiz Jaimes **Rol:** Product Owner
- Código: 1152256 Nombre: Anyela Jhohana Herrera Lobo **Rol:** Desarrollador Frontend

- Código: 1152265 Nombre: Laura Isabella Correa Nieto **Rol:** Desarrollador Backend
- Código: 1152268 Nombre: Maria Jose Lopez Reyes **Rol:** Desarrollador Backend
- Código: 1152269 Nombre: Daniela Alejandra Barreto Ibarra **Rol:** Desarrollador Frontend
- Código: 1152273 Nombre: Josue Daniel Perez Guerrero **Rol:** Desarrollador Backend
- Código: 1151943 Nombre: David Santiago Peñaranda Parada **Rol:** Desarrollador Frontend
- **Descripción Breve:**

El sistema Ticket-Help tiene como propósito principal gestionar, controlar y dar seguimiento completo al proceso de soporte técnico, desde la recepción del equipo por parte del cliente hasta la entrega final del producto reparado. Su objetivo es asegurar una atención organizada, transparente y eficiente para los clientes y para el personal técnico y administrativo.

En cuanto a su alcance funcional, el sistema permite:

**1\. Gestión del Cliente**

Verificar si el cliente está registrado.

Registrar nuevos clientes cuando sea necesario.

Notificar al cliente sobre el registro exitoso y los avances del ticket.

**2\. Registro y Administración de Tickets**

Registrar el problema reportado y crear un nuevo ticket.

Asignar el ticket a un técnico disponible.

Permitir visualizar la trazabilidad del ticket en todo momento.

**3\. Proceso Técnico de Reparación**

Recibir y revisar el ticket asignado.

Actualizar el estado del ticket y registrar tiempos para estadísticas.

Realizar la reparación del producto.

Solicitar aprobación para el cierre del ticket.

**4\. Validación y Cierre**

Aprobar o rechazar la reparación realizada.

Validar la reparación por parte del administrador.

Notificar al cliente sobre la finalización de la reparación.

Entregar el producto reparado al cliente.

**2\. Información Técnica y de Desarrollo**

- **Arquitectura:** _El sistema implementa una arquitectura cliente/servidor de 3 capas:_
- **_Frontend (Capa de presentación):_** _Desarrollado en React con Vite._
- **_Backend (Capa lógica):_** _API REST construida con Django + Django REST Framework._
- **_Base de datos (Capa de datos)_**_: PostgreSQL._

_El backend funciona como una API monolítica, no como microservicios._

- **Lenguaje de Programación Principal:**

**_Backend_**

_Lenguaje: Python_

_Framework principal: Django_

_Extensión para APIs: Django REST Framework_

**_Frontend_**

_Lenguaje: JavaScript_

_Framework/Librería: React_

_Herramienta de compilación: Vite_

- **Base de Datos:** _PostgreSQL_
- **Control de Versiones:** Git
- **Ruta del Código Fuente (Repositorio\_):_**

[_https://github.com/JulianOrtiz952/tickethelp-backend_](https://github.com/JulianOrtiz952/tickethelp-backend)

[_https://github.com/JulianOrtiz952/tickethelp-frontend_](https://github.com/JulianOrtiz952/tickethelp-frontend)

- **Herramientas y _Frameworks_ Clave:**

**Frontend**

React (Librería principal para la interfaz)

Vite (Herramienta de construcción)

Tailwind CSS (Estilos)

Axios (Consumo de API)

React Hook Form (Manejo de formularios)

**Backend**

Django (Framework principal)

Django REST Framework (Creación de API REST)

SimpleJWT (Autenticación mediante tokens)

Gunicorn (Servidor WSGI)

psycopg3 (Conector PostgreSQL)

django-environ (Manejo de variables de entorno)

CORS Headers (Control de acceso desde el frontend)

**Base de datos**

PostgreSQL

**Infraestructura**

Git (Control de versiones)

- **Estándares Aplicados:**

IEEE 830 – Especificación de requisitos de software.

ISO/IEC 25010 – Calidad del software.

Principios SOLID – Buenas prácticas de arquitectura y código.

RESTful API Principles – Diseño de interfaces de comunicación.

Convenciones PEP8 – Estilo de código Python.

- **Credenciales 1: Tecnico Usuario:** [**Jarba@soy.ufps.edu.co**](mailto:Jarba@soy.ufps.edu.co) **Clave: 123456789Pr@**
- **Credenciales 2: Cliente Usuario:** [**daniela@ufps.edu.co**](mailto:daniela@ufps.edu.co) **Clave: 1005028830**
- **Credenciales 3: Admin Base de datos:** [**daniela@ufps.edu.co**](mailto:daniela@ufps.edu.co) **Clave: 1091967730**

**3\. Entornos y Despliegue**

| **Entorno**            | **URL de acceso**                                                                                                                                                                            | **Credenciales**                                         | **Notas de Configuración**                                                                                        |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Producción**         | [**https://tickethelp-frontend.onrender.com/**](https://tickethelp-frontend.onrender.com/) **API:** [**https://tickethelp-backend.onrender.com/**](https://tickethelp-backend.onrender.com/) | **Se usan las credenciales de prueba (técnico/cliente)** | **Desplegado en Render; API y Frontend con variables de entorno, CORS y JWT configurados.**                       |
| ---                    | ---                                                                                                                                                                                          | ---                                                      | ---                                                                                                               |
| **Staging / Pruebas**  | **(No se creó un entorno staging separado)**                                                                                                                                                 | **—**                                                    | **Las pruebas funcionales y de integración se realizaron directamente sobre el entorno de producción de Render.** |
| ---                    | ---                                                                                                                                                                                          | ---                                                      | ---                                                                                                               |
| **Desarrollo (Local)** | **Frontend:** [**http://localhost:5173/**](http://localhost:5173/) **Backend:** [**http://localhost:8000/**](http://localhost:8000/)                                                         | **Credenciales locales iguales a las de producción**     | **Backend requiere entorno virtual y archivo .env; frontend requiere npm install y npm run dev.**                 |
| ---                    | ---                                                                                                                                                                                          | ---                                                      | ---                                                                                                               |

**4\. Requisitos Operacionales y Soporte**

- **Dependencias Críticas:**

_Conexión estable a la API REST.  
_

_Configuración correcta de CORS en backend.  
_

_Servicio de correo habilitado para notificaciones (SMTP)._

- **Requisitos del Cliente (Navegador/SO):**

_Navegadores soportados:  
_

- _Google Chrome (recomendado)  
  _
- _Mozilla Firefox  
  _
- _Microsoft Edge  
  _

_Sistema operativo mínimo: Windows 10 / Linux / macOS  
_

_Conexión a Internet estable._

- **Información de Contacto para Soporte:** Correos según integrantes del proyecto (UFPS).
- **Tipo de Licencia:** _Licencia académica para uso en el marco del proyecto universitario (no comercial)._
- **Registro de Software:** Proyecto registrado como entrega oficial del curso de **Análisis y Diseño de Sistemas – UFPS 2025**.

**5\. Documentación Relacionada**

- **Manual del Sistema:**[Copia de Manual del Sistema.docx](https://docs.google.com/document/d/1_mT2MAChzTG2QcxDBkGVSc7Uxl3zVmEl/edit?rtpof=true&tab=t.0)
- **Manual del Usuario:**[Manual del Usuario.docx](https://docs.google.com/document/d/1K-v43xc8pv5E_T7Z5rJ136gQgPoQAQAQ/edit)