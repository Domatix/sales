.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

================================
Importador de pedidos de venta
================================

Crea pedidos y clientes a partir de un fichero excel con las siguientes cabeceras.

* CANAL : Plataforma en la que se ha realizado la venta.(Amazon, Ebay...) Es necesario crear primero los canales en Odoo (Ventas > Configuración > Canales)
* N VENTA : Número de venta interno.
* N VENTA PLAT. : Número de venta proporcionado por la plataforma.
* FECHA VENTA : Fecha del pedido en formato dd/mm/YYYY
* N SEGUIMIENTO : Número de seguimiento del pedido
* USER : Usuario del cliente en la plataforma.
* NOMBRE : Nombre del cliente que recibirá el pedido.
* NOMBRE FACT. : Nombre de facturación del cliente.
* TELEFONO 1 : Teléfono del cliente que recibirá el pedido.
* TELEFONO FACT. : Teléfono de facturación del cliente.
* TELEFONO 2 : Segundo teléfono del cliente que recibirá el pedido.
* E-MAIL : Correo electrónico del cliente que recibirá el pedido.
* E-MAIL FACT. : Correo electrónico de facturación.
* DIRECCION : Dirección de envío.
* DIRECCION FACT. : Dirección de facturación.
* POBLACION : Población a la que se enviará el pedido.
* POBLACION FACT. : Población del cliente que paga el pedido.
* ESTADO : Estado al que se envía el pedido
* ESTADO FACT. : Estado del cliente que paga el pedido.
* CODIGO POSTAL : Código postal de envío.
* CODIGO POSTAL FACT. : Codigo postal del cliente que paga el pedido.
* PAIS : País donde se enviará el pedido.
* PAIS FACT. : País de facturación.
* SKU : Referencia única del producto que se vende en el pedido. (Es necesario añadir en Odoo el SKU correspondiente en la variante de producto. Ventas > Variantes de producto > SKU)
* DESCRIPCION : Descripción del producto.
* CANTIDAD : Cantidad que se ha vendido.
* PRECIO : Precio del producto.
* ENVIO : Costes de envío
* IVA : Iva del producto
* METODO PAGO : Método de pago del producto (Creado en Odoo).

Uso
===

1. Ir a Ventas > Importación de Pedidos > Importar pedidos de venta
2. Añadir fichero xls o xlsx
3. Confirmar



Créditos
========

Contribuidores
--------------

* Nacho Serra Almenar <nacho.serra@domatix.com>

Maintainer
----------
 * Domatix  <https://github.com/Domatix>
