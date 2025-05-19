import streamlit as st
import pandas as pd
import os
from PIL import Image
import qrcode
from io import BytesIO
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="BUMANDINO", layout="centered")
CORREOS_ADMIN = ["valejuana907@gmail.com"]
DB_FILE = "usuarios.csv"
REGISTRO_FILE = "registros_nuevos.csv"

# --- CARGAR BASES DE DATOS ---
if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=['id', 'nombre', 'correo', 'carrera', 'puntos'])
    df_init.to_csv(DB_FILE, index=False)

if not os.path.exists(REGISTRO_FILE):
    df_reg = pd.DataFrame(columns=['fecha', 'hora', 'nombre', 'correo', 'carrera'])
    df_reg.to_csv(REGISTRO_FILE, index=False)

usuarios = pd.read_csv(DB_FILE)

# --- MOSTRAR IMAGEN ---
try:
    image = Image.open("bienvenida.png")
    st.image(image, use_container_width=True)
except:
    st.warning("Imagen de bienvenida no encontrada.")

st.title("🎉 Programa de Recompensas BUMANDINO")

# --- VER PUNTOS DESDE QR ---
query_params = st.query_params
if 'id' in query_params:
    try:
        user_id = int(query_params['id'][0])
        usuario = usuarios[usuarios['id'] == user_id]
        if not usuario.empty:
            st.subheader(f"👋 ¡Hola, {usuario.iloc[0]['nombre']}!")
            st.success(f"Tienes **{usuario.iloc[0]['puntos']} puntos** 🎁")
            st.stop()
        else:
            st.error("❌ Usuario no encontrado.")
            st.stop()
    except:
        st.error("❌ ID inválido.")
        st.stop()

# --- FUNCIÓN PARA GENERAR QR ---
def generar_qr(texto):
    qr = qrcode.make(texto)
    buf = BytesIO()
    qr.save(buf)
    buf.seek(0)
    return buf

# --- REGISTRO DE USUARIOS ---
st.subheader("📝 Regístrate")
with st.form("registro_form"):
    nombre = st.text_input("Nombre completo")
    correo = st.text_input("Correo")
    carrera = st.selectbox("Carrera", ["Ingeniería", "Administración", "Diseño", "Psicología", "Economía", "Derecho", "Medicina", "Otra"])
    submit = st.form_submit_button("Registrar")

    if submit:
        if nombre and correo:
            if correo not in usuarios['correo'].values:
                nuevo_id = usuarios['id'].max() + 1 if not usuarios.empty else 1
                nuevo_usuario = {
                    'id': nuevo_id,
                    'nombre': nombre,
                    'correo': correo,
                    'carrera': carrera,
                    'puntos': 0
                }
                usuarios = pd.concat([usuarios, pd.DataFrame([nuevo_usuario])], ignore_index=True)
                usuarios.to_csv(DB_FILE, index=False)

                # Guardar en archivo privado
                now = datetime.now()
                nuevo_registro = {
                    'fecha': now.strftime("%Y-%m-%d"),
                    'hora': now.strftime("%H:%M:%S"),
                    'nombre': nombre,
                    'correo': correo,
                    'carrera': carrera
                }
                df_reg = pd.read_csv(REGISTRO_FILE)
                df_reg = pd.concat([df_reg, pd.DataFrame([nuevo_registro])], ignore_index=True)
                df_reg.to_csv(REGISTRO_FILE, index=False)

                st.success(f"¡Registro exitoso! Bienvenido/a, {nombre} 🎉")

                url = f"https://valencr17-pythonbumandino-app.streamlit.app/?id={nuevo_id}"
                qr_img = generar_qr(url)
                st.image(qr_img, caption="Escanea este QR para ver tus puntos", width=200)
            else:
                st.error("Este correo ya está registrado.")
        else:
            st.error("Por favor completa nombre y correo.")

# --- CONSULTAR PUNTOS POR CORREO ---
st.subheader("🔎 Consultar tus puntos")
with st.form("consulta_form"):
    correo_consulta = st.text_input("Ingresa tu correo")
    btn_buscar = st.form_submit_button("Buscar")

    if btn_buscar:
        user = usuarios[usuarios['correo'] == correo_consulta]
        if not user.empty:
            st.success(f"{user.iloc[0]['nombre']}, tienes {user.iloc[0]['puntos']} puntos 🎉")
        else:
            st.error("❌ No encontramos ese correo. ¿Ya te registraste?")

# --- PANEL ADMIN PRIVADO ---
st.subheader("🔐 Acceso administrador")
correo_login = st.text_input("Solo administradores: ingresa tu correo")

if correo_login in CORREOS_ADMIN:
    st.success("✅ Panel de administración activado")

    with st.form("form_asignar"):
        correo_admin = st.text_input("Correo del usuario al que deseas asignar puntos")
        puntos_nuevos = st.number_input("Puntos a agregar", min_value=1, step=1)
        enviar = st.form_submit_button("Asignar")

        if enviar:
            if correo_admin in usuarios['correo'].values:
                usuarios.loc[usuarios['correo'] == correo_admin, 'puntos'] += puntos_nuevos
                usuarios.to_csv(DB_FILE, index=False)
                st.success(f"🎯 ¡Asignaste {puntos_nuevos} puntos a {correo_admin}!")
            else:
                st.error("❌ Correo no encontrado.")

    # Descargar base de datos
    st.download_button(
        label="⬇️ Descargar base general (usuarios.csv)",
        data=usuarios.to_csv(index=False).encode('utf-8'),
        file_name='usuarios.csv',
        mime='text/csv'
    )

    st.download_button(
        label="⬇️ Descargar nuevos registros (registros_nuevos.csv)",
        data=pd.read_csv(REGISTRO_FILE).to_csv(index=False).encode('utf-8'),
        file_name='registros_nuevos.csv',
        mime='text/csv'
    )
else:
    st.info("🔒 Este panel es privado.")


