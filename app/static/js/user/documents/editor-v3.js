(() => {
  function extractDocumentParts(html) {
      let parser = new DOMParser();
      let documentObject = parser.parseFromString(html, "text/html");

      return {
          bodyHtml: documentObject.body.innerHTML,
          css: Array.from(documentObject.querySelectorAll("style"))
              .map(function(style) {
                  return style.textContent;
              })
              .join("\n")
      };

  }

  let cvDocument = extractDocumentParts(doc);

  tinymce.init({
      selector: "#editor",
      inline: false,
      height: 900,
      menubar: true,
      resize: true,
      
      menu: {
        view: {
          title: 'View',
          items: 'visualaid'
        },
        tools: {
          title: 'Tools',
          items: 'wordcount'
        }
      },

      plugins: [
              "lists",
              "link",
              "table",
              "searchreplace",
              "code",
              "fullscreen",
              "wordcount"
      ],

      toolbar:
              "mysave undo redo | " +
              "blocks fontfamily fontsize | " +
              "bold italic underline forecolor | " +
              "alignleft aligncenter alignright alignjustify | " +
              "bullist numlist outdent indent | " +
              "link table | " +
              "removeformat | " +
              "searchreplace | " +
              "download ",

      content_style:
          cvDocument.css +
          `
          body {
              width: 210mm;
              min-height: 297mm;
              margin: 0 auto;
              padding: 16mm 18mm;
              box-sizing: border-box;
              background: white;
          }
          `,

      setup: function(editor) {
          editor.on("init", function() {
              editor.setContent(cvDocument.bodyHtml);
          });
                     
                  
          editor.ui.registry.addButton('mysave', {
            text: 'Save',
            tooltip: 'Save document',
            onAction: () => {
              saveDocument()
            }
          })

          editor.ui.registry.addButton('download', {
            icon: 'save',
            tooltip: 'Downlaod DOCX',
            onAction: () => {
              download()
            }
          })
          
          editor.addShortcut("ctrl+s", "Save document", function () {
            saveDocument()
          })

      }
  });

  const finalHtml = () => {
    let editor = tinymce.get("editor");

    return `
      <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">

            <style>
              ${cvDocument.css}
            </style>
          </head>

          <body>
            ${editor.getContent()}
          </body>

        </html>
    `
  }

  const saveDocument = () => {
      if (!editor) {
          console.error("Editor is not initialized.");
          return;
      }

      let fHtml = finalHtml();

      // Send finalHtml to Backend
      const doc_data = {
        doc_id: doc_id, 
        doc_content: fHtml
      }

      axios.post(BackendUrl, doc_data)
            .then(function (response) {
              console.log(response.status)
              
              if (response.data.success) {
                const status = document.getElementById("save-status");
                status.classList.add("show");
                clearTimeout(status.timer);
                status.timer = setTimeout(() => {
                    status.classList.remove("show");
                }, 2500);
              }

              if (response.data.error) {
                const message = document.getElementById("document-error");
                message.classList.add("show");
                clearTimeout(message.timer);
                message.timer = setTimeout(() => {
                    message.classList.remove("show");
                }, 3000);     
              }
              
            })
            .catch(function (error) {
              console.error(error.message)
            })
  };

  const download = () => {
      const HTML = finalHtml();

      const blob = new Blob(["\ufeff", HTML], {
          type: "application/msword;charset=utf-8"
      });

      const downloadURL = URL.createObjectURL(blob);
      const downloadLink = document.createElement("a");

      downloadLink.href = downloadURL;
      downloadLink.download = `${doc_title} CV.doc`;

      downloadLink.click();

      URL.revokeObjectURL(downloadURL);
  }

})();
