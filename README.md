# API Pricut
> [!NOTE]
> Este proyecto aun está en desarrollo.

<div>
    <img src="/images/PricutBackendBanner.png">
</div>

## 1. Descripción del proyecto
El servicio que ofrece Pricut está relacionado con cortes computarizados de materiales, orientado principalmente a profesionales en áreas como la Ingeniería, el Diseño y la Arquitectura. El servicio se enfoca en ofrecer cortes precisos, con un énfasis en la rapidez, calidad y conveniencia, ya que entregan los materiales cortados directamente a la puerta de la casa o empresa de los clientes. Además, buscan una mejora continua en la variedad de materiales con los que trabajan y los servicios que proporcionan.

### 1.1. Características de los usuarios
En el sistema web de PRICUT, cada usuario tiene un conjunto específico de responsabilidades y permisos para garantizar el correcto funcionamiento de la plataforma y la mejor experiencia posible para el cliente.

- **Persona natural:** Profesionales independientes en campos como la Ingeniería, el Diseño y la Arquitectura. Sus necesidades de corte generalmente se centran en proyectos individuales o de pequeña escala, y pueden requerir orientación más detallada sobre materiales y técnicas de corte.
- **Empresa:** Compañías de diversos tamaños en sectores como la construcción, la fabricación y el diseño industrial. Estos usuarios generalmente poseen un alto nivel de conocimiento técnico y experiencia en el uso de servicios de corte. Sus necesidades suelen ser para proyectos de mayor escala o producción en serie, y pueden requerir funcionalidades adicionales como la gestión de múltiples usuarios o facturación empresarial.
- **Administradores:** Forman parte del personal interno de Pricut. Estos usuarios se encargan de la gestión y mantenimiento de la plataforma.

### 1.2. Requerimientos funcionales
- Registro de usuarios.
- Sistema de autenticación con JWT o redes sociales.
- Actualizar la información de perfil para usuarios.
- Eliminar cuenta.
- Restablecer contraseña.
- Cotizador inteligente.
- Lectura de archivos DXF y AI.
- Funcionalidades para administradores.
- Sistema de gestión de pedidos.
- Sistema de envío de correos electrónicos.
- Gestión de permisos de usuarios.

## 2. Tecnologías
<div>
    <img src="/images/TechnologiesBackendPricut.png">
</div>

## 3. Instalación del proyecto
> [!NOTE]
> Asegúrese que Python 3.12 y [Poetry](https://python-poetry.org/docs/#installation) esté instalado en su sistema operativo.

Primero debes seguir las siguientes instrucciones y dependiendo de que manera quieres realizar la instalación seguiras los pasos para instalar el proyecto de manera manual o utilizando Docker.

- **Clonar repositorio:** Para clonar este repositorio ejecuta los siguientes comandos.
    
    ```bash
    git clone https://github.com/viavervit-dev/api-pricut-monolitico.git
    cd api-pricut-monolitico
    ```
    
- **Activar entorno virtual:** Activamos un entorno virtual con el siguiente comando, en este entorno se instalarán todas las dependencias de este proyecto.
    
    ```bash
    eval $(poetry env activate)
    ```

- **Configurar variables de entorno:** Crea un archivo con el nombre _.env_ dentro del directorio _api_pricut_. En este archivo se definiran todas las variables de entorno de este proyecto. Las variables que se deben configurar son las siguientes.

    ```.env
    # DJANGO
    KEY_DJANGO=<value>

    # USERS ADMIN
    ADMIN_DEV_EMAIL=admin-dev@email.com
    ADMIN_DEV_PASSWORD=admin123456789
    ADMIN_PROD_EMAIL=admin-prod@email.com
    ADMIN_PROD_PASSWORD=admin123456789
    ADMIN_PROD_FIRSTNAME=admin
    ADMIN_PROD_LASTNAME=admin

    # URLS and Hosts
    BACKEND_HOST="172.29.178.209"
    BACKEND_URL="http://172.29.178.209:8000"
    ENVIRONMENT="development"
    FRONTEND_HOST="localhost"
    FRONTEND_URL="https://localhost"
    FRONTEND_HOST_LOCAL="localhost"
    FRONTEND_LOCAL_URL="http://localhost:3000"
    ```

    El valor de la variable `KEY_DJANGO` lo puedes obtener ejecutando los siguientes comandos. Primero iniciamos el intérprete de Python.

    ```bash
    python3
    ```

    El siguiente comando te va retornar el valor de `KEY_DJANGO` que deberas copiar en el archivo _.env_.

    ```bash
    from django.core.management.utils import get_random_secret_key; print(get_random_secret_key()); exit()
    ```

    Para el envío de mensajes a través de correo electrónico tienes que tener una contraseña de aplicación que permita a la API autenticarse y poder utilizar el servicio de mensajería por correo electrónico.

### 3.1. Instalación manual

- **Paso 1 (instalar dependencias):** Para instalar las teconologias y paquetes que usa el proyecto usa el siguiente comando. Asegurate estar en el directotio raíz.
    
    ```bash
    poetry install
    ```
    
- **Paso 2 (realizar migraciones):** Las migraciones son archivos que registran y aplican cambios en la estructura de la base de datos, como crear o modificar tablas y campos, asegurando que la base de datos esté sincronizada con los modelos definidos en el código. Migramos los modelos del proyecto con el siguiente comando.
    
    ```bash
    python3 api_pricut/manage.py migrate --settings=settings.environments.development
    ```

- **Paso 3 (configurar grupo de usuarios):** Un grupo de usuarios se refiere a una entidad dentro de un sistema o aplicación que agrupa a varios usuarios bajo un mismo conjunto de permisos, roles o privilegios. Esto se utiliza para simplificar la gestión de acceso y permisos en sistemas donde hay múltiples usuarios. Para crear los grupos configurados paraeste proyecto ejecuta el siguiente comando.
    
    ```bash
    python3 api_pricut/manage.py configureusergroups --settings=settings.environments.development
    ```

- **Paso 4 (cargar la información estática):** La información estática está estrechamente vinculada a los servicios que ofrece Pricut y será visible para el usuario final en la web. Por esta razón, es fundamental gestionar esta información desde un panel de administración para garantizar que el contenido de la web se mantenga siempre actualizado. Este comando se encarga de agregar toda la información estática inicial del proyecto en la base de datos.
    
    ```bash
    python3 api_pricut/manage.py loadstaticinfo --settings=settings.environments.development
    ```

- **Paso 5 (iniciar el servidor):** Para iniciar el servidor de manera local ejecuta el siguiente comando.
    
    ```bash
    python3 api_pricut/manage.py runserver --settings=settings.environments.development
    ```
    
### 3.2. Instalación con Docker

- **Paso 1 (Construir imagen):** para construir la imagen del contenedor de este pryecto debes ejecutar el siguiente comando.
    
    ```bash
    docker build -t api_pricut .
    ```
    
- **Paso 2 (Correr imagen):** para iniciar el contenedor de este pryecto debes ejecutar el siguiente comando.
    
    ```bash
    docker run -e ENVIRONMENT=development -p 8000:8000 api_pricut
    ```
    
De esta manera podrás usar todas las funcionalidades que este proyecto tiene para ofrecer. Es importante que hayas seguido todos los pasos explicados en el orden establecido.

## 4. Comandos disponibles
Este proyecto incluye algunos comandos personalizados de Django que puedes utilizar para facilitar el desarrollo y la administración. A continuación se describe cada uno de los comandos y su funcionalidad.

### 4.1. Configurar grupos de usuarios
Este comando configura los grupos de usuarios predefinidos en el sistema, asignando los permisos necesarios a cada uno. Facilita la administración de roles y permisos en la plataforma.

    ```bash
    python3 api_pricut/manage.py configureusergroups --settings=settings.environments.development
    ```

### 4.2. Borrar JWT expirados en la base de datos
Este comando elimina de la base de datos todos los JSON Web Tokens que hayan expirado. Es útil para mantener la base de datos limpia y optimizar su rendimiento.

```bash
python3 api_pricut/manage.py flushexpiredjwt --settings=settings.environments.development
```

### 4.3. Cargar la información estática
La información estática está estrechamente vinculada a los servicios que ofrece Pricut y será visible para el usuario final en la web. Por esta razón, es fundamental gestionar esta información desde un panel de administración para garantizar que el contenido de la web se mantenga siempre actualizado. Este comando se encarga de agregar toda la información estática inicial del proyecto en la base de datos.
    
```bash
python3 api_pricut/manage.py loadstaticinfo --settings=settings.environments.development
```

### 4.4. Crear usuario administrador
Este comando crea un usuario administrador dependiendo del entorno en el que se ejecute el proyecto (DESARROLLO o PRODUCCIÓN), destacando las siguientes diferencias:

- **Usuario administrador de desarrollo:** Este usuario está diseñado exclusivamente para el entorno de desarrollo. Su principal objetivo es facilitar el acceso al panel de administración de Django durante las fases de pruebas y construcción de la aplicación. No está pensado para un entorno en el que la aplicación esté en funcionamiento público.

- **Usuario administrador de producción:** Este usuario está orientado al trabajo posterior al despliegue de la aplicación en un entorno de producción. Proporciona acceso al panel de administración de la aplicación, desde donde se pueden realizar configuraciones, gestionar datos y ejecutar acciones necesarias para el correcto funcionamiento y mantenimiento del sistema en un entorno en vivo.

    
```bash
python3 api_pricut/manage.py createadmin --settings=settings.environments.development
```


## 5. Tests
Para correr las pruebas del proyecto debes ejecutar el siguiente comando.

```bash
pytest
```

## 6. Contributores
Si está interesado en contribuir a este proyecto, consulte nuestra guía [CONTRIBUTING](CONTRIBUTING.md) para obtener información sobre cómo comenzar. Proporciona pautas sobre cómo configurar su entorno de desarrollo, proponer cambios y más. ¡Esperamos sus contribuciones!

## 7. Colaboradores
A continuación se presentan a las personas que están aportando al desarrollo de este proyecto.

| Nombre | Enlaces | Roles |
|----------|:--------:|:--------:|
| Carlos Andres Aguirre Ariza | [GitHub](https://github.com/The-Asintota) - [LinkedIn](https://www.linkedin.com/in/carlosaguirredev/) | Backend |
