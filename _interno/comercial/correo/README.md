# Correo comercial (hola@guitle.com)

- `borradores/`: cada fichero se guarda como **borrador** en el buzón de hola@guitle.com (carpeta Borradores). No se
  envía nada.
- `enviar/`: cada fichero se **envía** desde hola@guitle.com y queda copia en Enviados. Un correo solo pasa aquí
  cuando Manuel dice «envía» para ese correo concreto.
- Lo hace `.github/workflows/correo.yml` (scraper/correo.py) con los secretos SMTP_* que ya existen. No reenvía ni
  duplica: cada correo lleva un identificador fijo.
- Ojo: el repositorio es público. Aquí solo van correos a empresas (tiendas, redes de afiliación), nunca datos
  personales, bancarios ni claves.

Formato (texto plano):

    Para: afiliados@tienda.com
    Cc: (opcional)
    Asunto: ...

    Cuerpo…
