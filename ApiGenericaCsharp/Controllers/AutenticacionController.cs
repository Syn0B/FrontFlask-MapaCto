// AutenticacionController.cs
// Controlador genérico que autentica usuarios en cualquier tabla de base de datos
// y genera tokens JWT válidos si las credenciales son correctas.
//
// ---------------------------------------------------------
// CARACTERÍSTICAS
// ---------------------------------------------------------
// - Compatible con cualquier tabla y campos personalizados
// - Usa BCrypt para comparar contraseñas encriptadas
// - Genera tokens JWT configurables desde appsettings.json
// - No depende del tipo de base de datos (SQL Server, PostgreSQL, etc.)
// - Sigue principios SOLID: SRP, DIP y OCP
//
// ---------------------------------------------------------
// IMPORTACIONES NECESARIAS
// ---------------------------------------------------------
using Microsoft.AspNetCore.Authorization;            // Para [AllowAnonymous]
using Microsoft.AspNetCore.Mvc;                      // Para el controlador y las acciones
using Microsoft.Extensions.Options;                  // Para inyectar configuraciones (IOptions)
using Microsoft.IdentityModel.Tokens;                // Para firmar y generar el token JWT
using System.IdentityModel.Tokens.Jwt;               // Para manipular JWT
using System.Security.Claims;                        // Para definir los claims dentro del token
using System.Text;                                   // Para codificar la clave secreta
using ApiGenericaCsharp.Modelos;                          // Para la clase ConfiguracionJwt
using ApiGenericaCsharp.Servicios.Abstracciones;           // Para la interfaz IServicioCrud

namespace ApiGenericaCsharp.Controllers
{
    /// <summary>
    /// Controlador que permite autenticar un usuario contra cualquier tabla
    /// y devuelve un token JWT si las credenciales son válidas.
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    public class AutenticacionController : ControllerBase
    {
        private readonly ConfiguracionJwt _configuracionJwt;   // Configuración JWT cargada desde appsettings
        private readonly IServicioCrud _servicioCrud;          // Servicio genérico para verificar contraseñas

        // ---------------------------------------------------------
        // CONSTRUCTOR
        // ---------------------------------------------------------
        public AutenticacionController(
            IOptions<ConfiguracionJwt> opcionesJwt, 
            IServicioCrud servicioCrud)
        {
            _configuracionJwt = opcionesJwt.Value;
            _servicioCrud = servicioCrud;
        }

        // ---------------------------------------------------------
        // POST: /api/autenticacion/token
        // Descripción:
        //   - Verifica credenciales en la tabla indicada (con hash BCrypt)
        //   - Si son válidas, genera un token JWT con los datos básicos.
        // ---------------------------------------------------------
        [HttpPost("token")]
        public async Task<IActionResult> GenerarToken([FromBody] CredencialesGenericas credenciales)
        {
            // -----------------------------------------------------
            // VALIDACIONES BÁSICAS DEL BODY
            // -----------------------------------------------------
            if (string.IsNullOrWhiteSpace(credenciales.Tabla) ||
                string.IsNullOrWhiteSpace(credenciales.CampoUsuario) ||
                string.IsNullOrWhiteSpace(credenciales.CampoContrasena) ||
                string.IsNullOrWhiteSpace(credenciales.Usuario) ||
                string.IsNullOrWhiteSpace(credenciales.Contrasena))
            {
                return BadRequest(new
                {
                    estado = 400,
                    mensaje = "Debe enviar tabla, campos y credenciales completas.",
                    ejemplo = new
                    {
                        tabla = "TablaDeUsuarios",
                        campoUsuario = "ejemploCampoUsuario",
                        campoContrasena = "ejemploCampoContrasena",
                        usuario = "ejemplo@correo.com",
                        contrasena = "admin123"
                    }
                });
            }

            // -----------------------------------------------------
            // FASE 1: VERIFICACIÓN DE CREDENCIALES ENCRIPTADAS
            // -----------------------------------------------------
            // Se delega la comparación de contraseñas al ServicioCrud,
            // el cual implementa la lógica de verificación usando BCrypt.
            var (codigo, mensaje) = await _servicioCrud.VerificarContrasenaAsync(
                credenciales.Tabla,
                null, // Esquema opcional
                credenciales.CampoUsuario,
                credenciales.CampoContrasena,
                credenciales.Usuario,
                credenciales.Contrasena
            );

            // -----------------------------------------------------
            // FASE 2: EVALUACIÓN DEL RESULTADO DE VERIFICACIÓN
            // -----------------------------------------------------
            if (codigo == 404)
                return NotFound(new { estado = 404, mensaje = "Usuario no encontrado." });

            if (codigo == 401)
                return Unauthorized(new { estado = 401, mensaje = "Contraseña incorrecta." });

            if (codigo != 200)
                return StatusCode(500, new { estado = 500, mensaje = "Error interno durante la verificación.", detalle = mensaje });

            // -----------------------------------------------------
            // FASE 3: GENERACIÓN DEL TOKEN JWT
            // -----------------------------------------------------
            // Si la verificación fue exitosa, se crea un token JWT con los datos básicos del usuario.
            var claims = new[]
            {
                new Claim(ClaimTypes.Name, credenciales.Usuario),       // Nombre de usuario
                new Claim("tabla", credenciales.Tabla),                 // Tabla usada para autenticación
                new Claim("campoUsuario", credenciales.CampoUsuario)    // Campo de usuario utilizado
            };

            // Clave secreta para firmar el token (obtenida desde appsettings.json)
            var clave = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_configuracionJwt.Key));

            // Se especifica el algoritmo de firma HMAC-SHA256
            var credencialesFirma = new SigningCredentials(clave, SecurityAlgorithms.HmacSha256);

            // Duración configurable del token (en minutos)
            var duracion = _configuracionJwt.DuracionMinutos > 0 ? _configuracionJwt.DuracionMinutos : 60;

            // Construcción del token con sus parámetros principales
            var token = new JwtSecurityToken(
                issuer: _configuracionJwt.Issuer,       // Emisor del token
                audience: _configuracionJwt.Audience,   // Público autorizado
                claims: claims,                         // Datos del usuario dentro del token
                expires: DateTime.UtcNow.AddMinutes(duracion), // Fecha de expiración
                signingCredentials: credencialesFirma   // Firma digital
            );

            // Serializa el token a formato string para enviarlo al cliente
            string tokenGenerado = new JwtSecurityTokenHandler().WriteToken(token);

            // -----------------------------------------------------
            // FASE 4: RESPUESTA FINAL
            // -----------------------------------------------------
            return Ok(new
            {
                estado = 200,
                mensaje = "Autenticación exitosa.",
                usuario = credenciales.Usuario,
                token = tokenGenerado,
                expiracion = token.ValidTo
            });
        }

        // ---------------------------------------------------------
        // POST: /api/autenticacion/restablecer-contrasena
        // Descripción:
        //   - Permite a un usuario que olvidó su contraseña restablecerla
        //     proporcionando su usuario + email (ambos deben coincidir en BD).
        //   - La nueva contraseña se encripta con BCrypt antes de guardarse
        //     (gracias al parametro camposEncriptar del ServicioCrud).
        //   - Es [AllowAnonymous] porque el usuario por definición no tiene
        //     sesión activa: olvidó su contraseña y no puede hacer login.
        // ---------------------------------------------------------
        [AllowAnonymous]
        [HttpPost("restablecer-contrasena")]
        public async Task<IActionResult> RestablecerContrasena([FromBody] RestablecerContrasenaDto datos)
        {
            // -----------------------------------------------------
            // VALIDACIONES BÁSICAS DEL BODY
            // -----------------------------------------------------
            if (datos == null ||
                string.IsNullOrWhiteSpace(datos.Tabla) ||
                string.IsNullOrWhiteSpace(datos.CampoUsuario) ||
                string.IsNullOrWhiteSpace(datos.CampoEmail) ||
                string.IsNullOrWhiteSpace(datos.CampoContrasena) ||
                string.IsNullOrWhiteSpace(datos.Usuario) ||
                string.IsNullOrWhiteSpace(datos.Email) ||
                string.IsNullOrWhiteSpace(datos.NuevaContrasena))
            {
                return BadRequest(new
                {
                    estado = 400,
                    mensaje = "Debe enviar tabla, campos, usuario, email y nueva contrasena."
                });
            }

            try
            {
                // -------------------------------------------------
                // FASE 1: Buscar el usuario por su campo de usuario.
                // -------------------------------------------------
                var filas = await _servicioCrud.ObtenerPorClaveAsync(
                    datos.Tabla,
                    null, // Esquema por defecto
                    datos.CampoUsuario,
                    datos.Usuario
                );

                if (filas.Count == 0)
                {
                    return NotFound(new { estado = 404, mensaje = "Usuario no encontrado." });
                }

                // -------------------------------------------------
                // FASE 2: Verificar que el email registrado coincide
                // con el email enviado. Comparación case-insensitive
                // porque los emails no son sensibles a mayúsculas.
                // -------------------------------------------------
                var registro = filas[0];
                string? emailRegistrado = null;

                if (registro.TryGetValue(datos.CampoEmail, out var valorEmail) && valorEmail != null)
                {
                    emailRegistrado = valorEmail.ToString();
                }

                if (string.IsNullOrWhiteSpace(emailRegistrado) ||
                    !string.Equals(emailRegistrado.Trim(), datos.Email.Trim(), System.StringComparison.OrdinalIgnoreCase))
                {
                    return Unauthorized(new
                    {
                        estado = 401,
                        mensaje = "El email no coincide con el usuario indicado."
                    });
                }

                // -------------------------------------------------
                // FASE 3: Actualizar la contraseña con encriptación
                // BCrypt (via camposEncriptar). El servicio se encarga
                // de hashear antes de persistir.
                // -------------------------------------------------
                var datosActualizar = new Dictionary<string, object?>
                {
                    [datos.CampoContrasena] = datos.NuevaContrasena
                };

                int filasAfectadas = await _servicioCrud.ActualizarAsync(
                    datos.Tabla,
                    null,
                    datos.CampoUsuario,
                    datos.Usuario,
                    datosActualizar,
                    datos.CampoContrasena // camposEncriptar: la API lo hashea con BCrypt
                );

                if (filasAfectadas == 0)
                {
                    return StatusCode(500, new
                    {
                        estado = 500,
                        mensaje = "No se pudo restablecer la contrasena."
                    });
                }

                return Ok(new
                {
                    estado = 200,
                    mensaje = "Contrasena restablecida exitosamente.",
                    usuario = datos.Usuario
                });
            }
            catch (System.Exception excepcion)
            {
                return StatusCode(500, new
                {
                    estado = 500,
                    mensaje = "Error interno al restablecer la contrasena.",
                    detalle = excepcion.Message
                });
            }
        }
    }

    // ---------------------------------------------------------
    // CLASE AUXILIAR: CredencialesGenericas
    // ---------------------------------------------------------
    // Representa el cuerpo del POST enviado por el cliente.
    // Incluye toda la información necesaria para validar un usuario
    // contra cualquier tabla de la base de datos.
    public class CredencialesGenericas
    {
        // Nombre de la tabla que contiene los usuarios (por ejemplo: "usuario", "vendedor", "cliente")
        public string Tabla { get; set; } = string.Empty;

        // Nombre del campo que almacena el identificador de usuario (por ejemplo: "email", "nombre", "login")
        public string CampoUsuario { get; set; } = string.Empty;

        // Nombre del campo que almacena la contraseña (por ejemplo: "clave", "password", "contrasena")
        public string CampoContrasena { get; set; } = string.Empty;

        // Valor del usuario que intenta autenticarse
        public string Usuario { get; set; } = string.Empty;

        // Contraseña enviada por el usuario (texto plano para comparar con hash en BD)
        public string Contrasena { get; set; } = string.Empty;
    }

    // ---------------------------------------------------------
    // CLASE AUXILIAR: RestablecerContrasenaDto
    // ---------------------------------------------------------
    // Representa el cuerpo del POST para restablecer contraseña.
    // El usuario olvidó su contraseña: se identifica con usuario + email,
    // y proporciona una nueva contraseña que será encriptada con BCrypt.
    public class RestablecerContrasenaDto
    {
        // Tabla de usuarios (ej: "usuario")
        public string Tabla { get; set; } = string.Empty;

        // Columna que identifica al usuario (ej: "username")
        public string CampoUsuario { get; set; } = string.Empty;

        // Columna que almacena el email del usuario (ej: "email")
        public string CampoEmail { get; set; } = string.Empty;

        // Columna que almacena la contraseña (ej: "password")
        public string CampoContrasena { get; set; } = string.Empty;

        // Valor del usuario que olvidó su contraseña
        public string Usuario { get; set; } = string.Empty;

        // Email que debe coincidir con el registrado para validar identidad
        public string Email { get; set; } = string.Empty;

        // Nueva contraseña en texto plano (se hashea antes de guardar)
        public string NuevaContrasena { get; set; } = string.Empty;
    }
}

