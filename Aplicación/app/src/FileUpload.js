import React, { useState, useEffect } from 'react';
import { storage } from './services/firebase';
import { storageBucket } from './services/bucket';
import DOMPurify from 'dompurify';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [contenidoArchivo, setContenidoArchivo] = useState('bienvenido');
  const [htmlContent, setHtmlContent] = useState('');
  const [iframeUrl, setIframeUrl] = useState('');

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setFile(file);
  };

  function cambiarExtensionWavATxt(nombreArchivo) {
    // Verificar que la cadena termine con ".wav" y cambiarla a ".txt"
    if (nombreArchivo.endsWith('.wav')) {
      return nombreArchivo.slice(0, -4) + '.txt';  // Elimina ".wav" y agrega ".txt"
    }
    return nombreArchivo;  // Si no termina con ".wav", devuelve el nombre tal cual
  }

  function cambiarExtensionWavAHtml(nombreArchivo) {
    // Verificar que la cadena termine con ".wav" y cambiarla a ".txt"
    if (nombreArchivo.endsWith('.wav')) {
      return nombreArchivo.slice(0, -4) + '.html';  // Elimina ".wav" y agrega ".txt"
    }
    return nombreArchivo;  // Si no termina con ".wav", devuelve el nombre tal cual
  }

  async function leerArchivo(nombreArchivo) {
    const storageRef = storage.ref();
    const archivoRef = storageRef.child(`${nombreArchivo}`); // Asumiendo que está en la carpeta 'files'

    try {
      const url = await archivoRef.getDownloadURL(); // Obtener la URL de descarga del archivo
      const response = await fetch(url);
      console.log(response)
      const contenidoTexto = await response.text(); // Leer el contenido como texto
      console.log("resultado0")
      console.log(contenidoTexto)
      return contenidoTexto;  // Devolver el contenido del archivo
    } catch (error) {
      console.error('Error al leer el archivo:', error.code);
      return error.code; // Lanza el error para que se pueda manejar
    }
  }

  async function returnUrlrArchivo(nombreArchivo) {
    const storageRef = storage.ref();
    const archivoRef = storageRef.child(`${nombreArchivo}`); // Asumiendo que está en la carpeta 'files'

    try {
      const url = await archivoRef.getDownloadURL(); // Obtener la URL de descarga del archivo
      console.log(url)
      return url;  // Devolver el contenido del archivo
    } catch (error) {
      console.error('Error al leer el archivo:', error.code);
      return error.code; // Lanza el error para que se pueda manejar
    }
  }

  const renderSentimiento = (sentimiento) => {
    let emoticon = "";
    let clase = "";

    // Asignar el emoticono y la clase según el sentimiento
    if (sentimiento === "Positivo") {
      emoticon = "😊"; // Emoji de feliz
      clase = "positivo";
    } else if (sentimiento === "Negativo") {
      emoticon = "😞"; // Emoji de triste
      clase = "negativo";
    } else if (sentimiento === "Neutro") {
      emoticon = "😐"; // Emoji de serio (Neutro)
      clase = "";
    } else {
      // Si el sentimiento no es ninguno de los tres, retornar null (no mostrar nada)
      return null;
    }

    // Devolver el párrafo con el emoticono y la clase apropiada
    return emoticon;
  }

  const handleUpload = async () => {
    let textContent = ""
    if (file) {
      const storageRef = storage.ref(`files/${file.name}`);
      const uploadTask = storageRef.put(file);


      await uploadTask.on(
        'state_changed',
        (snapshot) => {
          // Puedes mostrar el progreso de la subida aquí si quieres
        },
        (error) => {
          console.log(error);
        },
        () => {
          // El archivo ha sido subido
          uploadTask.snapshot.ref.getDownloadURL().then((downloadURL) => {
            console.log('File available at', downloadURL);
          });
        }
      );

      while (true) {
        textContent = await leerArchivo(cambiarExtensionWavATxt(file.name))
        setHtmlContent(await leerArchivo(cambiarExtensionWavAHtml(file.name)))
        setIframeUrl(await returnUrlrArchivo(cambiarExtensionWavAHtml(file.name)))
        console.log("resultado")
        console.log(textContent)
        if (textContent !== "storage/object-not-found") {
          setContenidoArchivo(textContent)
          break;
        } else {
          setContenidoArchivo("cargando")
          await new Promise((resolve) => setTimeout(resolve, 30000));
        }

      }
      setContenidoArchivo(textContent)

    }

  };
  useEffect(() => {
    console.log("renderizo")
  }, [contenidoArchivo]);

  useEffect(() => {
    console.log("renderizo")
    //setHtmlContent("data");
    /*fetch('/0c004255-cef5-479d-9be5-5f688c91499a_20230826T15_53_UTC.html')
    .then((response) => response.text())
    .then((data) => {
      console.log("sanitizedHtml")
      console.log(data)
      setHtmlContent(data);
    })
    .catch((error) => console.error('Error loading HTML:', error));
    */
  }, []);

  return (
    <div>
      <div className="contenedor">
        <h1 className="titulo">Análisis Emocional Llamadas</h1>
        <div className="contenedor-botones">
          <input className="boton" type="file" onChange={handleFileChange} />
          <button className="boton" onClick={handleUpload}>Subir Archivo</button>
        </div>
        <div className={`descripcion ${contenidoArchivo === "Positivo" ? "positivo" : contenidoArchivo === "Negativo" ? "negativo" : ""}`}>
          {contenidoArchivo}
        </div>
        <div className="emoticono">{renderSentimiento(contenidoArchivo)}</div>
        <div>
        {htmlContent ? (
          <div className="contenedor-botones">
          <a href={iframeUrl} target="_blank" rel="noopener noreferrer">
            <button className="boton">Mas detalles del resultado</button>
          </a>
        </div>
        ) : (
          <p></p>
        )}
      </div>
        
      </div>
      

    </div>
  );
};

/*
<div>
        {htmlContent ? (
          <div
            dangerouslySetInnerHTML={{
              __html: htmlContent,
            }}
          />
        ) : (
          <p>No se ha cargado el contenido HTML.</p>
        )}
      </div>
        <iframe
          src={iframeUrl}
          width="100%"
          height="600px"
          title="HTML desde Firebase"
          style={{ border: 'none' }}
        ></iframe>
        */
export default FileUpload;
