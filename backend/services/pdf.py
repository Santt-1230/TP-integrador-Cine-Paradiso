from io import BytesIO
from xml.sax.saxutils import escape
import qrcode

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from datetime import datetime


def generar_pdf_factura(factura):
    salida = BytesIO()
    documento = SimpleDocTemplate(
        salida, pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title=f"Factura {factura['factura']['numero']}",
    )
    estilos = getSampleStyleSheet()
    estilo_celda = ParagraphStyle("CeldaFactura", parent=estilos["BodyText"], fontSize=9, leading=12)
    contenido = [
        Paragraph("Cine Paradiso", estilos["Heading2"]),
        Paragraph("Factura de compra", estilos["Title"]),
        Spacer(1, 5 * mm),
    ]
    datos = factura["factura"]
    contenido.append(Paragraph(
        f"<b>Número:</b> {escape(str(datos.get('numero') or ''))}"
        f" &nbsp;&nbsp; <b>Emisión:</b> {escape(str(datos.get('fecha_emision') or ''))}"
        f" &nbsp;&nbsp; <b>Estado:</b> {escape(str(datos.get('estado') or ''))}",
        estilos["BodyText"],
    ))
    cliente = factura["cliente"]
    contenido.extend([
        Spacer(1, 4 * mm),
        Paragraph("Cliente", estilos["Heading2"]),
        Paragraph(
            f"{escape(str(cliente.get('nombre') or ''))} — "
            f"{escape(str(cliente.get('email') or ''))}",
            estilos["BodyText"],
        ),
        Spacer(1, 4 * mm),
        Paragraph("Función", estilos["Heading2"]),
        Paragraph(
            f"Película: {escape(str(factura['funcion'].get('pelicula') or ''))} "
            f"— {escape(str(factura['funcion'].get('fecha_hora_inicio') or ''))} "
            f"— Sala {escape(str(factura['funcion'].get('sala') or ''))} "
            f"— {escape(str(factura['funcion'].get('local') or ''))}",
            estilos["BodyText"],
        ),
        Spacer(1, 4 * mm),
        Paragraph("Detalle", estilos["Heading2"]),
    ])

    filas = [["Concepto", "Cantidad", "Precio unitario", "Subtotal"]]
    for entrada in factura.get("entradas", []):
        filas.append([
            Paragraph(f"Entrada — fila {escape(str(entrada.get('fila', '')))}, butaca {escape(str(entrada.get('numero', '')))}", estilo_celda),
            "1", f"$ {entrada['precio_unitario']:.2f}", f"$ {entrada['precio_unitario']:.2f}",
        ])
    for producto in factura.get("productos", []):
        filas.append([
            Paragraph(escape(str(producto.get("nombre") or "Producto")), estilo_celda),
            str(producto.get("cantidad", 0)),
            f"$ {producto['precio_unitario']:.2f}", f"$ {producto['subtotal']:.2f}",
        ])
    tabla = Table(filas, colWidths=[85 * mm, 20 * mm, 32 * mm, 32 * mm], repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#26364a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d5dbe3")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f6f9")]),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
    ]))
    contenido.extend([tabla, Spacer(1, 5 * mm)])
    totales = factura["totales"]
    contenido.append(Table([
        ["Subtotal entradas", f"$ {totales['subtotal_entradas']:.2f}"],
        ["Subtotal productos", f"$ {totales['subtotal_productos']:.2f}"],
        ["Descuento promociones", f"- $ {totales['descuento']:.2f}"],
        ["Total (ARS)", f"$ {totales['total']:.2f}"],
    ], colWidths=[137 * mm, 32 * mm], hAlign="RIGHT", style=TableStyle([
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LINEABOVE", (0, 3), (-1, 3), 1, colors.HexColor("#26364a")),
        ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
    ])))
    documento.build(contenido)
    salida.seek(0)
    return salida.getvalue()


def generar_pdf_entradas(factura, qrs):
    """Genera un PDF con una entrada por página y su QR escaneable."""
    salida = BytesIO()
    numero_factura = factura["factura"].get("numero") or factura["factura"].get("id_compra")
    documento = SimpleDocTemplate(
        salida, pagesize=A4, rightMargin=25 * mm, leftMargin=25 * mm,
        topMargin=25 * mm, bottomMargin=25 * mm,
        title=f"Entradas {numero_factura}",
    )
    estilos = getSampleStyleSheet()
    color_marca = colors.HexColor("#172B4D")
    color_acento = colors.HexColor("#E5A93D")
    color_fondo = colors.HexColor("#F3F6FA")
    estilo_marca = ParagraphStyle(
        "MarcaEntrada", parent=estilos["Heading2"], fontName="Helvetica-Bold",
        fontSize=15, leading=18, textColor=colors.white, spaceAfter=0,
    )
    estilo_etiqueta = ParagraphStyle(
        "EtiquetaEntrada", parent=estilos["BodyText"], fontName="Helvetica-Bold",
        fontSize=8, leading=10, textColor=colors.HexColor("#64748B"),
    )
    estilo_dato = ParagraphStyle(
        "DatoEntrada", parent=estilos["BodyText"], fontName="Helvetica-Bold",
        fontSize=11, leading=15, textColor=color_marca,
    )
    estilo_pelicula = ParagraphStyle(
        "PeliculaEntrada", parent=estilos["Title"], fontName="Helvetica-Bold",
        fontSize=21, leading=25, textColor=color_marca, alignment=1,
    )
    estilo_numero = ParagraphStyle(
        "NumeroEntrada", parent=estilos["Heading2"], fontName="Helvetica-Bold",
        fontSize=13, leading=16, textColor=color_marca, alignment=1,
    )
    estilo_instruccion = ParagraphStyle(
        "InstruccionEntrada", parent=estilos["BodyText"], fontSize=9,
        leading=13, textColor=colors.HexColor("#475569"), alignment=1,
    )
    estilo_codigo_manual = ParagraphStyle(
        "CodigoManualEntrada", parent=estilos["Heading2"], fontName="Courier-Bold",
        fontSize=15, leading=20, textColor=color_marca, alignment=1,
    )
    entradas = {entrada["id_entrada"]: entrada for entrada in factura.get("entradas", [])}
    funcion = factura.get("funcion", {})
    contenido = []

    for indice, qr in enumerate(qrs):
        entrada = entradas.get(qr["id_entrada"], {})
        encabezado = Table(
            [[Paragraph("CINE PARADISO", estilo_marca), Paragraph("ENTRADA DIGITAL", estilo_marca)]],
            colWidths=[85 * mm, 75 * mm],
        )
        encabezado.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), color_marca),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LINEBELOW", (0, -1), (-1, -1), 3, color_acento),
        ]))
        datos_funcion = Table([
            [Paragraph("FECHA Y HORA", estilo_etiqueta), Paragraph("LOCAL", estilo_etiqueta)],
            [Paragraph(escape(str(funcion.get("fecha_hora_inicio") or "—")), estilo_dato),
             Paragraph(escape(str(funcion.get("local") or "—")), estilo_dato)],
            [Paragraph("SALA", estilo_etiqueta), Paragraph("BUTACA", estilo_etiqueta)],
            [Paragraph(escape(str(funcion.get("sala") or "—")), estilo_dato),
             Paragraph(
                 f"Fila {escape(str(entrada.get('fila') or '—'))} · "
                 f"N.º {escape(str(entrada.get('numero') or '—'))}",
                 estilo_dato,
             )],
        ], colWidths=[80 * mm, 80 * mm])
        datos_funcion.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), color_fondo),
            ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#D9E1EC")),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.white),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        contenido.extend([
            encabezado,
            Spacer(1, 12 * mm),
            Paragraph(escape(str(funcion.get("pelicula") or "Función")), estilo_pelicula),
            Spacer(1, 4 * mm),
            Paragraph(f"ENTRADA N.º {escape(str(qr['id_entrada']))}", estilo_numero),
            Spacer(1, 8 * mm),
            datos_funcion,
            Spacer(1, 10 * mm),
        ])
        imagen_qr = qrcode.make(qr["token"])
        buffer_qr = BytesIO()
        imagen_qr.save(buffer_qr, format="PNG")
        buffer_qr.seek(0)
        imagen = Image(buffer_qr, width=68 * mm, height=68 * mm, hAlign="CENTER")
        tarjeta_qr = Table([[imagen]], colWidths=[82 * mm], rowHeights=[82 * mm], hAlign="CENTER")
        tarjeta_qr.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#D9E1EC")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        contenido.extend([
            tarjeta_qr,
            Spacer(1, 5 * mm),
            Paragraph("CÓDIGO MANUAL", estilo_etiqueta),
            Spacer(1, 1 * mm),
            Paragraph(escape(str(qr.get("codigo_manual") or "—")), estilo_codigo_manual),
            Spacer(1, 3 * mm),
            Paragraph("Presentá este código al ingresar. Cada QR permite un solo acceso.", estilo_instruccion),
            Spacer(1, 8 * mm),
            Paragraph(
                f"Compra {escape(str(factura['factura'].get('id_compra') or ''))}"
                f" &nbsp;·&nbsp; Cine Paradiso",
                estilo_etiqueta,
            ),
        ])
        if indice < len(qrs) - 1:
            contenido.append(PageBreak())

    documento.build(contenido)
    salida.seek(0)
    return salida.getvalue()

def generar_pdf_productos(qrs):
    """Genera un PDF con un producto por página y su QR escaneable."""

    salida = BytesIO()

    documento = SimpleDocTemplate(
        salida,
        pagesize=A4,
        rightMargin=25 * mm,
        leftMargin=25 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
        title="QR de productos",
    )

    estilos = getSampleStyleSheet()

    # Colores de Cine Paradiso
    color_marca = colors.HexColor("#172B4D")
    color_acento = colors.HexColor("#E5A93D")
    color_fondo = colors.HexColor("#F3F6FA")

    # Estilos
    estilo_marca = ParagraphStyle(
        "MarcaProducto",
        parent=estilos["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.white,
        spaceAfter=0,
    )

    estilo_etiqueta = ParagraphStyle(
        "EtiquetaProducto",
        parent=estilos["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#64748B"),
    )

    estilo_dato = ParagraphStyle(
        "DatoProducto",
        parent=estilos["BodyText"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=color_marca,
    )

    estilo_producto = ParagraphStyle(
        "NombreProducto",
        parent=estilos["Title"],
        fontName="Helvetica-Bold",
        fontSize=21,
        leading=25,
        textColor=color_marca,
        alignment=1,
    )

    estilo_numero = ParagraphStyle(
        "NumeroProducto",
        parent=estilos["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=color_marca,
        alignment=1,
    )

    estilo_instruccion = ParagraphStyle(
        "InstruccionProducto",
        parent=estilos["BodyText"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#475569"),
        alignment=1,
    )

    estilo_codigo_manual = ParagraphStyle(
        "CodigoManualProducto",
        parent=estilos["Heading2"],
        fontName="Courier-Bold",
        fontSize=15,
        leading=20,
        textColor=color_marca,
        alignment=1,
    )

    contenido = []

    for indice, qr in enumerate(qrs):

        # Encabezado
        encabezado = Table(
            [[
                Paragraph("CINE PARADISO", estilo_marca),
                Paragraph("PRODUCTO DIGITAL", estilo_marca)
            ]],
            colWidths=[85 * mm, 75 * mm],
        )

        encabezado.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), color_marca),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LINEBELOW", (0, -1), (-1, -1), 3, color_acento),
        ]))

        # Información del producto
        datos_producto = Table([
            [
                Paragraph("CATEGORÍA", estilo_etiqueta),
                Paragraph("CANTIDAD", estilo_etiqueta)
            ],
            [
                Paragraph(
                    escape(str(qr.get("categoria") or "—")),
                    estilo_dato
                ),
                Paragraph(
                    f"{qr.get('cantidad', 0)} unidad/es",
                    estilo_dato
                )
            ],
            [
                Paragraph("PRECIO UNITARIO", estilo_etiqueta),
                Paragraph("SUBTOTAL", estilo_etiqueta)
            ],
            [
                Paragraph(
                    f"$ {float(qr.get('precio_unitario') or 0):.2f}",
                    estilo_dato
                ),
                Paragraph(
                    f"$ {float(qr.get('subtotal') or 0):.2f}",
                    estilo_dato
                )
            ],
        ], colWidths=[80 * mm, 80 * mm])

        datos_producto.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), color_fondo),
            ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#D9E1EC")),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.white),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))

        # Construir contenido de la página
        contenido.extend([
            encabezado,
            Spacer(1, 12 * mm),

            Paragraph(
                escape(str(qr.get("producto") or "Producto")),
                estilo_producto
            ),

            Spacer(1, 4 * mm),

            Paragraph(
                f"PRODUCTO N.º {escape(str(qr['id_compra_producto']))}",
                estilo_numero
            ),

            Spacer(1, 8 * mm),

            datos_producto,

            Spacer(1, 10 * mm),
        ])

        # Generar imagen QR
        imagen_qr = qrcode.make(qr["token"])

        buffer_qr = BytesIO()
        imagen_qr.save(buffer_qr, format="PNG")
        buffer_qr.seek(0)

        imagen = Image(
            buffer_qr,
            width=68 * mm,
            height=68 * mm,
            hAlign="CENTER"
        )

        # Enmarcar QR
        tarjeta_qr = Table(
            [[imagen]],
            colWidths=[82 * mm],
            rowHeights=[82 * mm],
            hAlign="CENTER"
        )

        tarjeta_qr.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#D9E1EC")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))

        contenido.extend([
            tarjeta_qr,
            Spacer(1, 5 * mm),

            Paragraph("CÓDIGO MANUAL", estilo_etiqueta),

            Spacer(1, 1 * mm),

            Paragraph(
                escape(str(qr.get("codigo_manual") or "—")),
                estilo_codigo_manual
            ),

            Spacer(1, 3 * mm),

            Paragraph(
                "Presentá este código para retirar tu producto. "
                "Cada QR permite un único retiro de la cantidad indicada.",
                estilo_instruccion
            ),

            Spacer(1, 8 * mm),

            Paragraph(
                f"Compra {escape(str(qr['id_compra']))}"
                " &nbsp;·&nbsp; Cine Paradiso",
                estilo_etiqueta
            ),
        ])

        # Una página por producto
        if indice < len(qrs) - 1:
            contenido.append(PageBreak())

    documento.build(contenido)

    salida.seek(0)

    return salida.getvalue()


def generar_pdf_reembolso(factura, monto_reembolso=None, fecha_cancelacion=None):
    salida = BytesIO()
    datos = factura["factura"]
    numero_original = datos.get("numero") or f"compra-{datos.get('id_compra')}"
    total_original = float(factura["totales"]["total"])
    reembolso = float(monto_reembolso) if monto_reembolso is not None else total_original
    fecha_canc = fecha_cancelacion or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    documento = SimpleDocTemplate(
        salida, pagesize=A4, rightMargin=20 * mm, leftMargin=20 * mm,
        topMargin=18 * mm, bottomMargin=18 * mm,
        title=f"Comprobante de Reembolso - {numero_original}",
    )
    estilos = getSampleStyleSheet()
    estilo_celda = ParagraphStyle("CeldaReembolso", parent=estilos["BodyText"], fontSize=9, leading=12)
    estilo_nota = ParagraphStyle(
        "NotaReembolso", parent=estilos["BodyText"], fontSize=8.5,
        leading=12, textColor=colors.HexColor("#475569"),
    )

    contenido = [
        Paragraph("Cine Paradiso", estilos["Heading2"]),
        Paragraph("Comprobante de Cancelación y Reembolso", estilos["Title"]),
        Spacer(1, 5 * mm),
        Paragraph(
            f"<b>Factura original:</b> {escape(str(numero_original))}"
            f" &nbsp;&nbsp; <b>Compra:</b> {escape(str(datos.get('id_compra') or ''))}"
            f" &nbsp;&nbsp; <b>Cancelación:</b> {escape(str(fecha_canc))}"
            f" &nbsp;&nbsp; <b>Estado:</b> Cancelada",
            estilos["BodyText"],
        ),
    ]

    cliente = factura["cliente"]
    contenido.extend([
        Spacer(1, 4 * mm),
        Paragraph("Cliente", estilos["Heading2"]),
        Paragraph(
            f"{escape(str(cliente.get('nombre') or ''))} — "
            f"{escape(str(cliente.get('email') or ''))} "
            f"(ID {escape(str(cliente.get('id_usuario') or ''))})",
            estilos["BodyText"],
        ),
        Spacer(1, 4 * mm),
        Paragraph("Función cancelada", estilos["Heading2"]),
        Paragraph(
            f"Película: {escape(str(factura['funcion'].get('pelicula') or ''))} "
            f"— {escape(str(factura['funcion'].get('fecha_hora_inicio') or ''))} "
            f"— Sala {escape(str(factura['funcion'].get('sala') or ''))} "
            f"— {escape(str(factura['funcion'].get('local') or ''))}",
            estilos["BodyText"],
        ),
        Spacer(1, 4 * mm),
        Paragraph("Detalle de ítems anulados", estilos["Heading2"]),
    ])

    filas = [["Concepto", "Cantidad", "Precio unitario", "Subtotal"]]
    for entrada in factura.get("entradas", []):
        filas.append([
            Paragraph(
                f"Entrada anulada — fila {escape(str(entrada.get('fila', '')))}, "
                f"butaca {escape(str(entrada.get('numero', '')))}",
                estilo_celda,
            ),
            "1",
            f"$ {entrada['precio_unitario']:.2f}",
            f"$ {entrada['precio_unitario']:.2f}",
        ])
    for producto in factura.get("productos", []):
        filas.append([
            Paragraph(f"{escape(str(producto.get('nombre') or 'Producto'))} (anulado)", estilo_celda),
            str(producto.get("cantidad", 0)),
            f"$ {producto['precio_unitario']:.2f}",
            f"$ {producto['subtotal']:.2f}",
        ])

    tabla = Table(filas, colWidths=[85 * mm, 20 * mm, 32 * mm, 32 * mm], repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#26364a")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d5dbe3")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f6f9")]),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
    ]))
    contenido.extend([tabla, Spacer(1, 5 * mm)])

    totales = factura["totales"]
    contenido.append(Table([
        ["Subtotal entradas anuladas", f"$ {totales['subtotal_entradas']:.2f}"],
        ["Subtotal productos anulados", f"$ {totales['subtotal_productos']:.2f}"],
        ["Total original abonado", f"$ {total_original:.2f}"],
        ["Monto reembolsado (ARS)", f"$ {reembolso:.2f}"],
    ], colWidths=[137 * mm, 32 * mm], hAlign="RIGHT", style=TableStyle([
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LINEABOVE", (0, 3), (-1, 3), 1, colors.HexColor("#26364a")),
        ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
    ])))

    contenido.extend([
        Spacer(1, 8 * mm),
        Paragraph(
            "Las entradas y códigos QR asociados a esta compra fueron invalidados y ya no son válidos "
            "para el ingreso a sala ni retiro de productos. El reintegro se acreditará en el mismo medio "
            "de pago utilizado en la compra original.",
            estilo_nota,
        ),
    ])

    documento.build(contenido)
    salida.seek(0)
    return salida.getvalue()