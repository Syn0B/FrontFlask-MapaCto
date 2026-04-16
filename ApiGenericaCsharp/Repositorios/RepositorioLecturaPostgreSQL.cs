// --------------------------------------------------------------
// Archivo: RepositorioLecturaPostgreSQL.cs (VERSIÓN CON SOPORTE TIMESTAMP)
// Ruta: ApiGenericaCsharp/Repositorios/RepositorioLecturaPostgreSQL.cs
// Propósito: Implementar IRepositorioLecturaTabla para PostgreSQL con detección de tipos
// --------------------------------------------------------------

using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
using Npgsql;
using NpgsqlTypes;
using ApiGenericaCsharp.Repositorios.Abstracciones;
using ApiGenericaCsharp.Servicios.Abstracciones;
using ApiGenericaCsharp.Servicios.Utilidades;

namespace ApiGenericaCsharp.Repositorios
{
    /// <summary>
    /// Implementación específica para PostgreSQL que resuelve problemas de incompatibilidad de tipos.
    /// 
    /// PROBLEMAS RESUELTOS:
    /// 1. Error "42883: el operador no existe: integer = text"
    /// 2. Error "42804: column 'fecha' is of type date but expression is of type text"
    /// 3. Búsquedas en columnas TIMESTAMP usando solo fecha (sin hora)
    /// </summary>
    public sealed class RepositorioLecturaPostgreSQL : IRepositorioLecturaTabla
    {
        private readonly IProveedorConexion _proveedorConexion;

        public RepositorioLecturaPostgreSQL(IProveedorConexion proveedorConexion)
        {
            _proveedorConexion = proveedorConexion ?? throw new ArgumentNullException(nameof(proveedorConexion));
        }

        /// <summary>
        /// Detecta el tipo de una columna consultando information_schema.
        /// </summary>
        private async Task<NpgsqlDbType?> DetectarTipoColumnaAsync(string nombreTabla, string esquema, string nombreColumna)
        {
            string sql = @"
                SELECT data_type, udt_name 
                FROM information_schema.columns 
                WHERE table_schema = @esquema 
                AND table_name = @tabla 
                AND column_name = @columna";

            try
            {
                string cadena = _proveedorConexion.ObtenerCadenaConexion();
                await using var conexion = new NpgsqlConnection(cadena);
                await conexion.OpenAsync();

                await using var comando = new NpgsqlCommand(sql, conexion);
                comando.Parameters.AddWithValue("esquema", esquema);
                comando.Parameters.AddWithValue("tabla", nombreTabla);
                comando.Parameters.AddWithValue("columna", nombreColumna);

                await using var lector = await comando.ExecuteReaderAsync();
                if (await lector.ReadAsync())
                {
                    string dataType = lector.GetString(0);
                    string udtName = lector.GetString(1);
                    return MapearTipoPostgreSQL(dataType, udtName);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Advertencia: No se pudo detectar tipo de columna {nombreColumna}: {ex.Message}");
            }

            return null;
        }

        /// <summary>
        /// Mapea tipos de PostgreSQL a NpgsqlDbType.
        /// </summary>
        private NpgsqlDbType? MapearTipoPostgreSQL(string dataType, string udtName)
        {
            return dataType.ToLower() switch
            {
                "integer" or "int4" => NpgsqlDbType.Integer,
                "bigint" or "int8" => NpgsqlDbType.Bigint,
                "smallint" or "int2" => NpgsqlDbType.Smallint,
                "numeric" or "decimal" => NpgsqlDbType.Numeric,
                "real" or "float4" => NpgsqlDbType.Real,
                "double precision" or "float8" => NpgsqlDbType.Double,
                "character varying" or "varchar" => NpgsqlDbType.Varchar,
                "character" or "char" => NpgsqlDbType.Char,
                "text" => NpgsqlDbType.Text,
                "boolean" or "bool" => NpgsqlDbType.Boolean,
                "uuid" => NpgsqlDbType.Uuid,
                "timestamp without time zone" => NpgsqlDbType.Timestamp,
                "timestamp with time zone" => NpgsqlDbType.TimestampTz,
                "date" => NpgsqlDbType.Date,
                "time" => NpgsqlDbType.Time,
                "json" => NpgsqlDbType.Json,
                "jsonb" => NpgsqlDbType.Jsonb,
                _ => null
            };
        }

        /// <summary>
        /// Convierte un valor string al tipo apropiado según NpgsqlDbType detectado.
        /// </summary>
        private object ConvertirValor(string valor, NpgsqlDbType? tipoDestino)
        {
            if (tipoDestino == null) return valor;

            try
            {
                return tipoDestino switch
                {
                    NpgsqlDbType.Integer => int.Parse(valor),
                    NpgsqlDbType.Bigint => long.Parse(valor),
                    NpgsqlDbType.Smallint => short.Parse(valor),
                    NpgsqlDbType.Numeric => decimal.Parse(valor),
                    NpgsqlDbType.Real => float.Parse(valor),
                    NpgsqlDbType.Double => double.Parse(valor),
                    NpgsqlDbType.Boolean => bool.Parse(valor),
                    NpgsqlDbType.Uuid => Guid.Parse(valor),
                    NpgsqlDbType.Timestamp => DateTime.Parse(valor),
                    NpgsqlDbType.TimestampTz => DateTime.Parse(valor),
                    NpgsqlDbType.Date => ExtraerSoloFecha(valor),
                    NpgsqlDbType.Time => TimeOnly.Parse(valor),
                    NpgsqlDbType.Varchar => valor,
                    NpgsqlDbType.Char => valor,
                    NpgsqlDbType.Text => valor,
                    NpgsqlDbType.Json => valor,
                    NpgsqlDbType.Jsonb => valor,
                    _ => valor
                };
            }
            catch
            {
                return valor;
            }
        }

        /// <summary>
        /// Extrae solo la fecha de un string.
        /// </summary>
        private DateOnly ExtraerSoloFecha(string valor)
        {
            if (DateTime.TryParse(valor, out DateTime fechaCompleta))
                return DateOnly.FromDateTime(fechaCompleta);
            
            if (DateOnly.TryParse(valor, out DateOnly soloFecha))
                return soloFecha;
            
            throw new FormatException($"No se pudo convertir '{valor}' a fecha.");
        }

        /// <summary>
        /// Detecta si un valor parece ser una fecha sin hora (YYYY-MM-DD).
        /// </summary>
        private bool EsFechaSinHora(string valor)
        {
            return valor.Length == 10 && 
                   valor.Count(c => c == '-') == 2 &&
                   !valor.Contains("T") && 
                   !valor.Contains(":");
        }

        public async Task<IReadOnlyList<Dictionary<string, object?>>> ObtenerFilasAsync(
            string nombreTabla,
            string? esquema,
            int? limite)
        {
            if (string.IsNullOrWhiteSpace(nombreTabla))
                throw new ArgumentException("El nombre de la tabla no puede estar vacío.", nameof(nombreTabla));

            string esquemaFinal = string.IsNullOrWhiteSpace(esquema) ? "public" : esquema.Trim();
            int limiteFinal = limite ?? 1000;

            string sql = $"SELECT * FROM \"{esquemaFinal}\".\"{nombreTabla}\" LIMIT @limite";
            var filas = new List<Dictionary<string, object?>>();

            try
            {
                string cadena = _proveedorConexion.ObtenerCadenaConexion();

                await using var conexion = new NpgsqlConnection(cadena);
                await conexion.OpenAsync();

                await using var comando = new NpgsqlCommand(sql, conexion);
                comando.Parameters.AddWithValue("limite", limiteFinal);

                await using var lector = await comando.ExecuteReaderAsync();
                while (await lector.ReadAsync())
                {
                    var fila = new Dictionary<string, object?>();
                    for (int i = 0; i < lector.FieldCount; i++)
                    {
                        string nombreColumna = lector.GetName(i);
                        object? valor = lector.IsDBNull(i) ? null : lector.GetValue(i);
                        fila[nombreColumna] = valor;
                    }
                    filas.Add(fila);
                }
            }
            catch (NpgsqlException ex)
            {
                throw new InvalidOperationException(
                    $"Error PostgreSQL al consultar '{esquemaFinal}.{nombreTabla}': {ex.Message}", ex);
            }

            return filas;
        }

        public async Task<IReadOnlyList<Dictionary<string, object?>>> ObtenerPorClaveAsync(
            string nombreTabla,
            string? esquema,
            string nombreClave,
            string valor)
        {
            if (string.IsNullOrWhiteSpace(nombreTabla))
                throw new ArgumentException("El nombre de la tabla no puede estar vacío.", nameof(nombreTabla));
            if (string.IsNullOrWhiteSpace(nombreClave))
                throw new ArgumentException("El nombre de la clave no puede estar vacío.", nameof(nombreClave));
            if (string.IsNullOrWhiteSpace(valor))
                throw new ArgumentException("El valor no puede estar vacío.", nameof(valor));

            string esquemaFinal = string.IsNullOrWhiteSpace(esquema) ? "public" : esquema.Trim();
            var filas = new List<Dictionary<string, object?>>();

            try
            {
                var tipoColumna = await DetectarTipoColumnaAsync(nombreTabla, esquemaFinal, nombreClave);
                
                bool esBusquedaFechaSoloEnTimestamp = 
                    tipoColumna == NpgsqlDbType.Timestamp && 
                    EsFechaSinHora(valor);
                
                string sql;
                object valorConvertido;
                NpgsqlDbType tipoParametro;
                
                if (esBusquedaFechaSoloEnTimestamp)
                {
                    sql = $"SELECT * FROM \"{esquemaFinal}\".\"{nombreTabla}\" WHERE CAST(\"{nombreClave}\" AS DATE) = @valor";
                    valorConvertido = ExtraerSoloFecha(valor);
                    tipoParametro = NpgsqlDbType.Date;
                }
                else
                {
                    sql = $"SELECT * FROM \"{esquemaFinal}\".\"{nombreTabla}\" WHERE \"{nombreClave}\" = @valor";
                    valorConvertido = ConvertirValor(valor, tipoColumna);
                    tipoParametro = tipoColumna ?? NpgsqlDbType.Text;
                }

                string cadena = _proveedorConexion.ObtenerCadenaConexion();

                await using var conexion = new NpgsqlConnection(cadena);
                await conexion.OpenAsync();

                await using var comando = new NpgsqlCommand(sql, conexion);
                
                if (tipoColumna.HasValue || esBusquedaFechaSoloEnTimestamp)
                {
                    var parametro = new NpgsqlParameter("valor", tipoParametro) { Value = valorConvertido };
                    comando.Parameters.Add(parametro);
                }
                else
                {
                    comando.Parameters.AddWithValue("valor", valor);
                }

                await using var lector = await comando.ExecuteReaderAsync();
                while (await lector.ReadAsync())
                {
                    var fila = new Dictionary<string, object?>();
                    for (int i = 0; i < lector.FieldCount; i++)
                    {
                        string nombreColumna = lector.GetName(i);
                        object? valorColumna = lector.IsDBNull(i) ? null : lector.GetValue(i);
                        fila[nombreColumna] = valorColumna;
                    }
                    filas.Add(fila);
                }
            }
            catch (NpgsqlException ex)
            {
                throw new InvalidOperationException(
                    $"Error PostgreSQL al filtrar '{esquemaFinal}.{nombreTabla}': {ex.Message}", ex);
            }

            return filas;
        }

        public async Task<bool> CrearAsync(
            string nombreTabla,
            string? esquema,
            Dictionary<string, object?> datos,
            string? camposEncriptar = null)
        {
            if (string.IsNullOrWhiteSpace(nombreTabla))
                throw new ArgumentException("El nombre de la tabla no puede estar vacío.", nameof(nombreTabla));
            if (datos == null || !datos.Any())
                throw new ArgumentException("Los datos no pueden estar vacíos.", nameof(datos));

            string esquemaFinal = string.IsNullOrWhiteSpace(esquema) ? "public" : esquema.Trim();

            var datosFinales = new Dictionary<string, object?>(datos);
            
            if (!string.IsNullOrWhiteSpace(camposEncriptar))
            {
                var camposAEncriptar = camposEncriptar.Split(',')
                    .Select(c => c.Trim())
                    .Where(c => !string.IsNullOrEmpty(c))
                    .ToHashSet(StringComparer.OrdinalIgnoreCase);

                foreach (var campo in camposAEncriptar)
                {
                    if (datosFinales.ContainsKey(campo) && datosFinales[campo] != null)
                    {
                        string valorOriginal = datosFinales[campo]?.ToString() ?? "";
                        datosFinales[campo] = EncriptacionBCrypt.Encriptar(valorOriginal);
                    }
                }
            }

            var columnas = string.Join(", ", datosFinales.Keys.Select(k => $"\"{k}\""));
            var parametros = string.Join(", ", datosFinales.Keys.Select(k => $"@{k}"));
            string sql = $"INSERT INTO \"{esquemaFinal}\".\"{nombreTabla}\" ({columnas}) VALUES ({parametros})";

            try
            {
                string cadena = _proveedorConexion.ObtenerCadenaConexion();

                await using var conexion = new NpgsqlConnection(cadena);
                await conexion.OpenAsync();

                await using var comando = new NpgsqlCommand(sql, conexion);

                foreach (var kvp in datosFinales)
                {
                    var tipoColumna = await DetectarTipoColumnaAsync(nombreTabla, esquemaFinal, kvp.Key);
                    
                    if (kvp.Value == null)
                    {
                        comando.Parameters.AddWithValue(kvp.Key, DBNull.Value);
                    }
                    else if (tipoColumna.HasValue && kvp.Value is string valorString)
                    {
                        object valorConvertido = ConvertirValor(valorString, tipoColumna);
                        var parametro = new NpgsqlParameter(kvp.Key, tipoColumna.Value) { Value = valorConvertido };
                        comando.Parameters.Add(parametro);
                    }
                    else
                    {
                        comando.Parameters.AddWithValue(kvp.Key, kvp.Value);
                    }
                }

                int filasAfectadas = await comando.ExecuteNonQueryAsync();
                return filasAfectadas > 0;
            }
            catch (NpgsqlException ex)
            {
                throw new InvalidOperationException(
                    $"Error PostgreSQL al insertar en '{esquemaFinal}.{nombreTabla}': {ex.Message}", ex);
            }
        }

        public async Task<int> ActualizarAsync(
            string nombreTabla,
            string? esquema,
            string nombreClave,
            string valorClave,
            Dictionary<string, object?> datos,
            string? camposEncriptar = null)
        {
            if (string.IsNullOrWhiteSpace(nombreTabla))
                throw new ArgumentException("El nombre de la tabla no puede estar vacío.", nameof(nombreTabla));
            if (string.IsNullOrWhiteSpace(nombreClave))
                throw new ArgumentException("El nombre de la clave no puede estar vacío.", nameof(nombreClave));
            if (string.IsNullOrWhiteSpace(valorClave))
                throw new ArgumentException("El valor de la clave no puede estar vacío.", nameof(valorClave));
            if (datos == null || !datos.Any())
                throw new ArgumentException("Los datos no pueden estar vacíos.", nameof(datos));

            string esquemaFinal = string.IsNullOrWhiteSpace(esquema) ? "public" : esquema.Trim();

            var datosFinales = new Dictionary<string, object?>(datos);
            
            if (!string.IsNullOrWhiteSpace(camposEncriptar))
            {
                var camposAEncriptar = camposEncriptar.Split(',')
                    .Select(c => c.Trim())
                    .Where(c => !string.IsNullOrEmpty(c))
                    .ToHashSet(StringComparer.OrdinalIgnoreCase);

                foreach (var campo in camposAEncriptar)
                {
                    if (datosFinales.ContainsKey(campo) && datosFinales[campo] != null)
                    {
                        string valorOriginal = datosFinales[campo]?.ToString() ?? "";
                        datosFinales[campo] = EncriptacionBCrypt.Encriptar(valorOriginal);
                    }
                }
            }

            try
            {
                var tipoColumna = await DetectarTipoColumnaAsync(nombreTabla, esquemaFinal, nombreClave);
                object valorClaveConvertido = ConvertirValor(valorClave, tipoColumna);

                var clausulaSet = string.Join(", ", datosFinales.Keys.Select(k => $"\"{k}\" = @{k}"));
                string sql = $"UPDATE \"{esquemaFinal}\".\"{nombreTabla}\" SET {clausulaSet} WHERE \"{nombreClave}\" = @valorClave";

                string cadena = _proveedorConexion.ObtenerCadenaConexion();

                await using var conexion = new NpgsqlConnection(cadena);
                await conexion.OpenAsync();

                await using var comando = new NpgsqlCommand(sql, conexion);

                foreach (var kvp in datosFinales)
                {
                    var tipoColumnaSet = await DetectarTipoColumnaAsync(nombreTabla, esquemaFinal, kvp.Key);
                    
                    if (kvp.Value == null)
                    {
                        comando.Parameters.AddWithValue(kvp.Key, DBNull.Value);
                    }
                    else if (tipoColumnaSet.HasValue && kvp.Value is string valorString)
                    {
                        object valorConvertido = ConvertirValor(valorString, tipoColumnaSet);
                        var parametro = new NpgsqlParameter(kvp.Key, tipoColumnaSet.Value) { Value = valorConvertido };
                        comando.Parameters.Add(parametro);
                    }
                    else
                    {
                        comando.Parameters.AddWithValue(kvp.Key, kvp.Value);
                    }
                }

                if (tipoColumna.HasValue)
                {
                    var parametro = new NpgsqlParameter("valorClave", tipoColumna.Value) { Value = valorClaveConvertido };
                    comando.Parameters.Add(parametro);
                }
                else
                {
                    comando.Parameters.AddWithValue("valorClave", valorClave);
                }

                return await comando.ExecuteNonQueryAsync();
            }
            catch (NpgsqlException ex)
            {
                throw new InvalidOperationException(
                    $"Error PostgreSQL al actualizar '{esquemaFinal}.{nombreTabla}': {ex.Message}", ex);
            }
        }

        public async Task<int> EliminarAsync(
            string nombreTabla,
            string? esquema,
            string nombreClave,
            string valorClave)
        {
            if (string.IsNullOrWhiteSpace(nombreTabla))
                throw new ArgumentException("El nombre de la tabla no puede estar vacío.", nameof(nombreTabla));
            if (string.IsNullOrWhiteSpace(nombreClave))
                throw new ArgumentException("El nombre de la clave no puede estar vacío.", nameof(nombreClave));
            if (string.IsNullOrWhiteSpace(valorClave))
                throw new ArgumentException("El valor de la clave no puede estar vacío.", nameof(valorClave));

            string esquemaFinal = string.IsNullOrWhiteSpace(esquema) ? "public" : esquema.Trim();

            try
            {
                var tipoColumna = await DetectarTipoColumnaAsync(nombreTabla, esquemaFinal, nombreClave);
                object valorConvertido = ConvertirValor(valorClave, tipoColumna);

                string sql = $"DELETE FROM \"{esquemaFinal}\".\"{nombreTabla}\" WHERE \"{nombreClave}\" = @valorClave";
                
                string cadena = _proveedorConexion.ObtenerCadenaConexion();

                await using var conexion = new NpgsqlConnection(cadena);
                await conexion.OpenAsync();

                await using var comando = new NpgsqlCommand(sql, conexion);

                if (tipoColumna.HasValue)
                {
                    var parametro = new NpgsqlParameter("valorClave", tipoColumna.Value) { Value = valorConvertido };
                    comando.Parameters.Add(parametro);
                }
                else
                {
                    comando.Parameters.AddWithValue("valorClave", valorClave);
                }

                return await comando.ExecuteNonQueryAsync();
            }
            catch (NpgsqlException ex)
            {
                throw new InvalidOperationException(
                    $"Error PostgreSQL al eliminar de '{esquemaFinal}.{nombreTabla}': {ex.Message}", ex);
            }
        }

        public async Task<string?> ObtenerHashContrasenaAsync(
            string nombreTabla,
            string? esquema,
            string campoUsuario,
            string campoContrasena,
            string valorUsuario)
        {
            if (string.IsNullOrWhiteSpace(nombreTabla))
                throw new ArgumentException("El nombre de la tabla no puede estar vacío.", nameof(nombreTabla));
            if (string.IsNullOrWhiteSpace(campoUsuario))
                throw new ArgumentException("El campo de usuario no puede estar vacío.", nameof(campoUsuario));
            if (string.IsNullOrWhiteSpace(campoContrasena))
                throw new ArgumentException("El campo de contraseña no puede estar vacío.", nameof(campoContrasena));
            if (string.IsNullOrWhiteSpace(valorUsuario))
                throw new ArgumentException("El valor de usuario no puede estar vacío.", nameof(valorUsuario));

            string esquemaFinal = string.IsNullOrWhiteSpace(esquema) ? "public" : esquema.Trim();

            try
            {
                var tipoColumna = await DetectarTipoColumnaAsync(nombreTabla, esquemaFinal, campoUsuario);
                object valorConvertido = ConvertirValor(valorUsuario, tipoColumna);

                string sql = $"SELECT \"{campoContrasena}\" FROM \"{esquemaFinal}\".\"{nombreTabla}\" WHERE \"{campoUsuario}\" = @valorUsuario";
                
                string cadena = _proveedorConexion.ObtenerCadenaConexion();

                await using var conexion = new NpgsqlConnection(cadena);
                await conexion.OpenAsync();

                await using var comando = new NpgsqlCommand(sql, conexion);

                if (tipoColumna.HasValue)
                {
                    var parametro = new NpgsqlParameter("valorUsuario", tipoColumna.Value) { Value = valorConvertido };
                    comando.Parameters.Add(parametro);
                }
                else
                {
                    comando.Parameters.AddWithValue("valorUsuario", valorUsuario);
                }

                var resultado = await comando.ExecuteScalarAsync();
                return resultado?.ToString();
            }
            catch (NpgsqlException ex)
            {
                throw new InvalidOperationException(
                    $"Error PostgreSQL al obtener hash de '{esquemaFinal}.{nombreTabla}': {ex.Message}", ex);
            }
        }

        public async Task<Dictionary<string, object?>> ObtenerDiagnosticoConexionAsync()
        {
            string sql = @"
                SELECT
                    current_database() as nombre_base_datos,
                    current_schema() as esquema_actual,
                    version() as version_servidor,
                    inet_server_addr() as direccion_ip_servidor,
                    inet_server_port() as puerto_servidor,
                    pg_postmaster_start_time() as hora_inicio_servidor,
                    current_user as usuario_actual,
                    pg_backend_pid() as id_proceso_conexion";

            string cadena = _proveedorConexion.ObtenerCadenaConexion();
            await using var conexion = new NpgsqlConnection(cadena);
            await conexion.OpenAsync();

            await using var comando = new NpgsqlCommand(sql, conexion);
            await using var lector = await comando.ExecuteReaderAsync();

            if (!await lector.ReadAsync())
                throw new InvalidOperationException("No se pudo obtener información de diagnóstico.");

            var nombreBaseDatos = lector["nombre_base_datos"]?.ToString() ?? "desconocido";
            var esquemaActual = lector["esquema_actual"]?.ToString() ?? "public";
            var versionServidor = lector["version_servidor"]?.ToString() ?? "desconocido";
            var direccionIP = lector["direccion_ip_servidor"]?.ToString() ?? "localhost";
            var puertoServidor = lector["puerto_servidor"];
            var horaInicioServidor = lector["hora_inicio_servidor"];
            var usuarioActual = lector["usuario_actual"]?.ToString() ?? "desconocido";
            var idProcesoConexion = lector["id_proceso_conexion"];

            var diagnostico = new Dictionary<string, object?>
            {
                ["proveedor"] = "PostgreSQL",
                ["baseDatos"] = nombreBaseDatos,
                ["esquema"] = esquemaActual,
                ["version"] = versionServidor,
                ["direccionIP"] = direccionIP,
                ["puerto"] = puertoServidor,
                ["horaInicio"] = horaInicioServidor,
                ["usuarioConectado"] = usuarioActual,
                ["idProcesoConexion"] = idProcesoConexion
            };

            return diagnostico;
        }



        /// <summary>
        /// Elimina un registro usando una clave primaria compuesta (N columnas).
        ///
        /// Construye dinámicamente: DELETE FROM "esquema"."tabla"
        /// WHERE "col1" = @clave_0 AND "col2" = @clave_1 AND ...
        ///
        /// Cada valor de clave se detecta por tipo de columna y se convierte
        /// al tipo nativo apropiado (int, date, uuid, etc.) antes de parametrizarse.
        /// Los nombres de columna NUNCA se concatenan sin escapar: van entre comillas dobles
        /// y los valores van como parámetros, evitando inyección SQL.
        /// </summary>
        public async Task<int> EliminarCompuestaAsync(
            string nombreTabla,
            string? esquema,
            List<(string nombre, string valor)> claves)
        {
            if (string.IsNullOrWhiteSpace(nombreTabla))
                throw new ArgumentException("El nombre de la tabla no puede estar vacío.", nameof(nombreTabla));
            if (claves == null || claves.Count == 0)
                throw new ArgumentException("Debe proporcionar al menos una columna clave.", nameof(claves));

            string esquemaFinal = string.IsNullOrWhiteSpace(esquema) ? "public" : esquema.Trim();

            try
            {
                // FASE 1: Detectar el tipo de cada columna clave y convertir su valor.
                // Se hace ANTES de abrir la conexión principal para fallar rápido si algo no cuadra.
                var clavesConTipo = new List<(string nombre, object valor, NpgsqlDbType? tipo)>();
                for (int i = 0; i < claves.Count; i++)
                {
                    var (nombreCol, valorStr) = claves[i];
                    var tipo = await DetectarTipoColumnaAsync(nombreTabla, esquemaFinal, nombreCol);
                    object valorConvertido = ConvertirValor(valorStr, tipo);
                    clavesConTipo.Add((nombreCol, valorConvertido, tipo));
                }

                // FASE 2: Construir el WHERE dinámico con parámetros indexados.
                // Cada columna recibe un parámetro único: @clave_0, @clave_1, @clave_2, ...
                // Esto evita colisiones si dos columnas tuvieran nombres parecidos.
                var clausulasWhere = clavesConTipo
                    .Select((c, i) => $"\"{c.nombre}\" = @clave_{i}");
                string where = string.Join(" AND ", clausulasWhere);

                string sql = $"DELETE FROM \"{esquemaFinal}\".\"{nombreTabla}\" WHERE {where}";

                // FASE 3: Ejecutar contra la base de datos
                string cadena = _proveedorConexion.ObtenerCadenaConexion();
                await using var conexion = new NpgsqlConnection(cadena);
                await conexion.OpenAsync();

                await using var comando = new NpgsqlCommand(sql, conexion);

                // FASE 4: Asociar cada valor con su parámetro tipado
                for (int i = 0; i < clavesConTipo.Count; i++)
                {
                    var (_, valor, tipo) = clavesConTipo[i];
                    string nombreParam = $"clave_{i}";

                    if (tipo.HasValue)
                    {
                        var parametro = new NpgsqlParameter(nombreParam, tipo.Value) { Value = valor };
                        comando.Parameters.Add(parametro);
                    }
                    else
                    {
                        // Si no se pudo detectar el tipo, dejar que Npgsql infiera (fallback string)
                        comando.Parameters.AddWithValue(nombreParam, valor);
                    }
                }

                return await comando.ExecuteNonQueryAsync();
            }
            catch (NpgsqlException ex)
            {
                throw new InvalidOperationException(
                    $"Error PostgreSQL al eliminar de '{esquemaFinal}.{nombreTabla}' con PK compuesta: {ex.Message}", ex);
            }
        }

        /// <summary>
        /// Actualiza un registro usando una clave primaria compuesta (N columnas).
        ///
        /// Construye dinámicamente: UPDATE "esquema"."tabla"
        /// SET "colA" = @colA, "colB" = @colB, ...
        /// WHERE "pk1" = @clave_0 AND "pk2" = @clave_1 AND ...
        ///
        /// Reutiliza la misma estrategia de detección de tipos que ActualizarAsync,
        /// tanto para los campos del SET como para las columnas del WHERE.
        /// </summary>
        public async Task<int> ActualizarCompuestaAsync(
            string nombreTabla,
            string? esquema,
            List<(string nombre, string valor)> claves,
            Dictionary<string, object?> datos,
            string? camposEncriptar = null)
        {
            if (string.IsNullOrWhiteSpace(nombreTabla))
                throw new ArgumentException("El nombre de la tabla no puede estar vacío.", nameof(nombreTabla));
            if (claves == null || claves.Count == 0)
                throw new ArgumentException("Debe proporcionar al menos una columna clave.", nameof(claves));
            if (datos == null || !datos.Any())
                throw new ArgumentException("Los datos no pueden estar vacíos.", nameof(datos));

            string esquemaFinal = string.IsNullOrWhiteSpace(esquema) ? "public" : esquema.Trim();

            // Aplicar encriptación a los campos solicitados (mismo patrón que ActualizarAsync)
            var datosFinales = new Dictionary<string, object?>(datos);

            if (!string.IsNullOrWhiteSpace(camposEncriptar))
            {
                var camposAEncriptar = camposEncriptar.Split(',')
                    .Select(c => c.Trim())
                    .Where(c => !string.IsNullOrEmpty(c))
                    .ToHashSet(StringComparer.OrdinalIgnoreCase);

                foreach (var campo in camposAEncriptar)
                {
                    if (datosFinales.ContainsKey(campo) && datosFinales[campo] != null)
                    {
                        string valorOriginal = datosFinales[campo]?.ToString() ?? "";
                        datosFinales[campo] = EncriptacionBCrypt.Encriptar(valorOriginal);
                    }
                }
            }

            try
            {
                // FASE 1: Detectar tipos de las columnas clave y convertir sus valores
                var clavesConTipo = new List<(string nombre, object valor, NpgsqlDbType? tipo)>();
                foreach (var (nombreCol, valorStr) in claves)
                {
                    var tipo = await DetectarTipoColumnaAsync(nombreTabla, esquemaFinal, nombreCol);
                    object valorConvertido = ConvertirValor(valorStr, tipo);
                    clavesConTipo.Add((nombreCol, valorConvertido, tipo));
                }

                // FASE 2: Construir cláusula SET dinámica
                // Cada campo del diccionario va como "col" = @col
                var clausulaSet = string.Join(", ", datosFinales.Keys.Select(k => $"\"{k}\" = @{k}"));

                // FASE 3: Construir cláusula WHERE dinámica con parámetros indexados
                // Usamos @clave_0, @clave_1, ... para que NUNCA choquen con los nombres
                // de los campos del SET (importante si una columna del SET se llamara
                // igual que una columna de la PK, aunque sea raro).
                var clausulasWhere = clavesConTipo
                    .Select((c, i) => $"\"{c.nombre}\" = @clave_{i}");
                string where = string.Join(" AND ", clausulasWhere);

                string sql = $"UPDATE \"{esquemaFinal}\".\"{nombreTabla}\" SET {clausulaSet} WHERE {where}";

                // FASE 4: Ejecutar contra la base de datos
                string cadena = _proveedorConexion.ObtenerCadenaConexion();
                await using var conexion = new NpgsqlConnection(cadena);
                await conexion.OpenAsync();

                await using var comando = new NpgsqlCommand(sql, conexion);

                // FASE 5: Parámetros del SET (mismo patrón que ActualizarAsync)
                foreach (var kvp in datosFinales)
                {
                    var tipoColumnaSet = await DetectarTipoColumnaAsync(nombreTabla, esquemaFinal, kvp.Key);

                    if (kvp.Value == null)
                    {
                        comando.Parameters.AddWithValue(kvp.Key, DBNull.Value);
                    }
                    else if (tipoColumnaSet.HasValue && kvp.Value is string valorString)
                    {
                        object valorConvertido = ConvertirValor(valorString, tipoColumnaSet);
                        var parametro = new NpgsqlParameter(kvp.Key, tipoColumnaSet.Value) { Value = valorConvertido };
                        comando.Parameters.Add(parametro);
                    }
                    else
                    {
                        comando.Parameters.AddWithValue(kvp.Key, kvp.Value);
                    }
                }

                // FASE 6: Parámetros del WHERE (PK compuesta)
                for (int i = 0; i < clavesConTipo.Count; i++)
                {
                    var (_, valor, tipo) = clavesConTipo[i];
                    string nombreParam = $"clave_{i}";

                    if (tipo.HasValue)
                    {
                        var parametro = new NpgsqlParameter(nombreParam, tipo.Value) { Value = valor };
                        comando.Parameters.Add(parametro);
                    }
                    else
                    {
                        comando.Parameters.AddWithValue(nombreParam, valor);
                    }
                }

                return await comando.ExecuteNonQueryAsync();
            }
            catch (NpgsqlException ex)
            {
                throw new InvalidOperationException(
                    $"Error PostgreSQL al actualizar '{esquemaFinal}.{nombreTabla}' con PK compuesta: {ex.Message}", ex);
            }
        }


    }
}

