# Pruebas del sistema

Antes de entregar se intentó romper el programa a propósito. Marca cada fila con ✔ cuando la hayas probado en tu computadora.

| Prueba | Dónde | Entrada de ejemplo | Resultado esperado | ✔ |
|---|---|---|---|---|
| Texto donde se espera número | Nueva compra (presupuesto) | `abc` | Cuadro de error: "debe ser un número válido" | ✅ |
| Valor negativo | Agregar producto (precio) | `-50` | Cuadro de error: "debe ser mayor que 0" | ✅ |
| Valor cero | Agregar producto (cantidad) | `0` | Cuadro de error: "debe ser mayor que 0" | ✅ |
| Cantidad decimal | Agregar producto (cantidad) | `2.5` | Cuadro de error: "debe ser un número válido" | ✅ |
| Campo vacío | Nueva compra (cliente) | (nada) | Cuadro de error: "no puede estar vacío" | ✅ |
| Registro inexistente | Agregar producto, Ver factura o Eliminar | Compra `9999` | "No existe una compra con ese número", sin cerrarse |✅|
| Base de datos vacía | Listar compras | (sin compras) | Mensaje "No hay compras registradas." |✅|
| Compra sin productos | Ver factura | Compra recién creada | "Esta compra todavía no tiene productos." |✅|
| Presupuesto superado | Agregar producto | Producto que pase del presupuesto | Aviso con el exceso y pregunta si se agrega |✅|
| Cierre y reapertura | Cerrar y volver a ejecutar | — | Las compras siguen guardadas en Listar compras |✅|
